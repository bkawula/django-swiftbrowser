""" Standalone webinterface for Openstack Swift. """
# -*- coding: utf-8 -*-
#pylint:disable=E1101
import os
import time
import urlparse
import hmac
import re
from hashlib import sha1
import logging
import zipfile
import json
from StringIO import StringIO
from swiftclient import client

from django.shortcuts import render_to_response, redirect, render
from django.template import RequestContext
from django.contrib import messages
from django.contrib.messages import get_messages
from django.conf import settings
from django.http import HttpResponseRedirect
from django.http import HttpResponse, HttpResponseServerError, \
    HttpResponseForbidden
from django.http import JsonResponse
from django.views import generic
from django.views.decorators.http import require_POST
from django.utils.translation import ugettext as _
from django.core.urlresolvers import reverse
from jfu.http import upload_receive, UploadResponse, JFUResponse
from swiftbrowser.models import Photo
from swiftbrowser.models import Document
from swiftbrowser.forms import CreateContainerForm, PseudoFolderForm, \
    LoginForm, DocumentForm, TimeForm
from swiftbrowser.utils import *
from swiftbrowser.views.containers import containerview
from swiftbrowser.views.objects import objectview

import swiftbrowser

logger = logging.getLogger(__name__)


def login(request):
    """ Tries to login user and sets session data """
    request.session.flush()

    #Process the form if there is a POST request.
    if (request.POST):
        form = LoginForm(request.POST)
        if form.is_valid():
            username = form.cleaned_data['username']
            password = form.cleaned_data['password']
            try:
                auth_version = settings.SWIFT_AUTH_VERSION or 1
                (storage_url, auth_token) = client.get_auth(
                    settings.SWIFT_AUTH_URL, username, password,
                    auth_version=auth_version)
                request.session['auth_token'] = auth_token
                request.session['storage_url'] = storage_url
                request.session['username'] = username
                request.session['password'] = password

                tenant_name, user = split_tenant_user_names(username)
                request.session['user'] = user
                request.session['tenant_name'] = tenant_name

                # Upon successful retrieval of a token, if we're unable to
                # head the account, then the user is not an admin or
                # swiftoperator and has access to only a container.
                try:
                    client.head_account(storage_url, auth_token)
                except:
                    request.session['norole'] = True

                return redirect(containerview)

            # Specify why the login failed.
            except client.ClientException, e:
                messages.error(request, _("Login failed: {0}".format(
                    e)))

            # Generic login failure message.
            except Exception, e:
                print(e)
                messages.error(request, _("Login failed."))
        # Generic login failure on invalid forms.
        else:
            messages.error(request, _("Login failed."))
    else:
        form = LoginForm(None)

    return render_to_response(
        'login.html',
        {'form': form},
        context_instance=RequestContext(request)
    )


@session_valid
def delete_folder(request, container, objectname):
    """ Deletes a pseudo folder. """

    try:
        delete_given_folder(request, container, objectname)
        messages.add_message(request, messages.INFO, _("Folder deleted."))
    except client.ClientException:
        messages.add_message(request, messages.ERROR, _("Access denied."))
        return redirect(objectview, container=container)
    if objectname[-1] == '/':  # deleting a pseudofolder, move one level up
        objectname = objectname[:-1]
    prefix = '/'.join(objectname.split('/')[:-1])
    if prefix:
        prefix += '/'
    return redirect(objectview, container=container, prefix=prefix)


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
