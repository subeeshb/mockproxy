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