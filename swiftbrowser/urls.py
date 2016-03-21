from django.conf import settings
from django.conf.urls.static import static
from django.conf.urls import patterns, url

from swiftbrowser.views import *
from swiftbrowser.utils import download_collection, set_default_temp_time
from swiftbrowser.angular_handlers import *

from swiftbrowser.trashviews import move_to_trash, trashview, delete_trash,\
    restore_trash, move_collection_to_trash, restore_trash_collection

urlpatterns = patterns(
    'swiftbrowser.views',

    # views/main.py
    url(r'^login/$', login, name="login"),
    url(r'^create_pseudofolder/(?P<container>.+?)/(?P<prefix>.+)?$',
        create_pseudofolder, name="create_pseudofolder"),
    url(r'^settings$', settings_view, name="settings_view"),
    url(r'^version.info/$', get_version, name="get_version"),
    url(r'^toggle_public/(?P<container>.+?)/$', toggle_public,
        name="toggle_public"),
    url(r'^switch_tenant/(?P<tenant>.+?)/(?P<login>(.+)+)?$', switch_tenant,
        name="switch_tenant"),
    url(r'^switch_tenant/(?P<tenant>.+?)$', switch_tenant,
        name="switch_tenant"),

    #views/containers.py
    url(r'^$', containerview, name="containerview"),
    url(r'^create_container$', create_container, name="create_container"),
    url(r'^delete_container/(?P<container>.+?)$', delete_container,
        name="delete_container"),
    url(r'^delete_container_form/(?P<container>.+?)$', delete_container_form,
        name="delete_container_form"),
    url(r'^get_acls/(?P<container>.+?)/$', get_acls, name="get_acls"),
    url(r'^set_acls/(?P<container>.+?)/$', set_acls, name="set_acls"),
    url(r'^get_total_objects_container/(?P<container>.+?)$', get_total_objects,
        name="get_total_objects_container"),

    # views/objects.py
    url(r'^objects/(?P<container>.+?)/(?P<prefix>(.+)+)?$', objectview,
        name="objectview"),
    url(r'^get_object_table/$', get_object_table, name="get_object_table"),
    url(r'^download/(?P<container>.+?)/(?P<objectname>.+?)$', download,
        name="download"),
    url(r'^delete/(?P<container>.+?)/(?P<objectname>.+?)$', delete_object,
        name="delete_object"),
    url(r'^tempurl/(?P<container>.+?)/(?P<objectname>.+?)$', tempurl,
        name="tempurl"),
    url(r'^object_expiry/(?P<container>.+?)/(?P<objectname>.+?)$',
        object_expiry, name="object_expiry"),
    url(r'^public/(?P<account>.+?)/(?P<container>.+?)/(?P<prefix>(.+)+)?$',
        public_objectview, name="public_objectview"),
    url(r'^get_total_objects/(?P<container>.+?)/(?P<objectname>.+?)$',
        get_total_objects,
        name="get_total_objects"),
    url(r'^delete_folder_form/(?P<container>.+?)/(?P<objectname>.+?)$',
        delete_folder_form,
        name="delete_folder_form"),
    url(r'^delete_folder/(?P<container>.+?)/(?P<objectname>.+?)$',
        delete_folder,
        name="delete_folder"),

    # views/slo.py
    url(r'^initialize_slo/(?P<container>.+?)/(?P<prefix>(.+)+)?$',
        initialize_slo, name="initialize_slo"),
    url(r'^create_manifest/(?P<container>.+?)/(?P<prefix>(.+)+)?$',
        create_manifest, name="create_manifest"),
    url(r'^delete_incomplete_slo/(?P<container>.+?)/(?P<objectname>.+?)$',
        delete_incomplete_slo, name="delete_incomplete_slo"),

    # trashviews.py
    url(r'^move_to_trash/(?P<container>.+?)/(?P<objectname>.+?)$',
        move_to_trash, name="move_to_trash"),
    url(r'^trashview/(?P<account>.+?)/$', trashview, name="trashview"),
    url(r'^delete_trash/(?P<account>.+?)/(?P<trashname>.+?)$',
        delete_trash, name="delete_trash"),
    url(r'^restore_trash/(?P<account>.+?)/(?P<trashname>.+?)$',
        restore_trash, name="restore_trash"),
    url(r'^restore_trash_collection/(?P<account>.+?)/(?P<trashname>.+?)$',
        restore_trash_collection, name="restore_trash_collection"),
    url(r'^move_collection_to_trash/(?P<container>.+?)/(?P<prefix>.+?)?$',
        move_collection_to_trash, name="move_collection_to_trash"),

    # utils.py
    url(r'^download_collection/(?P<container>.+?)/(?P<prefix>.+)?$',
        download_collection, name="download_collection"),
    url(r'^set_object_expiry_time/(?P<container>.+?)/(?P<objectname>.+?)$',
        set_object_expiry_time,
        name="set_object_expiry_time"),
    url(r'^set_default_tempurl_time$', set_default_temp_time,
        name="set_default_tempurl_time"),

    # angular_handlers.py
    url(r'^get_users/$', get_users, name="get_users"),
    url(r'^create_user/$', create_user, name="create_user"),
    url(r'^delete_user/$', delete_user, name="delete_user"),

    # limited_users.py
    url(r'^limited_users_login/$', limited_users_login,
        name="limited_users_login"),
    url(r'^limited_users_containerview/$', limited_users_containerview,
        name="limited_users_containerview"),

) + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
