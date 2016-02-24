""" Standalone webinterface for Openstack Swift. """
# -*- coding: utf-8 -*-
#pylint:disable=E1101
from swiftclient import client

from django.shortcuts import render_to_response, redirect
from django.template import RequestContext
from django.contrib import messages
from django.conf import settings
from django.http import JsonResponse
from django.utils.translation import ugettext as _

from swiftbrowser.forms import CreateContainerForm, UpdateACLForm
from swiftbrowser.utils import *
from swiftbrowser.utils import _get_total_objects


@session_valid
def containerview(request):
    """ Returns a list of all containers in current account. """

    storage_url = request.session.get('storage_url', '')
    auth_token = request.session.get('auth_token', '')

    try:
        account_stat, containers = client.get_account(storage_url, auth_token)
    except client.ClientException:
        return redirect(swiftbrowser.views.main.login)

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
            client.get_container(
                storage_url, auth_token, container,
                headers={"X-Forwarded-For": request.META.get('REMOTE_ADDR')})
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
        _m, objects = client.get_container(
            storage_url, auth_token, container,
            headers={"X-Forwarded-For": request.META.get('REMOTE_ADDR')})
        for obj in objects:
            client.delete_object(
                storage_url, auth_token, container, obj['name'],
                headers={"X-Forwarded-For": request.META.get('REMOTE_ADDR')})
        client.delete_container(storage_url, auth_token, container,)
    except client.ClientException:
        return HttpResponse(e, status=500)

    return JsonResponse({
        'success': True,
    })


@session_valid
def delete_container_form(request, container):
    """ Display delete container modal """

    return render_to_response(
        'delete_container.html',
        {
            'container': container,
            'total_objects': _get_total_objects(request, container, "")
        },
        context_instance=RequestContext(request))


@ajax_session_valid
def get_acls(request, container):
    """ Read and return the Read and Write ACL of the given container. """

    storage_url = request.session.get('storage_url', '')
    auth_token = request.session.get('auth_token', '')

    cont = client.head_container(storage_url, auth_token, container)
    readers = split_acl(cont.get('x-container-read', ''))
    writers = split_acl(cont.get('x-container-write', ''))

    return JsonResponse({
        "read_acl": readers,
        "write_acl": writers,
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
