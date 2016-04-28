""" Utility functions for angular operations, particularly for user
management"""
from django.conf import settings
import keystoneclient.v2_0.client
from django.shortcuts import redirect
from swiftbrowser.utils import split_tenant_user_names
from swiftbrowser.views import settings_view


def keystone_users_to_list(user_list):
    '''Given a list of keystone user objects, return a dict representing
    the users.'''

    users = []

    for user in user_list:
        user_dict = {
            'username': user.username,
            'name': user.name,
            'email': user.email,
            'id': user.id,
            'enabled': user.enabled,
            'tenantId': user.tenantId,
        }
        users.append(user_dict)

    return users


def get_keystoneclient(request):
    ''' Given a request with the assumption the user is already authenticated,
    return a keystoneclient object.'''

    username = request.session.get('username', '')
    tenant_name, user = split_tenant_user_names(username)
    password = request.session.get('password', '')

    try:
        keystone_client = keystoneclient.v2_0.client.Client(
            username=user, password=password, tenant_name=tenant_name,
            auth_url=settings.SWIFT_AUTH_URL)

    except Exception, e:
        print(e)
        return redirect(settings_view)

    return keystone_client
