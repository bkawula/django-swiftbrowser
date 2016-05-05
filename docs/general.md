# General Docs

## Running Swiftbrowser in production
Django applications can be run by Apache. In order to do that you need the mod_wsgi module that allows requests to your server be directed to your Django application.

## Code execution flow

### Code execution within Django
When a user makes a request to swiftbrowser, ```myproj/urls.py``` is the main file that maps the string request to a function. These functions are mostly stored in the ```swiftbrowser/views/``` directory.

Within the ```swiftbrowser/views/``` directory there are files for different type of tasks. They are broken up into ```main.py``` for general tasks like login and  ```containers.py``` and  ```objects.py``` for tasks related to containers and objects respectively. These functions then render templates found in the ```swiftbrowser/templates/``` directory which is finally returned to the user.

Files in the ```swiftbrowser/templates/``` "import" or "include" files found in ```swiftbrowser/static/``` directory. In particular, CSS and JavaScript files. The ```swiftbrowser/static/templates``` directory contain templates that are imported through angular.

### Code execution between the browser, Swiftbrowser (Django) and Swift

The following diagram shows the flow of communication between the web browser, Swiftbrowser and Swift.

![Execution flow](images/flow.png "Swiftbrowser execution flow")

For most interactions with Swiftbrowser, requests are sent from the browser to Swiftbrowser. Swiftbrowser then communicates with the Swift cluster directly. This communication is all possible because of [python-swiftclient](https://github.com/openstack/python-swiftclient). Swiftbrowser then collects information and does some manipulation (all within some function within ```swiftbrowser/views/```) before returning it to the browser.

There are a couple of instances where the browser directly communicates to the Swift cluster. In particular, for uploading files. This is thanks to the Swift middleware [form POST](http://docs.openstack.org/developer/swift/api/form_post_middleware.html). For python-swiftclient, communicating to Swift requires a few things for authentication such as storage URL and an auth token. We can generate an AUTH URL and a signature from these credentials to allow the browser to make direct POSTs to the Swift cluster. This is why the arrow from between the Browser and Swift is one way.


## Temp-Url-Keys
The ```Temp-URL-Key``` is header meta data that can be set for tenants and containers. Setting a tenant temp-url-key is a requirement for Swiftbrowser to work. Uploading and downloading is only possible when the ```temp-url-key``` is set on the tenant. Swiftbrowser uses this key to create an auth url and signature that the browser can use to make direct POSTs to Swift.

**Make sure the ```temp-url-key``` is set when you create new tenants**

For users who only have access to specific containers, a temp-url-key needs to be set for each container. The signature generated for this key is scoped to the container and won't work for other containers.

## Debugging

### PDB
[PDB](https://docs.python.org/2/library/pdb.html) is much like GDB (if you've done debugging in C before). This tool is convenient for inspecting what is happening with Swiftbrowser while it interacts with Swift.

To run pdb for swiftbrowser:
```bash
python -m pdb django-swiftbrowser/myproj/manage.py runserver --nothreading --noreload
```

The extra options, ```--nothreading``` and ```--noreload```, are required otherwise the breakpoints will not work.

Here is a quick summary of different commands used in pdb:
```bash
# "b" - creates a breakpoint
b swiftbrowser/views/main.py:37 #This will set a breakpoint on line 37 of the main.py file

# "c" - continue after entering breakpoints
c

# "b" - list all breakpoints
b

# "clear" - clear all breakpoints
clear

# "p" - Once a breakpoint is reached, you can print variable names like so
p <variable name>
```

### Proxy logs
Another great source for information when you're stuck on a bug is to check the logs on the proxy server. When you interact with a Swift cluster, you make requests to it's proxy server. The logs can be found in ```/var/log/swift/proxy.log``` on the proxy server. The log will display information for each request made to the proxy server and may provide more information than you would get using pdb or your browser's developer tools.
