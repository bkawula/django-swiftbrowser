""" Standalone webinterface for Openstack Swift. """
# -*- coding: utf-8 -*-
#pylint:disable=E0611, E1101
import os
import time
import urlparse
import hmac
import logging
import string
import random
import re
import Image
from hashlib import sha1

from swiftclient import client

from django.http import HttpResponse
from django.shortcuts import render_to_response, redirect
from django.template import RequestContext
from django.contrib import messages
from django.conf import settings


from django.utils.translation import ugettext as _

from StringIO import StringIO
from swiftbrowser.forms import LoginForm
import swiftbrowser.views

logger = logging.getLogger(__name__)


def get_base_url(request):
    base_url = getattr(settings, 'BASE_URL', None)
    if base_url:
        return base_url
    if request.is_secure():
        base_url = "https://%s" % request.get_host()
    else:
        base_url = "http://%s" % request.get_host()
    return base_url


def replace_hyphens(olddict):
    """ Replaces all hyphens in dict keys with an underscore.

    Needed in Django templates to get a value from a dict by key name. """
    newdict = {}
    for key, value in olddict.items():
        key = key.replace('-', '_')
        newdict[key] = value
    return newdict


def prefix_list(prefix):
    prefixes = []

    if prefix:
        elements = prefix.split('/')
        elements = filter(None, elements)
        prefix = ""
        for element in elements:
            prefix += element + '/'
            prefixes.append({'display_name': element, 'full_name': prefix})

    return prefixes


def pseudofolder_object_list(objects, prefix):
    pseudofolders = []
    objs = []

    duplist = []

    for obj in objects:
        # Rackspace Cloudfiles uses application/directory
        # Cyberduck uses application/x-directory
        
        
        
        if obj.get('content_type', None) in ('application/directory',
                                             'application/x-directory'):
            obj['subdir'] = obj['name']
        
        if 'subdir' in obj:
            # make sure that there is a single slash at the end
            # Cyberduck appends a slash to the name of a pseudofolder
            entry = obj['subdir'].strip('/') + '/'
            if entry != prefix and entry not in duplist:
                duplist.append(entry)
                pseudofolders.append((entry, obj['subdir']))
        else:
            #add extension to object for file icon display
            obj['extension'] = obj.get('name').split('.')[-1]
            if obj.get('extension', None) not in (
            'pdf','png','txt','doc','rtf','log','tex','msg','text','wpd','wps','docx','page','csv',
            'dat','tar','xml','vcf','pps','key','ppt','pptx','sdf','gbr','ged','mp3','m4a','waw',
            'wma','mpa','iff','aif','ra','mid','m3v','swf','avi','asx','mp4','mpg',
            'asf','vob','wmv','mov','srt','m4v','flv','rm','png','psd','psp','jpg','tif','tiff','gif',
            'bmp','tga','thm','yuv','dds','ai','eps','ps','svg','pdf','pct','indd','xlr','xls','xlsx',
            'db','dbf','mdb','pdb','sql','aacd','app','exe','com','bat','apk','jar','hsf','pif','vb',
            'cgi','css','js','php','xhtml','htm','html','asp','cer','jsp','cfm','aspx','rss','csr',
            'less','otf','ttf','font','fnt','eot','woff','zip','zipx','rar','targ','sitx','deb','pkg',
            'rmp','cbr','gz','dmg','cue','bin','iso','hdf','vcd','bak','tmp','ics','msi','cfg','ini',
            'prf'): obj['extension'] = 'other'
            objs.append(obj)
            
    return (pseudofolders, objs)


def redirect_to_objectview_after_delete(objectname, container):
    if objectname[-1] == '/':  # deleting a pseudofolder, move one level up
            objectname = objectname[:-1]
    prefix = '/'.join(objectname.split('/')[:-1])
    if prefix:
        prefix += '/'
    return redirect("objectview", container=container, prefix=prefix)


def get_original_account(storage_url, auth_token, container):
    try:
        headers = client.head_container(storage_url, auth_token, container)
        msp = headers.get('x-container-meta-storage-path')
        if msp is None:
            account = storage_url.split('/')[-1]
            original_container_name = container
        else:
            account = msp.split('/')[2]
            original_container_name = '_'.join(container.split('_')[2:])
    except client.ClientException as e:
        logger.error("Cannot head container %s . Error: %s "
                     % (container, str(e)))
        return (None, None)

    return (account, original_container_name)


def create_pseudofolder_from_prefix(storage_url, auth_token, container,
                                    prefix, prefixlist):
    #Recursively creates pseudofolders from a given prefix, if the
    #prefix is not included in the prefixlist
    subprefix = '/'.join(prefix.split('/')[0:-1])
    if subprefix == '' or prefix in prefixlist:
        return prefixlist

    prefixlist = create_pseudofolder_from_prefix(
        storage_url,
        auth_token,
        container,
        subprefix,
        prefixlist)

    content_type = 'application/directory'
    obj = None

    client.put_object(
        storage_url,
        auth_token,
        container,
        prefix + '/',
        obj,
        content_type=content_type)
    prefixlist.append(prefix)

    return prefixlist


def get_temp_key(storage_url, auth_token):
    """ Tries to get meta-temp-url key from account.
    If not set, generate tempurl and save it to acocunt.
    This requires at least account owner rights. """

    try:
        account = client.get_account(storage_url, auth_token)
    except client.ClientException:
        return None

    key = account[0].get('x-account-meta-temp-url-key')

    if not key:
        chars = string.ascii_lowercase + string.digits
        key = ''.join(random.choice(chars) for x in range(32))
        headers = {'x-account-meta-temp-url-key': key}
        try:
            client.post_account(storage_url, auth_token, headers)
        except client.ClientException:
            return None
    return key


def get_temp_url(storage_url, auth_token, container, objectname, expires=600):
    key = get_temp_key(storage_url, auth_token)
    if not key:
        return None

    expires += int(time.time())
    url_parts = urlparse.urlparse(storage_url)
    path = "%s/%s/%s" % (url_parts.path, container, objectname)
    base = "%s://%s" % (url_parts.scheme, url_parts.netloc)
    hmac_body = 'GET\n%s\n%s' % (expires, path)
    sig = hmac.new(key, hmac_body, sha1).hexdigest()
    url = '%s%s?temp_url_sig=%s&temp_url_expires=%s' % (
        base, path, sig, expires)
    return url


def create_thumbnail(request, account, original_container_name, container,
                     objectname):
    """ Creates a thumbnail for an image. """
    storage_url = request.session.get('storage_url', '')
    auth_token = request.session.get('auth_token', '')

    try:
        client.head_container(storage_url, auth_token,
                              account)
    except client.ClientException:
        try:
            client.put_container(
                storage_url,
                auth_token,
                account)
        except client.ClientException as e:
            logger.error("Cannot put container %s. Error: %s "
                         % (container, str(e)))
            return None
    try:
        headers, content = client.get_object(
            storage_url,
            auth_token,
            container,
            objectname)

        im = Image.open(StringIO(content))
        im.thumbnail(settings.THUMBNAIL_SIZE, Image.ANTIALIAS)
        output = StringIO()
        mimetype = headers['content-type'].split('/')[-1]
        im.save(output, format=mimetype)
        content = output.getvalue()
        headers = {'X-Delete-After': settings.THUMBNAIL_DURABILITY}
        try:
            client.put_object(
                storage_url,
                auth_token,
                account,
                "%s_%s" % (original_container_name, objectname),
                content,
                headers=headers)
        except client.ClientException as e:
            logger.error("Cannot create thumbnail for image %s."
                         "Could not put thumbnail to storage: %s"
                         % (objectname, str(e)))
        output.close()
    except client.ClientException as e:
        logger.error("Cannot create thumbnail for image %s."
                     "Could not retrieve the image from storage: %s"
                     % (objectname, str(e)))
    except IOError as e:
        logger.error("Cannot create thumbnail for image %s."
                     "An IOError occured: %s" % (objectname, e.strerror))

def delete_given_object(request, container, objectname):
    '''Delete the given object. '''

    storage_url = request.session.get('storage_url', '')
    auth_token = request.session.get('auth_token', '')

    client.delete_object(storage_url, auth_token, container, objectname)


def delete_given_folder(request, container, foldername):

    storage_url = request.session.get('storage_url', '')
    auth_token = request.session.get('auth_token', '')

    # Get all objects within folder.
    meta, objects = client.get_container(
        storage_url, auth_token, container, delimiter='/', prefix=foldername)

    # Recursive call to delete subfolders.
    pseudofolders, objs = pseudofolder_object_list(objects, foldername)
    for folder in pseudofolders:
        delete_given_folder(request, container, folder[0])

    # Delete all objects.
    for obj in objs:
        delete_given_object(request, container, obj["name"])

    # Delete the folder itself.
    try:
        delete_given_object(request, container, foldername)
    except:
        #Except a failure to delete if the pseudo folder was not created
        #manually.
        pass


def replace_ip(domain, url):
    '''Given a url, replace one occurence of an IP address with the project's
    base url.'''

    new_url = re.sub('.*(\d{1,3}\.){3}\d', domain, url)

    return new_url


def session_valid(fn):
    '''Decorator class to verify session has not expired before displaying a
    view. Redirect to login when session is not available in the request.'''

    def wrapper(*args, **kw):

        storage_url = args[0].session.get('storage_url', '')
        auth_token = args[0].session.get('auth_token', '')

        try:
            client.head_account(storage_url, auth_token)
            return fn(*args, **kw)
        except:
            messages.error(args[0], _("Session expired."))
        return redirect(swiftbrowser.views.login)

    return wrapper


def ajax_session_valid(fn):
    '''Decorator class to verify session has not expired before displaying a
    view for views that are only accessed with Ajax requests. Return error
    code if failed.'''

    def wrapper(*args, **kw):

        storage_url = args[0].session.get('storage_url', '')
        auth_token = args[0].session.get('auth_token', '')

        try:
            client.head_account(storage_url, auth_token)
            return fn(*args, **kw)
        except:
            messages.error(args[0], _("Session expired."))
        return {'errors': 'true'}

    return wrapper
