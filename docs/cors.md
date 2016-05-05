#CORS - Cross Origin Resource Sharing

The main reason Swiftbrowser works is because Swift can handle POSTs in any form. From servers, machines and directly from a browser. But in order for this to work, each container must have the header meta-data ```Access-Control-Expose-Headers``` set to ```Access-Control-Allow-Origin``` and ```Access-Control-Allow-Origin``` set to the URL Swiftbrowser is hosted at.

Swiftbrowser ensures that these headers are set when a container is created. But it only does this correctly when ```BASE_URL``` in ```myproj/settings.py``` is set correctly.

##CORS errors
Sometimes your browser will receive a CORS related error and sometimes it feels like CORS is a default error message. As long as the above headers are set, it may not actually be a CORS related error at all. Check the logs instead to find out more.