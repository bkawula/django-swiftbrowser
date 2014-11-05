django-swiftbrowser
===================

This is a fork of [cschwede / django-swiftbrowser](https://github.com/cschwede/django-swiftbrowser) that adds [django-jfu](https://github.com/Alem/django-jfu) as the file upload form. 

Quick Install
-------------

1) Install swiftbrowser:

    git clone git://github.com/bkawula/django-swiftbrowser.git
    cd django-swiftbrowser
    sudo python setup.py install

   Optional: run tests

    python runtests.py

2.1) Create a new Django project:

    django-admin.py startproject myproj
    cd myproj
    cp ~/django-swiftbrowser/example/settings.py myproj/settings.py
	mkdir myproj/database

2.2) For development make symlink to the swiftbrowser folder

	ln -s ../swiftbrowser swiftbrowser

3) Adopt myproj/settings.py to your needs, especially settings for Swift and static file directories.

4) Update myproj/urls.py and include swiftbrowser.urls:

    import swiftbrowser.urls

    urlpatterns = patterns('',
        url(r'^', include(swiftbrowser.urls)),
    )

5) Sync Database

	python manage.py syncdb

6) Collect static files:

    python manage.py collectstatic

7) Run development server:
   
    python manage.py runserver

   *Important*: Either use 'python manage.py runserver --insecure' or set DEBUG = True in myproj/settings.py if you want to use the
   local development server. Don't use these settings in production!
   
IMPORTANT CORS INFORMATION!!!
-----------------------------

This browser uses the formpost.py swift middleware. Currently you need to set Access-Control-Allow-Origin header for containers in order to upload as well as set the Temp-URL-Key on your swift account to 'MYKEY'. 

Setting the Temp-URL-Key:

	swift post -m "Temp-URL-Key:MYKEY" -A http://127.0.0.1:5000/v2.0 -V 2 -U tenantID:username -K password
	swift post -m "X-Account-Meta-Temp-URL-Key:MYKEY" -A http://127.0.0.1:5000/v2.0 -V 2 -U tenantID:username -K

Setting the Access-Control-Allow-Origin header on a container:

	curl -i -XPUT -H "X-Auth-Token: TOKEN" -H "X-Container-Meta-Access-Control-Expose-Headers: Access-Control-Allow-Origin" -H "X-Container-Meta-Access-Control-Allow-Origin: http://127.0.0.1(swiftbrowser server)" http://127.0.0.1(openstack server):8080/v1/AUTH_TenantID/ContainerName/

You can get the X-Auth-Token with this:

	curl -d '{ "auth":{ "passwordCredentials":{ "username":"username", "password":"password" }, "tenantName":"tenantName" }}' -H "Content-type: application/json" http://127.0.0.1:5000/v2.0/tokens
