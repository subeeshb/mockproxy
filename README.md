mockproxy
=========

This is a Flask-based web application that acts as a proxy server to an API, letting you capture and repeat HTTP responses. Recorded responses can be useful when testing applications that rely on web service data.

Pre-requisites
--------------

To use this script, you must first install the Flask web application framework. You can do this using pip using the command below, or refer to detailed instructions here: http://flask.pocoo.org/

```
$ pip install Flask
```


Usage
-----

Update the values in config.py. Specify the port the application should listen on, the base url (if any), and the details of the upstream API that you want to proxy to.

```python
#which port should the server run on?
PORT = 5000

#what's the base url path? e.g. do all web service requests start with 'api/'?
BASE_URL_PATH = 'api/'

#what's the actual web service endpoint? requests will be proxied here if there's
#no recorded data available.
UPSTREAM_ENDPOINT = {
	'host' : '127.0.0.1',
	'port' : '8080'
}
```

Then, just start the application by running server.py. You can specify an output folder for saving web responses as a parameter, otherwise the default output folder will be 'templates'.

```
$ python server.py [output folder]
```


Recording and playback
----------------------

Each web service response is saved in its own file, with the folder structure in the output folder matching the url path. When a request is received, the application proxies the request to the upstream API if no response was previously recorded. If a recorded response is present, the contents of the response are processed and played back. 

The application current supports request data in JSON format. You can insert dynamic values into recorded responses by enclosing python code within {{ ... }} blocks. Request data is converted into a dictionary and can be referenced using the 'request' variable.

For example, with the following request data,

```
{
	"userid":"user001",
	"password":"mypassword"
}
```

, a request to a URL with the following recorded response

```
{
	"loginstatus":"success",
	"userid":"{{ request['userid'] }}"
}
```

will return the following 

```
{
	"loginstatus":"success",
	"userid":"user001"
}
```
