from django.conf import settings
from django.contrib import messages
from django.http import JsonResponse
from django.shortcuts import redirect

from swiftclient import client
from swiftbrowser.utils import ajax_session_valid, get_base_url, prefix_list, \
    pseudofolder_object_list, split_tenant_user_names
from swiftbrowser.views import containerview
from swiftbrowser.angular_utils import *
from swiftbrowser.forms import CreateUserForm
import keystoneclient.v2_0.client


@ajax_session_valid
def get_object_table(request):
    """ Returns json object of all objects in current container. """

    storage_url = request.session.get('storage_url', '')
    auth_token = request.session.get('auth_token', '')
    container = request.session.get('container')
    prefix = request.session.get('prefix')

    try:
        meta, objects = client.get_container(
            storage_url,
            auth_token,
            container,
            delimiter='/',
            prefix=prefix)

    except client.ClientException:
        messages.add_message(request, messages.ERROR, _("Access denied."))
        return redirect(containerview)

    prefixes = prefix_list(prefix)
    pseudofolders, objs = pseudofolder_object_list(objects, prefix)
    base_url = get_base_url(request)
    account = storage_url.split('/')[-1]

    return JsonResponse({
        'container': container,
        'objects': objs,
        'folders': pseudofolders,
        'folder_prefix': prefix
    })


@ajax_session_valid
def get_users(request):
    """ Returns json object of all tenants in the current  """

    username = request.session.get('username', '')
    tenant_name, user = split_tenant_user_names(username)
    password = request.session.get('password', '')

    try:
        keystone_client = keystoneclient.v2_0.client.Client(
            username=user, password=password, tenant_name=tenant_name,
            auth_url=settings.SWAUTH_URL)

        keystone_usermanager = keystone_client.users

    except Exception, e:
        print(e)
        return redirect(containerview)

    # Get tenant id from list of tenants
    for tenants in keystone_client.tenants.list():
        if tenants.name == tenant_name:
            tenant = tenants

    # Get users within the tenant
    try:
        user_objects = keystone_usermanager.list(tenant.id)
        users = keystone_users_to_list(user_objects)
    except Exception, e:
        print(e)

    return JsonResponse({'users': users})


@ajax_session_valid
def create_user(request):
    '''Create a user with the given form post information.'''

    username = request.session.get('username', '')
    tenant_name, user = split_tenant_user_names(username)
    password = request.session.get('password', '')

    try:
        keystone_client = keystoneclient.v2_0.client.Client(
            username=user, password=password, tenant_name=tenant_name,
            auth_url=settings.SWAUTH_URL)

        keystone_usermanager = keystone_client.users
    except Exception, e:
        print(e)
        return redirect(containerview)

    # Get tenant id from list of tenants
    for tenants in keystone_client.tenants.list():
        if tenants.name == tenant_name:
            tenant = tenants

    form = CreateUserForm(request.POST)
    if (form.is_valid()):
        email = form.cleaned_data['email']
        password = form.cleaned_data['password']
    else:
        return JsonResponse({'error': 'invalid form'})

    #Create user
    try:
        response = keystone_usermanager.create(
            name=email,
            password=password,
            tenant_id=tenant.id,
        )
    except Exception, e:
        return JsonReponse({
            'error': e
        })

    return JsonResponse({'success': 'User created'})
