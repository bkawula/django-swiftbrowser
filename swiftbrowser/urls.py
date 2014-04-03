from django.conf import settings
from django.conf.urls import patterns, include, url

from swiftbrowser.views import containerview, objectview, download,\
    delete_object, login, tempurl, upload, create_pseudofolder,\
    create_container, delete_container, public_objectview, toggle_public,\
    edit_acl, upload_form, upload_delete, objecttable

urlpatterns = patterns('swiftbrowser.views',
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
    url(r'^acls/(?P<container>.+?)/$', edit_acl, name="edit_acl"),
    url(r'^upload_form/(?P<container>.+?)/(?P<prefix>.+)?$', upload_form, name="upload_form"),
    url( r'upload/', upload, name = 'jfu_upload' ),
    url( r'^delete/(?P<pk>.+)$', upload_delete, name = 'jfu_delete' ),
      
    )

