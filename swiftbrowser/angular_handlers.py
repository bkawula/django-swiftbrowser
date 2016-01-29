import string
import random
from django.conf import settings
from django.contrib import messages
from django.http import JsonResponse, HttpResponse
from django.shortcuts import redirect

from swiftclient import client
from swiftbrowser.utils import ajax_session_valid, get_base_url, prefix_list, \
    pseudofolder_object_list, split_tenant_user_names
from swiftbrowser.views import containerview
from swiftbrowser.angular_utils import *
from swiftbrowser.forms import CreateUserForm, DeleteUserForm, UpdateACLForm
import keystoneclient.v2_0.client


@ajax_session_valid
def get_users(request):
    """ Returns json object of all tenants in the current  """

    username = request.session.get('username', '')
    tenant_name, user = split_tenant_user_names(username)
    password = request.session.get('password', '')

    try:
        keystone_client = keystoneclient.v2_0.client.Client(
            username=user, password=password, tenant_name=tenant_name,
            auth_url=settings.SWIFT_AUTH_URL)

        keystone_usermanager = keystone_client.users

    except Exception, e:
        print(e)
        return redirect(containerview)

    # Get tenant id from list of tenants
    for tenants in keystone_client.tenants.list():
        if tenants.name == tenant_name:
            tenant = tenants
            request.session['tenant_id'] = tenant.id
            break

    # Get users within the tenant
    try:
        user_objects = keystone_usermanager.list(tenant.id)
        users = keystone_users_to_list(user_objects)
    except Exception, e:
        return HttpResponse(e, status=500)

    return JsonResponse({'users': users})


@ajax_session_valid
def create_user(request):
    '''Create a user with the given form post information.'''

    # Check submission is valid
    form = CreateUserForm(request.POST)

    if (form.is_valid()):
        email = form.cleaned_data['email']
        password = form.cleaned_data['password']
    else:
        return JsonResponse({'error': 'invalid form'})

    # Get keystone object
    keystone_client = get_keystoneclient(request)

    tenant_id = request.session.get('tenant_id', '')
    tenant_name = request.session.get('tenant_name', '')

    try:
        #Create user. New users' usernames will be their email address.
        keystone_client.users.create(
            name=email, password=password, tenant_id=tenant_id)

    except Exception, e:
        return HttpResponse(e, status=500)

    # Create a container for that user with matching name.
    chars = string.ascii_lowercase + string.digits
    key = ''
    for x in range(32):
        key += random.choice(chars)

    headers = {
        'X-Container-Meta-Access-Control-Expose-Headers':
        'Access-Control-Allow-Origin',
        'X-Container-Meta-Access-Control-Allow-Origin': settings.BASE_URL,
        'X-Container-Read': tenant_name + ":" + email,
        'X-Container-Write': tenant_name + ":" + email,
        'X-Container-Meta-Temp-URL-Key': key
    }

    try:
        storage_url = request.session.get('storage_url', '')
        auth_token = request.session.get('auth_token', '')

        client.put_container(
            storage_url, auth_token, email, headers)

    except Exception, e:
        return HttpResponse(e, status=500)

    return JsonResponse({'success': 'User created'})


@ajax_session_valid
def delete_user(request):
    '''Create a user with the given form post information.'''

    form = DeleteUserForm(request.POST)
    if (form.is_valid()):
        user_id = form.cleaned_data['user_id']
    else:
        return JsonResponse({'error': 'invalid form'})

    keystone_client = get_keystoneclient(request)

    tenant_id = request.session.get('tenant_id', '')

    roles = keystone_client.users.list_roles(user_id, tenant_id)
    # Do not allow users to delete themselves
    for role in roles:
        if role.name == "admin":
            return JsonResponse({'error': 'You cannot delete admins.'})

    try:
        keystone_client.users.delete(user_id)

    except Exception, e:
        return HttpResponse(e, status=500)

    return JsonResponse({'success': 'User deleted'})
