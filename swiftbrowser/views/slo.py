import os

from django.http import JsonResponse, HttpResponse

from swiftclient import client
from swiftbrowser.forms import StartSloForm
from swiftbrowser.utils import pseudofolder_object_list, \
    get_first_nonconsecutive, calculate_segment_size


def get_segment_number(file_name, request, container, prefix=None):
    '''Return the segment number a given file should create next. If it is 0,
    create a pseudo folder for the file. The folder is created if it doesn't
    exist. '''

    if prefix:
        foldername = prefix + '/' + file_name + '_segments'
    else:
        foldername = file_name + '_segments'

    storage_url = request.session.get('storage_url', '')
    auth_token = request.session.get('auth_token', '')

    foldername = os.path.normpath(foldername)
    foldername = foldername.strip('/')
    foldername += '/'

    content_type = 'application/directory'
    obj = None

    try:
        client.put_object(storage_url, auth_token,
                          container, foldername, obj,
                          content_type=content_type)

        meta, objects = client.get_container(storage_url, auth_token,
                                             container, delimiter='/',
                                             prefix=foldername)

        pseudofolders, objs = pseudofolder_object_list(objects, prefix)

        return get_first_nonconsecutive(objs)

    except client.ClientException:
        messages.add_message(
            request, messages.ERROR, _("Access denied."))

    return 0


def initialize_slo(request, container, prefix=None):
    '''Initiate a slo upload.
    Return the segment number the upload should start at.
    Return the size of the segments.
    '''
    if (request.POST):
        form = StartSloForm(request.POST)
        if form.is_valid():

            file_name = form.cleaned_data["file_name"]
            file_size = float(form.cleaned_data["file_size"])

            response = {
                "next_segment": get_segment_number(file_name, request,
                                                   container, prefix),
                "segment_size": calculate_segment_size(file_size),
            }

            return JsonResponse(response)

    return HttpResponse("invalid form", status=500)
