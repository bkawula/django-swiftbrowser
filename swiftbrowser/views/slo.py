import os
import json
from tempfile import TemporaryFile, NamedTemporaryFile

from django.conf import settings
from django.http import JsonResponse, HttpResponse

from swiftclient import client
from swiftbrowser.forms import StartSloForm
from swiftbrowser.utils import pseudofolder_object_list, \
    get_first_nonconsecutive, calculate_segment_size


def get_segment_number(request, file_name, container, prefix=None):
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

    meta, objects = client.get_container(
        storage_url, auth_token, container, delimiter='/', prefix=foldername,
        headers={"X-Forwarded-For": request.META.get('REMOTE_ADDR')})

    pseudofolders, objs = pseudofolder_object_list(objects, prefix)

    return get_first_nonconsecutive(objs)


def initialize_slo(request, container, prefix=None):
    '''Initiate a slo upload.

    Create a segments container if one does not exist.

    Return the segment number the upload should start at.
    Return the size of the segments.
    Return swift_url

    Create header SLO
    '''

    # Check POST
    if not (request.POST):
        return HttpResponse("No POST in request.", status=500)

    # Check form is valid.
    form = StartSloForm(request.POST)
    if not form.is_valid():
        return HttpResponse("Invalid Form.", status=500)

    # Create container for the segments
    if not create_segments_container(request, container):
        return HttpResponse("Unable to create container", status=500)

    file_name = form.cleaned_data["file_name"]
    file_size = float(form.cleaned_data["file_size"])

    try:
        segment_number = get_segment_number(request, file_name,
                                            container + "_segments", prefix)
    except client.ClientException, e:

        return HttpResponse(e, status=500)

    response = {
        "next_segment": segment_number,
        "segment_size": calculate_segment_size(file_size),
    }

    # Check for headers
    storage_url = request.session.get('storage_url', '')
    auth_token = request.session.get('auth_token', '')
    try:
        cont = client.head_container(storage_url, auth_token, container)
    except client.ClientException, e:
        return HttpResponse(e, status=500)

    # Check header doesn't exist
    path = (file_name if not prefix else prefix + "/" + file_name)

    # Check headers to see if there are any existing SLO
    if not "x-container-meta-slo" in cont:

        # Create a new SLO header with the current path.
        headers = {
            "X-Container-Meta-slo": path,
        }

    else:

        # Check to see if any of the existing SLO matches the current path.
        slo = cont["x-container-meta-slo"]

        matching_slo = False
        for obj in slo.split(","):
            if obj == path:
                matching_slo = True

        # If the current path is not in SLO, add it in by posting back to the
        # container.
        if not matching_slo:
            headers = {
                "x-container-meta-slo": slo + "," + path,
            }
        else:
            headers = {
                "x-container-meta-slo": slo,
            }

    try:
        client.post_container(storage_url, auth_token, container, headers)

    except client.ClientException:
        return JsonResponse({'error': 'Error updating headers.'})

    return JsonResponse(response)


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
                storage_url, auth_token, container + "_segments",
                delimiter='/', prefix=foldername,
                headers={"X-Forwarded-For": request.META.get('REMOTE_ADDR')})

            pseudofolders, objs = pseudofolder_object_list(objects, prefix)

            # Create

            manifest = []

            # Create a manifest entry for each segment
            for segment in objs:

                manifest.append({
                    "path": "/" + container + "_segments/" + segment["name"],
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
                        storage_url, auth_token,
                        container.encode('ascii', 'ignore'), file_name, f,
                        query_string="multipart-manifest=put")
                except Exception, e:
                    return HttpResponse("Failed to upload manifest.",
                                        status=500)

            return HttpResponse("Successfully uploaded " + file_name,
                                status=201)

    return HttpResponse("invalid form", status=500)


def create_segments_container(request, container):
    '''For the given container, create a container with the name
    <container>_segments. Return true on success.'''

    storage_url = request.session.get('storage_url', '')
    auth_token = request.session.get('auth_token', '')
    headers = {
        'X-Container-Meta-Access-Control-Expose-Headers':
        'Access-Control-Allow-Origin',
        'X-Container-Meta-Access-Control-Allow-Origin': settings.BASE_URL
    }

    try:
        client.put_container(
            storage_url, auth_token, container + "_segments", headers)
        return True
    except:
        return False
