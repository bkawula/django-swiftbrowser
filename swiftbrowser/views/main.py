""" Standalone webinterface for Openstack Swift. """
# -*- coding: utf-8 -*-
#pylint:disable=E1101
import os
import logging
from swiftclient import client

from django.shortcuts import render_to_response, redirect
from django.template import RequestContext
from django.contrib import messages
from django.conf import settings
from django.http import JsonResponse
from django.views.decorators.http import require_POST
from django.utils.translation import ugettext as _
from jfu.http import JFUResponse
from swiftbrowser.models import Photo
from swiftbrowser.forms import PseudoFolderForm, LoginForm, TimeForm
from swiftbrowser.utils import *
from swiftbrowser.views.containers import containerview
from swiftbrowser.views.objects import objectview

from openstack_auth.utils import get_session
import keystoneauth1.identity
from keystoneclient.v2_0 import client as v2_client


logger = logging.getLogger(__name__)


def login(request):
    """ Tries to login user and sets session data """
    request.session.flush()

    #Process the form if there is a POST request.
    if (request.POST):
        form = LoginForm(request.POST)
        if form.is_valid():
            user = form.cleaned_data['username']
            password = form.cleaned_data['password']
            try:

                tenant_specified = user.find(":") > 0
                if tenant_specified:
                    # The user has specifed the tenant they want to login to
                    tenant_name, user = split_tenant_user_names(user)

                # Authenticate with keystone
                unscoped_auth = keystoneauth1.identity.v2.Password(
                    auth_url=settings.SWIFT_AUTH_URL,
                    username=user,
                    password=password)
                unscoped_auth_ref = unscoped_auth.get_access(get_session())
                keystone_token = unscoped_auth_ref.auth_token
                keystoneclient = v2_client.Client(
                    token=keystone_token,
                    endpoint="https://olrcdev.scholarsportal.info:5000/v2.0/")
                tenant_manager = keystoneclient.tenants
                projects = tenant_manager.list()

                # Save tenants the user is part of.
                request.session["tenants"] = \
                    [project.name for project in projects]

                # When the user does not specify a tenant on login, use the
                # first tenant as a default.
                if not tenant_specified:
                    tenant_name = request.session["tenants"][0]

                # Authenticate with swift
                username = tenant_name + ":" + user
                auth_version = settings.SWIFT_AUTH_VERSION or 1
                (storage_url, auth_token) = client.get_auth(
                    settings.SWIFT_AUTH_URL, username, password,
                    auth_version=auth_version)

                request.session['auth_token'] = auth_token
                request.session['storage_url'] = storage_url
                request.session['password'] = password
                request.session['user'] = user
                request.session['username'] = username
                request.session['tenant_name'] = tenant_name

                # Upon successful retrieval of a token, if we're unable to
                # head the account, then the user is not an admin or
                # swiftoperator and has access to only a container.

                try:
                    client.head_account(storage_url, auth_token)
                except:
                    request.session['norole'] = True

                return redirect(containerview)

            # Swift authentication error.
            except client.ClientException, e:
                messages.error(request, _("Login failed: {0}".format(e)))

            # Other error.
            except Exception, e:
                messages.error(request, _("Login failed: {0}").format(e))

        # Login failure on invalid forms.
        else:
            messages.error(request, _("Login failed."))
    else:
        form = LoginForm(None)
        user = ""

    return render_to_response(
        'login.html',
        {'form': form,
        'username': user},
        context_instance=RequestContext(request)
    )


@session_valid
def toggle_public(request, container):
    """ Sets/unsets '.r:*,.rlistings' container read ACL """

    storage_url = request.session.get('storage_url', '')
    auth_token = request.session.get('auth_token', '')

    try:
        meta = client.head_container(storage_url, auth_token, container)
    except client.ClientException:
        messages.add_message(request, messages.ERROR, _("Access denied."))
        return redirect(containerview)

    read_acl = meta.get('x-container-read', '')
    if '.rlistings' and '.r:*' in read_acl:
        read_acl = read_acl.replace('.r:*', '')
        read_acl = read_acl.replace('.rlistings', '')
        read_acl = read_acl.replace(',,', ',')
    else:
        read_acl += '.r:*,.rlistings'
    headers = {'X-Container-Read': read_acl, }

    try:
        client.post_container(storage_url, auth_token, container, headers)
    except client.ClientException:
        messages.add_message(request, messages.ERROR, _("Access denied."))

    return redirect(objectview, container=container)


@session_valid
def create_pseudofolder(request, container, prefix=None):
    """ Creates a pseudofolder (empty object of type application/directory) """
    storage_url = request.session.get('storage_url', '')
    auth_token = request.session.get('auth_token', '')

    form = PseudoFolderForm(request.POST)
    if form.is_valid():
        foldername = request.POST.get('foldername', None)
        if prefix:
            foldername = prefix + '/' + foldername
        foldername = os.path.normpath(foldername)
        foldername = foldername.strip('/')
        foldername += '/'

        content_type = 'application/directory'
        obj = None

        try:
            client.put_object(storage_url, auth_token,
                              container, foldername, obj,
                              content_type=content_type)
            messages.add_message(
                request,
                messages.SUCCESS,
                _(
                    "The folder " +
                    request.POST.get('foldername', None) + " was created.")
            )

        except client.ClientException:
            messages.add_message(request, messages.ERROR, _("Access denied."))

    return JsonResponse({})


@session_valid
@require_POST
def upload_delete(request, pk):
    success = True
    try:
        instance = Photo.objects.get(pk=pk)
        os.unlink(instance.file.path)
        instance.delete()
    except Photo.DoesNotExist:
        success = False

    return JFUResponse(request, success)


@session_valid
def settings_view(request):
    """ Returns list of all objects in current container. """

    storage_url = request.session.get('storage_url', '')
    auth_token = request.session.get('auth_token', '')

    # If temp url is set, display it, else, inform user the default is 7 days.
    default_temp_time = get_default_temp_time(storage_url, auth_token)
    if not default_temp_time:
        default_temp_time = 604800  # 7 days in seconds

    days_to_expiry = int(default_temp_time) / (24 * 3600)
    hours_to_expiry = (int(default_temp_time) % (24 * 3600)) / 3600

    tempurl_form = TimeForm(
        initial={
            'days': days_to_expiry,
            'hours': hours_to_expiry,
        }
    )

    return render_to_response(
        "settings.html",
        {
            'session': request.session,
            'tempurl_form': tempurl_form,
        },
        context_instance=RequestContext(request)
    )


def get_version(request):
    return render_to_response('version.html',
                              context_instance=RequestContext(request))


@session_valid
def switch_tenant(request, tenant):
    """ Switch the user to another tenant. Authenticate under the new tenant
    and redirect to the container view. """

    user = request.session.get('user', '')
    password = request.session.get('password', '')
    username = tenant + ":" + user
    auth_version = settings.SWIFT_AUTH_VERSION or 1
    (storage_url, auth_token) = client.get_auth(
        settings.SWIFT_AUTH_URL, username, password,
        auth_version=auth_version)

    request.session['auth_token'] = auth_token
    request.session['storage_url'] = storage_url
    request.session['tenant_name'] = tenant

    return redirect(containerview)
