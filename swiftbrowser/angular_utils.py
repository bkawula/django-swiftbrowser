""" Utility functions for angular operations."""


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
