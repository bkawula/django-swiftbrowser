django-swiftbrowser
===================

This is a fork of [cschwede / django-swiftbrowser](https://github.com/cschwede/django-swiftbrowser) that uses [django-storage-swift](https://github.com/wecreatepixels/django-storage-swift) instead of the formpost middleware.

Simple web app build with Django and Twitter Bootstrap to access Openstack Swift.

* Works with keystone, tempauth & swauth
* Support for public containers. ACL support in the works
* Minimal interface, usable on your desktop as well as on your smartphone

Quick Install
-------------

1) Install swiftbrowser:

    git clone git://github.com/bkawula/django-swiftbrowser.git
    cd django-swiftbrowser
    sudo python setup.py install

   Optional: run tests

    python runtests.py

2) Create a new Django project:

    django-admin.py startproject myproj
    cd myproj
    cp ~/django-swiftbrowser/example/settings.py myproj/settings.py
	mkdir myproj/database

3) Adopt myproj/settings.py to your needs, especially settings for Swift and static file directories.

4) Update myproj/urls.py and include swiftbrowser.urls:

    import swiftbrowser.urls

    urlpatterns = patterns('',
        url(r'^', include(swiftbrowser.urls)),
    )

5) Collect static files:

    python manage.py collectstatic

6) Run development server:
   
    python manage.py runserver

   *Important*: Either use 'python manage.py runserver --insecure' or set DEBUG = True in myproj/settings.py if you want to use the
   local development server. Don't use these settings in production!

