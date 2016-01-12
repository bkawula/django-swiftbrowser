import os
import json
from tempfile import TemporaryFile, NamedTemporaryFile

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

    client.put_object(storage_url, auth_token, container, foldername, obj,
                      content_type=content_type)

    meta, objects = client.get_container(storage_url, auth_token, container,
                                         delimiter='/', prefix=foldername)

    pseudofolders, objs = pseudofolder_object_list(objects, prefix)

    return get_first_nonconsecutive(objs)


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

            try:
                segment_number = get_segment_number(file_name, request,
                                                    container, prefix)
            except client.ClientException, e:

                return HttpResponse(e, status=500)

            response = {
                "next_segment": segment_number,
                "segment_size": calculate_segment_size(file_size),
            }

            return JsonResponse(response)

    return HttpResponse("invalid form", status=500)


def create_manifest(request, container, prefix=None):
    '''Given a file name, upload a manifest file assuming the segments are held
    in a "<file_name>_segments" pseudo folder.

    Return an error if the upload of the manifest fails.

    Return an HTTP request with status 201 if no issues.
    '''
    if (request.POST):
        form = StartSloForm(request.POST)
        if form.is_valid():

            # Get objects in the segment folder
            file_name = form.cleaned_data["file_name"]

            if prefix:
                foldername = prefix + '/' + file_name + '_segments'
            else:
                foldername = file_name + '_segments'

            storage_url = request.session.get('storage_url', '')
            auth_token = request.session.get('auth_token', '')

            foldername = os.path.normpath(foldername)
            foldername = foldername.strip('/')
            foldername += '/'

            meta, objects = client.get_container(
                storage_url, auth_token, container, delimiter='/',
                prefix=foldername)

            pseudofolders, objs = pseudofolder_object_list(objects, prefix)

            # Create

            manifest = []

            # Create a manifest entry for each segment
            for segment in objs:

                manifest.append({
                    "path": container + "/" + segment["name"].encode('ascii', 'ignore'),
                    "etag": segment["hash"].encode('ascii', 'ignore'),
                    "size_bytes": str(segment["bytes"]),
                })

            manifest = sorted(manifest, key=lambda k: k['path'])

            with NamedTemporaryFile() as f:
                json.dump(manifest, f)
                f.seek(0)

                try:

                    #TODO: add prefix to file_name
                    client.put_object(
                        storage_url, auth_token, container.encode('ascii', 'ignore'), file_name, f,
                        query_string="multipart-manifest=put")
                except Exception, e:
                    return HttpResponse("Failed to upload manifest.",
                                        status=500)

            return HttpResponse("Successfully uploaded " + file_name,
                                status=201)

    return HttpResponse("invalid form", status=500)
