""" Standalone webinterface for Openstack Swift. """
# -*- coding: utf-8 -*-
#pylint:disable=E1101
from swiftclient import client

from django.shortcuts import render_to_response, redirect
from django.template import RequestContext
from django.contrib import messages
from django.utils.translation import ugettext as _
from swiftbrowser.utils import *


def limited_users_login(request):
    """ Get and parse the list of containers the user has access to. """

    storage_url = request.session.get('storage_url', '')
    auth_token = request.session.get('auth_token', '')
    user = request.session.get('user', '')

    # Get list of containers the user has access to in
    # "X-Container-Meta-container-list" of the container that matches the
    # user's username.
    try:
        meta = client.head_container(storage_url, auth_token, user)
    except client.ClientException:

        # The user may belong to more than one tenant and so the user's
        # container my be in another tenant. Switch to the next tenant
        # in the tenant list.
        for i, tenant in enumerate(request.session["tenants"]):
            if tenant == request.session["tenant_name"]:
                if i + 1 <= len(request.session["tenants"]):
                    return redirect(
                        swiftbrowser.views.main.switch_tenant,
                        request.session["tenants"][i + 1], True)
                else:
                    # We've tried all the tenants, no container exists
                    messages.add_message(
                        request, messages.ERROR,
                        _("Unable to find container {0} in any tenant."
                            .format(user)))
                    break

        return redirect(swiftbrowser.views.main.login)

    # List of containers
    if not "x-container-meta-container-list" in meta:
        # User does not have access to any container but it's own
        containers = request.session["tenant_name"] + ":" + user
    else:
        containers = meta["x-container-meta-container-list"]

    # Save the mapping of tenants and containers the user has access to.
    if not request.session.get('container_mapping', ''):
        request.session['container_mapping'] = get_tenant_container_mapping(
            containers)

    return redirect(limited_users_containerview)


@session_valid
def limited_users_containerview(request):
    """ Display the containers the user has access to within the current
    tenant."""

    storage_url = request.session.get('storage_url', '')
    auth_token = request.session.get('auth_token', '')

    container_list = []
    keys = {}

    container_mapping = request.session.get('container_mapping', '')

    if not container_mapping:
        messages.add_message(
            request, messages.ERROR, _("No container mapping."))
        return redirect(swiftbrowser.views.main.login)

    # Get keys for all the containers
    for container_name in container_mapping[request.session["tenant_name"]]:

        # Make sure user has access to the container
        try:
            meta = client.head_container(
                storage_url, auth_token, container_name)

        except client.ClientException:
            messages.add_message(
                request, messages.ERROR,
                _("Failed to head container {0}.".format(container_name)))
            return redirect(swiftbrowser.views.main.login)

        container_list.append({"name": container_name})
        keys[container_name] = meta.get('x-container-meta-temp-url-key', '')

    # Store the keys for later use
    request.session["keys"] = keys

    return render_to_response('limited_containerview.html', {
        'containers': container_list,
        'session': request.session,
    }, context_instance=RequestContext(request))
