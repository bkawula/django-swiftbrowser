from django.contrib import messages
from django.http import JsonResponse

from swiftclient import client
from swiftbrowser.utils import ajax_session_valid, get_base_url, prefix_list, \
    pseudofolder_object_list


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
