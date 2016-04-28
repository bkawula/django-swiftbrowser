""" This file holds the trashview functions that is not currently being used."""
def trashview(request, account):
    storage_url = request.session.get('storage_url', '')
    auth_token = request.session.get('auth_token', '')

    #Users are only allowed to view the trash of their own account.
    if storage_url == '' or account != storage_url.split('/')[-1]:
        messages.add_message(request, messages.ERROR, _("Access denied."))
        return redirect(containerview)

    '''(storage_url, auth_token) = client.get_auth(
                            settings.SWIFT_AUTH_URL,
                            settings.TRASH_USER, settings.TRASH_AUTH_KEY)'''

    try:
        client.head_container(storage_url, auth_token, account)
    except client.ClientException:
        try:
            client.put_container(storage_url, auth_token, account)
        except client.ClientException as e:
            logger.error(
                "Cannot put container %s. Error: %s " % (account, str(e))
            )
            messages.add_message(request, messages.ERROR, _("Internal error."))
            return redirect(containerview)

    objs = []
    try:
        x, objects = client.get_container(
            storage_url,
            auth_token,
            account
        )
        for o in objects:
            last_modified = o['last_modified']
            size = 0
            directory = False
            try:
                headers = client.head_object(storage_url,
                                             auth_token,
                                             account, o['name'])
                size = headers.get('x-object-meta-original-length', 0)
                if headers.get('content-type', '') == 'application/directory':
                    directory = True
            except client.ClientException:
                pass

            obj = {'name': o['name'], 'size': size,
                   'last_modified': last_modified, 'dir': directory}
            objs.append(obj)
    except client.ClientException:
        messages.add_message(request, messages.ERROR, _("Access denied."))
        return redirect(containerview)

    return render_to_response(
        "trashview.html",
        {
            'objects': objs,
            'session': request.session,
            'account': account,
        },
        context_instance=RequestContext(request)
    )


def delete_trash(request, account, trashname):
    storage_url = request.session.get('storage_url', '')
    auth_token = request.session.get('auth_token', '')

    if storage_url == '' or account != storage_url.split('/')[-1]:
        messages.add_message(request, messages.ERROR, _("Access denied."))
        return redirect(containerview)

    '''(storage_url, auth_token) = client.get_auth(
                            settings.SWIFT_AUTH_URL,
                            settings.TRASH_USER, settings.TRASH_AUTH_KEY)'''

    try:
        client.delete_object(storage_url, auth_token,
                             account, trashname)
        messages.add_message(request, messages.INFO, _("Object deleted."))
    except client.ClientException:
        messages.add_message(request, messages.ERROR, _("Access denied."))

    return redirect(trashview, account=account)


def restore_trash(request, account, trashname):
    storage_url = request.session.get('storage_url', '')
    auth_token = request.session.get('auth_token', '')

    if storage_url == '' or account != storage_url.split('/')[-1]:
        messages.add_message(request, messages.ERROR, _("Access denied."))
        return redirect(containerview)

    '''(storage_url, auth_token) = client.get_auth(
                            settings.SWIFT_AUTH_URL,
                            settings.TRASH_USER, settings.TRASH_AUTH_KEY)'''
    try:
        x, zipped_content = client.get_object(
            storage_url,
            auth_token,
            account,
            trashname
        )
    except client.ClientException as e:
        logger.error("Cannot retrieve object %s of container %s. Error: %s "
                     % (trashname, account, str(e)))
        messages.add_message(request, messages.ERROR, _("Internal error."))
        return redirect(trashview, account=account)

    container = trashname.split('/')[0]
    objectname = '/'.join(trashname.split('/')[1:])
    inp = StringIO(zipped_content)
    zipf = zipfile.ZipFile(inp, 'r')
    content = zipf.read(objectname)
    zipf.close()

    try:
        client.put_object(storage_url, auth_token, container, objectname,
                          content)
    except client.ClientException as e:
        logger.error("Cannot put object %s to container %s. Error: %s "
                     % (objectname, container, str(e)))
        messages.add_message(request, messages.ERROR, _("Internal error."))
        return redirect(trashview, account=account)

    messages.add_message(request, messages.INFO, _("Object restored."))
    try:
        client.delete_object(storage_url, auth_token,
                             account, trashname)
    except client.ClientException as e:
        logger.error("Cannot delete object %s of container %s. Error: %s"
                     % (trashname, account, str(e)))

    return redirect(trashview, account=account)


def restore_trash_collection(request, account, trashname):
    storage_url = request.session.get('storage_url', '')
    auth_token = request.session.get('auth_token', '')

    if account != storage_url.split('/')[-1]:
        messages.add_message(request, messages.ERROR, _("Access denied."))
        return redirect(containerview)

    '''(storage_url, auth_token) = client.get_auth(
                            settings.SWIFT_AUTH_URL,
                            settings.TRASH_USER, settings.TRASH_AUTH_KEY)'''
    try:
        x, zipped_content = client.get_object(
            storage_url,
            auth_token,
            account,
            trashname
        )
    except client.ClientException as e:
        logger.error("Cannot retrieve object %s of container %s. Error: %s "
                     % (trashname, account, str(e)))
        messages.add_message(request, messages.ERROR, _("Internal error."))
        return redirect(trashview, account=account)

    container = trashname.split('/')[0]
    directory = True
    try:
        client.head_container(storage_url, auth_token, container)
    except client.ClientException:
        try:
            client.put_container(storage_url, auth_token, container)
            directory = False
        except client.ClientException as e:
            logger.error("Cannot put container %s. Error: %s "
                         % (container, str(e)))
            messages.add_message(request, messages.ERROR, _("Internal error."))
            return redirect(trashview, account=account)

    inp = StringIO(zipped_content)
    zipf = zipfile.ZipFile(inp, 'r')
    prefixlist = []
    for name in zipf.namelist():
        try:
            prefix = '/'.join(name.split('/')[0:-1])
            prefixlist = create_pseudofolder_from_prefix(
                storage_url,
                auth_token,
                container,
                prefix,
                prefixlist
            )
        except client.ClientException as e:
            logger.error(
                "Cannot create pseudofolder from prefix %s in "
                "container %s. Error: %s " % (prefix, container, str(e))
            )

        content = zipf.read(name)
        try:
            client.put_object(storage_url, auth_token, container, name,
                              content)
        except client.ClientException as e:
            logger.error(
                "Cannot put object %s to container %s. Error: %s "
                % (name, container, str(e))
            )
            messages.add_message(request, messages.ERROR, _("Internal error."))
    zipf.close()

    msg = "%s restored." % ("Folder" if directory else "Container")
    messages.add_message(request, messages.INFO, _(msg))
    try:
        client.delete_object(storage_url, auth_token,
                             account, trashname)
    except client.ClientException as e:
        logger.error("Cannot delete object %s of container %s. Error: %s"
                     % (trashname, account, str(e)))
    return redirect(trashview, account=account)


def move_to_trash(request, container, objectname):

    storage_url = request.session.get('storage_url', '')
    auth_token = request.session.get('auth_token', '')

    #Is this an alias container? Then use the original account
    #to prevent duplicating.
    (account, original_container_name) = get_original_account(
        storage_url,
        auth_token,
        container
    )
    if account is None:
        messages.add_message(request, messages.ERROR, _("Internal error."))
        return redirect_to_objectview_after_delete(objectname, container)

    '''(storage_url, auth_token) = client.get_auth(
                            settings.SWIFT_AUTH_URL,
                            settings.TRASH_USER, settings.TRASH_AUTH_KEY)'''
    try:
        meta, content = client.get_object(
            storage_url,
            auth_token,
            container,
            objectname
        )

    except client.ClientException as e:
        logger.error("Cannot retrieve object %s of container %s. Error: %s"
                     % (objectname, container, str(e)))
        messages.add_message(request, messages.ERROR, _("Internal error."))
        return redirect_to_objectview_after_delete(objectname, container)

    try:
        client.head_container(storage_url, auth_token, account)
    except client.ClientException:
        try:
            client.put_container(storage_url, auth_token, account)
        except client.ClientException as e:
            logger.error("Cannot put container %s. Error: %s "
                         % (container, str(e)))
            messages.add_message(request, messages.ERROR, _("Internal error."))
            return redirect_to_objectview_after_delete(objectname, container)

    output = StringIO()
    zipf = zipfile.ZipFile(output, 'w')
    zipf.writestr(objectname, content)
    zipf.close()

    trashname = "%s/%s" % (original_container_name, objectname)
    try:
        headers = {'X-Delete-After': settings.TRASH_DURABILITY,
                   'x-object-meta-original-length': meta['content-length']}
        client.put_object(
            storage_url,
            auth_token,
            account,
            trashname,
            contents=output.getvalue(),
            headers=headers
        )
        output.close()
    except client.ClientException as e:
        logger.error("Cannot put object %s to container %s. Error: %s "
                     % (trashname, container, str(e)))
        messages.add_message(request, messages.ERROR, _("Internal error."))
        return redirect_to_objectview_after_delete(objectname, container)

    try:
        client.delete_object(storage_url, auth_token, container, objectname)
    except client.ClientException as e:
        logger.error("Cannot delete object %s of container %s. Error: %s "
                     % (container, objectname, str(e)))
        messages.add_message(request, messages.ERROR, _("Access denied."))

        try:
            client.delete_object(storage_url, auth_token,
                                 account, trashname)
        except client.ClientException:
            pass
        return redirect_to_objectview_after_delete(objectname, container)

    msg = "%s moved to trash." % trashname
    messages.add_message(request, messages.INFO, _(msg))
    return redirect_to_objectview_after_delete(objectname, container)


def move_collection_to_trash(request, container, prefix):
    if request.session['username'] == settings.TRASH_USER:
        return HttpResponseForbidden()

    storage_url = request.session.get('storage_url', '')
    auth_token = request.session.get('auth_token', '')

    #Is this an alias container? Then use the original account
    #to prevent duplicating.
    (account, original_container_name) = get_original_account(
        storage_url,
        auth_token,
        container
    )
    if account is None:
        messages.add_message(request, messages.ERROR, _("Internal error."))
        return (redirect(containerview) if prefix is None else
                redirect_to_objectview_after_delete(prefix, container))

    '''(storage_url, auth_token) = client.get_auth(
                            settings.SWIFT_AUTH_URL,
                            settings.TRASH_USER, settings.TRASH_AUTH_KEY)'''

    try:
        x, objects = client.get_container(
            storage_url,
            auth_token,
            container,
            prefix=prefix
        )
    except client.ClientException as e:
        if prefix is None:
            logger.error(
                "Cannot retrieve container %s."
                "Error: %s " % (container, str(e))
            )
        else:
            logger.error("Cannot retrieve container %s with prefix %s."
                         "Error: %s " % (container, prefix, str(e)))

        messages.add_message(request, messages.ERROR, _("Internal error."))
        return (redirect(containerview) if prefix is None else
                redirect_to_objectview_after_delete(prefix, container))

    x, objs = pseudofolder_object_list(objects, prefix)

    output = StringIO()
    zipf = zipfile.ZipFile(output, 'w')
    original_length = 0
    for o in objs:
        name = o['name']
        try:
            meta, content = client.get_object(storage_url, auth_token,
                                              container, name)
            original_length += int(meta.get('content-length', 0))
        except client.ClientException as e:
            logger.error(
                "Cannot retrieve object %s of container %s. Error: %s"
                % (name, container, str(e)))
            messages.add_message(request, messages.ERROR, _("Internal error."))
            return (redirect(containerview) if prefix is None else
                    redirect_to_objectview_after_delete(prefix, container))

        zipf.writestr(name, content)
    zipf.close()

    try:
        client.head_container(storage_url, auth_token, account)
    except client.ClientException:
        try:
            client.put_container(storage_url, auth_token, account)
        except client.ClientException as e:
            logger.error("Cannot put container %s. Error: %s "
                         % (container, str(e)))
            messages.add_message(request, messages.ERROR, _("Internal error."))
            return (redirect(containerview) if prefix is None else
                    redirect_to_objectview_after_delete(prefix, container))

    trashname = "%s/%s" % (original_container_name,
                           '' if prefix is None else prefix)
    try:
        headers = {'X-Delete-After': settings.TRASH_DURABILITY,
                   'x-object-meta-original-length': str(original_length)}
        client.put_object(
            storage_url,
            auth_token,
            account,
            trashname,
            output.getvalue(),
            content_type='application/directory',
            headers=headers)
        output.close()
    except client.ClientException as e:
        logger.error("Cannot put object %s to container %s. Error: %s "
                     % (trashname, container, str(e)))
        messages.add_message(request, messages.ERROR, _("Internal error."))
        return (redirect(containerview) if prefix is None else
                redirect_to_objectview_after_delete(prefix, container))

    try:
        for o in objects:
            name = o['name']
            client.delete_object(storage_url, auth_token, container, name)
    except client.ClientException as e:
        logger.error(
            "Cannot delete all objects of container %s."
            "Error: %s " % (container, str(e)))
        messages.add_message(request, messages.ERROR, _("Access denied."))

        try:
            client.delete_object(storage_url, auth_token,
                                 account, trashname)
        except client.ClientException:
            pass

        return (redirect(containerview) if prefix is None else
                redirect_to_objectview_after_delete(prefix, container))

    if prefix is None:
        try:
            client.delete_container(storage_url, auth_token, container)
        except client.ClientException as e:
            logger.error("Cannot delete container %s."
                         "Error: %s " % (container, str(e)))
            messages.add_message(request, messages.ERROR, _("Access denied."))

            try:
                client.delete_object(storage_url, auth_token,
                                     account, trashname)
            except client.ClientException:
                pass

            return redirect(containerview)

    msg = "%s moved to trash." % ("Container" if prefix is None else "Folder")
    messages.add_message(request, messages.INFO, _(msg))
    return (redirect(containerview) if prefix is None else
            redirect_to_objectview_after_delete(prefix, container))
