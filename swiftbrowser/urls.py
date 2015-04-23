from django.conf import settings
from django.conf.urls.static import static
from django.conf.urls import patterns, include, url

from swiftbrowser.views import containerview, objectview, download,\
    delete_object, login, tempurl, upload, create_pseudofolder,\
    create_container, delete_container, public_objectview, toggle_public,\
    edit_acl, upload_delete, objecttable, serve_thumbnail, \
    move_to_trash, trashview, delete_trash,\
    restore_trash, move_collection_to_trash, restore_trash_collection,\
    download_collection

urlpatterns = patterns(
    'swiftbrowser.views',
    url(r'^login/$', login, name="login"),
    url(r'^$', containerview, name="containerview"),
    url(r'^public/(?P<account>.+?)/(?P<container>.+?)/(?P<prefix>(.+)+)?$',
        public_objectview, name="public_objectview"),
    url(r'^toggle_public/(?P<container>.+?)/$', toggle_public,
        name="toggle_public"),
    url(r'^tempurl/(?P<container>.+?)/(?P<objectname>.+?)$', tempurl,
        name="tempurl"),
    url(r'^create_pseudofolder/(?P<container>.+?)/(?P<prefix>.+)?$',
        create_pseudofolder, name="create_pseudofolder"),
    url(r'^create_container$', create_container, name="create_container"),
    url(r'^delete_container/(?P<container>.+?)$', delete_container,
        name="delete_container"),
    url(r'^download/(?P<container>.+?)/(?P<objectname>.+?)$', download,
        name="download"),
    url(r'^delete/(?P<container>.+?)/(?P<objectname>.+?)$', delete_object,
        name="delete_object"),
    url(r'^objects/(?P<container>.+?)/(?P<prefix>(.+)+)?$', objectview,
        name="objectview"),
    url(r'^object_table/', objecttable, name="objecttable"),
    url(r'upload/', upload, name='jfu_upload'),
    url(r'^acls/(?P<container>.+?)/$', edit_acl, name="edit_acl"),
    url(r'^delete/(?P<pk>.+)$', upload_delete, name='jfu_delete'),
    url(
        r'^thumbnails/(?P<container>.+?)/(?P<objectname>.+?)$',
        serve_thumbnail,
        name="serve_thumbnail"),
    url(
        r'^move_to_trash/(?P<container>.+?)/(?P<objectname>.+?)$',
        move_to_trash,
        name="move_to_trash"),
    url(r'^trashview/(?P<account>.+?)/$', trashview, name="trashview"),
    url(
        r'^delete_trash/(?P<account>.+?)/(?P<trashname>.+?)$',
        delete_trash,
        name="delete_trash"),
    url(
        r'^restore_trash/(?P<account>.+?)/(?P<trashname>.+?)$',
        restore_trash,
        name="restore_trash"),
    url(
        r'^restore_trash_collection/(?P<account>.+?)/(?P<trashname>.+?)$',
        restore_trash_collection,
        name="restore_trash_collection"),
    url(
        r'^move_collection_to_trash/(?P<container>.+?)/(?P<prefix>.+?)?$',
        move_collection_to_trash,
        name="move_collection_to_trash"),
    url(
        r'^download_collection/(?P<container>.+?)/(?P<prefix>.+)?$',
        download_collection,
        name="download_collection"),
    url(
        r'^download_collection_nonrec/(?P<container>.+?)/(?P<prefix>.+)?$',
        download_collection,
        {'non_recursive': True},
        name="download_collection_nonrec"),
) + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
