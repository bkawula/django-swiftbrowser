# Install Guide

## Requirements
* virtualenv
* python == 2.7.10
* Pillow 3.2.0 ```pip install Pillow==3.2.0```

## Installation steps

1. Set up a virtual environment
    1. Create a virtual environment

        ```bash
        virtualenv swiftbrowserenv
        cd swiftbrowserenv
        ```

    2. Activate the virtual environment

        ```bash
        source bin/activate
        ```

2. Download and install
    ```bash
    git clone git://github.com/bkawula/django-swiftbrowser.git
    cd django-swiftbrowser
    python setup.py install
    ```

3. Setup your Django project. Django projects are made up of modules which are called apps.
    1. Initiate a new app called ```myproj``` (or your name of choice). It will be the main app within your Django project that "imports" swiftbrowser as an app.
        ```bash
        django-admin.py startproject myproj
        cd myproj
        ```

    2. Copy the sample settings.py file to the newly created app.
        ```bash
        cp ../example/settings.py myproj/settings.py
        ```

    3. Adopt ```myproj/settings.py``` to your needs, specifically settings for Swift such as ```SWIFT_AUTH_URL```, ```SWIFT_AUTH_VERSION```, ```BASE_URL``` and ```STATIC_DIR```. The following is an example used in development:
        ```python
        SWIFT_AUTH_URL = 'https://yourswiftserver.com:5000/v2.0/'
        SWIFT_AUTH_VERSION = 2  # 2 for keystone
        BASE_URL = 'http://localhost:8000'
        STATIC_DIR = 'swiftbrowser/static/'
        ```

    4. Create a directory for Django to put it's database.
        ```bash
        mkdir myproj/database
        ```

    5. In this step, we make the swiftbrowser app available to the main app "myproj". This is done by making a symlink to the swiftbrowser folder.

        ```bash
        ln -s ../swiftbrowser swiftbrowser
        ```

    6. As mentioned earlier, "myproj" in a way "imports" swiftbrowser as an app. This is done by adding it into the ```myproj/urls.py``` file. This is Django's file to route requests to different functions.
        1. Update the ```myproj/urls.py``` by adding the following to the top of your file:
            ```python
            import swiftbrowser.urls
            ```

        2. Edit your ```urlpatterns``` variable by adding ```url(r'^', include(swiftbrowser.urls))```. Once done, your urlpatterns will look something like this:
            ```python
            urlpatterns = [
                # Examples:
                # url(r'^$', 'myproj.views.home', name='home'),
                # url(r'^blog/', include('blog.urls')),

                url(r'^admin/', include(admin.site.urls)),
                url(r'^', include(swiftbrowser.urls)), # Add this line
            ]
            ````

4. Setup the Django app for development.
    1. Django manages database queries through classes (in ```models.py```). The following step ensures that any database requirements have been applied to the database. Swiftbrowser doesn't use a database as it's simply a gateway to a Swift cluster but for development purposes this step is required. You'll be asked to create an admin user but you'll never need to use it.
        ```bash
        python manage.py syncdb
        ```

    2. Static files across all the "apps" in this django project are collected to one place to be served out.
        ```bash
        python manage.py collectstatic
        ```

    3. That's it! The following will run the development server:
        ```bash
        python manage.py runserver
        ```

If you're planning to do any front end changes, specifically any CSS changes, be sure to read the [Compiling the CSS (Foundation)](foundation.md).

### Extra step for Scholars Portal Staff
At Scholars Portal, we have access to a paid library of icons from [Glyphicons](http://glyphicons.com/). Our copy is held on gitlab - so ask someone on the systems team to give you access to the "fonts" repository under "Bartek Kawula". To add this library to the repo, follow these steps:

1. Change directories to your django-swiftbrowser repository.
    ```bash
    cd django-swiftbrowser
    ```

2. Initalize the submodule within the django-swiftbrowser repository.
    ```bash
    git submodule init
    ```

3. Pull in the files from the repository.
    ```bash
    git submodule update
    ```

4. Move these new files into the static directory.
    ```bash
    python myproj/manage.py collectstatic
    ```
