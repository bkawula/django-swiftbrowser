"""
This file contains functions to facilitate the uploading of Static Large
Objects (SLO).
"""
import os
import json
from tempfile import NamedTemporaryFile

from django.conf import settings
from django.http import JsonResponse, HttpResponse
from django.shortcuts import render_to_response
from django.template import RequestContext

from swiftclient import client
from swiftbrowser.forms import StartSloForm
from swiftbrowser.utils import pseudofolder_object_list, \
    get_first_nonconsecutive, calculate_segment_size, delete_given_folder, \
    _get_total_objects


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

    When SLO are created, we store information about the SLO in the header of
    the container. This allows us to continue the upload of a SLO if a user
    is disconnected.
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
    path = (file_name if not prefix else prefix + file_name)

    # Check headers to see if there are any existing SLO
    if not "x-container-meta-slo" in cont:

        # Create a new SLO header with the current path.
        headers = {
            "X-Container-Meta-slo": path + ":" + str(file_size),
        }

    else:

        # Check to see if any of the existing SLO matches the current path.
        slo = cont["x-container-meta-slo"]

        matching_slo = False
        for obj in slo.split(","):
            if obj.split(":")[0] == path:
                matching_slo = True

        # If the current path is not in SLO, add it in by posting back to the
        # container.
        if not matching_slo:
            headers = {
                "x-container-meta-slo":
                slo + "," + path + ":" + str(file_size),
            }
        else:
            headers = {
                "x-container-meta-slo": slo,
            }

    # Update the headers.
    try:
        client.post_container(storage_url, auth_token, container, headers)

    except client.ClientException:
        return JsonResponse({'error': 'Error updating headers.'})

    return JsonResponse(response)


def create_manifest(request, container, prefix=None):
    '''Given a file name, upload a manifest file assuming the segments are held
    in a "<file_name>_segments" pseudo folder. Remove the slo header when the
    manifest is successfuly uploaded.

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

            manifest = []

            # Create a manifest entry for each segment
            for segment in objs:

                manifest.append({
                    "path": "/" + container + "_segments/" + segment["name"],
                    "etag": segment["hash"].encode('ascii', 'ignore'),
                    "size_bytes": str(segment["bytes"]),
                })

            manifest = sorted(manifest, key=lambda k: k['path'])

            # Create the manifest in a temp file and upload it
            with NamedTemporaryFile() as f:
                json.dump(manifest, f)
                f.seek(0)

                try:
                    full_file_name = (prefix + file_name
                                      if prefix else file_name)

                    #TODO: add prefix to file_name
                    client.put_object(
                        storage_url, auth_token,
                        container.encode('ascii', 'ignore'), full_file_name, f,
                        query_string="multipart-manifest=put")
                except Exception:
                    return HttpResponse("Failed to upload manifest.",
                                        status=500)

                remove_slo_header(
                    storage_url, auth_token, container, full_file_name)

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


def delete_incomplete_slo(request, container, objectname):
    """ Delete incomplete slo by removing it's segments and removing it
    from the container header. """

    storage_url = request.session.get('storage_url', '')
    auth_token = request.session.get('auth_token', '')

    # Delete the segments
    try:
        delete_given_folder(
            request, container + "_segments", objectname + "_segments")
    except client.ClientException:
        return HttpResponse("Failed to delete segments.", status=500)

    # Remove the object from SLO header.
    remove_slo_header(storage_url, auth_token, container, objectname)

    return HttpResponse(
        "Successfully deleted incomplete static large object " + objectname,
        status=201)


def remove_slo_header(storage_url, auth_token, container, objectname):
    '''Given a slo header value, remove it from the given container.'''

    try:
        headers = client.head_container(storage_url, auth_token, container)
    except client.ClientException, e:
        return HttpResponse(e, status=500)

    if "x-container-meta-slo" in headers:

        slo_header = headers["x-container-meta-slo"]
        new_slo_header = ""

        # Rebuild the header without the slo that was deleted.
        for obj in slo_header.split(","):
            if obj.split(":")[0] != objectname:
                new_slo_header += obj + ","

        if len(new_slo_header) > 0 and new_slo_header[-1] == ",":
            new_slo_header = new_slo_header[0:-1]

        headers = {
            "x-container-meta-slo": new_slo_header
        }

    # Update the header
    try:
        client.post_container(storage_url, auth_token, container, headers)
    except client.ClientException:
        return JsonResponse({'error': 'Error updating headers.'})


def delete_slo_form(request, container, objectname):
    """ Display delete slo template for the modal. """

    slo_name = objectname
    objectname += "_segments"  # Objectname is the object to delete which is
    # the segments folder.

    container += "_segments"

    return render_to_response(
        'delete_folder.html',
        {
            'slo_name': slo_name,
            'objectname': objectname,
            'container': container,
            'foldername': objectname,
            'total_objects': _get_total_objects(
                request, container, objectname),
            'delete_slo': True,
        },
        context_instance=RequestContext(request))
