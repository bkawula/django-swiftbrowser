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
    LoginForm, DocumentForm, TimeForm, UpdateACLForm
from swiftbrowser.utils import *

import swiftbrowser


@session_valid
def containerview(request):
    """ Returns a list of all containers in current account. """

    # Users with no role will not be able to list containers.
    if request.session.get('norole'):
        # Redirect them to the container that is their username.
        return redirect(objectview, request.session.get('user'))
    storage_url = request.session.get('storage_url', '')
    auth_token = request.session.get('auth_token', '')

    try:
        account_stat, containers = client.get_account(storage_url, auth_token)
    except client.ClientException:
        return redirect(login)

    account_stat = replace_hyphens(account_stat)

    account = storage_url.split('/')[-1]

    return render_to_response('containerview.html', {
        'account': account,
        'account_stat': account_stat,
        'containers': containers,
        'session': request.session,
    }, context_instance=RequestContext(request))


@session_valid
def create_container(request):
    """ Creates a container (empty object of type application/directory) """

    storage_url = request.session.get('storage_url', '')
    auth_token = request.session.get('auth_token', '')

    headers = {
        'X-Container-Meta-Access-Control-Expose-Headers':
        'Access-Control-Allow-Origin',
        'X-Container-Meta-Access-Control-Allow-Origin': settings.BASE_URL
    }

    form = CreateContainerForm(request.POST or None)
    if form.is_valid():
        container = form.cleaned_data['containername']

        #Check container does not already exist
        try:
            client.get_container(storage_url, auth_token, container)
            messages.add_message(
                request,
                messages.ERROR,
                _("Container {0} already exists.".format(container)))
        except:
            try:
                client.put_container(
                    storage_url, auth_token, container, headers)
                messages.add_message(request, messages.INFO,
                                     _("Container created."))
            except client.ClientException:
                messages.add_message(
                    request, messages.ERROR, _("Access denied."))

        return redirect(containerview)

    return render_to_response(
        'create_container.html',
        {'session': request.session},
        context_instance=RequestContext(request))


@session_valid
def delete_container(request, container):
    """ Deletes a container """

    storage_url = request.session.get('storage_url', '')
    auth_token = request.session.get('auth_token', '')

    try:
        _m, objects = client.get_container(storage_url, auth_token, container)
        for obj in objects:
            client.delete_object(storage_url, auth_token,
                                 container, obj['name'])
        client.delete_container(storage_url, auth_token, container)
        messages.add_message(request, messages.INFO, _("Container deleted."))
    except client.ClientException:
        messages.add_message(request, messages.ERROR, _("Access denied."))

    return redirect(containerview)


@ajax_session_valid
def get_acls(request, container):
    """ Read and return the Read and Write ACL of the given container. """

    storage_url = request.session.get('storage_url', '')
    auth_token = request.session.get('auth_token', '')

    cont = client.head_container(storage_url, auth_token, container)
    readers = cont.get('x-container-read', '')
    writers = cont.get('x-container-write', '')

    return JsonResponse({
        "read_acl": readers,
        "write_acl": writers
    })


@ajax_session_valid
def set_acls(request, container):
    """For the given container, set the ACLs. """

    form = UpdateACLForm(request.POST)

    if (form.is_valid()):
        read_acl = form.cleaned_data['read_acl']
        write_acl = form.cleaned_data['write_acl']
    else:
        return JsonResponse({'error': 'invalid form'})

    storage_url = request.session.get('storage_url', '')
    auth_token = request.session.get('auth_token', '')

    headers = {'X-Container-Read': read_acl,
               'X-Container-Write': write_acl}
    try:
        client.post_container(storage_url, auth_token,
                              container, headers)

        return JsonResponse({
            "success": "Successfully updated ACL.",
            "read_acl": read_acl,
            "write_acl": write_acl
        })
    except client.ClientException:
        return JsonResponse({'error': 'Error updating ACL.'})
