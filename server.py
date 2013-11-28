from flask import Flask, Response, request
from werkzeug.datastructures import Headers
import json
import sys
import os
import httplib
import StringIO
import gzip
import config

app = Flask(__name__)

DEFAULT_TEMPLATE_FOLDER = './templates/'

def get_response_template(path):
    filename = os.path.join(template_folder, path)
    resp_template = '{}';
    with file(filename) as f:
        resp_template = f.read()
    return resp_template

def extract_tokens(template):
    tokens = {}
    while template.find('{{') > -1:
        tokenStart = template.find('{{')
        tokenEnd = template.find('}}')
        if tokenEnd == -1:
            raise Exception('Error parsing tokens: token not closed?')
        tokenName = template[tokenStart+2:tokenEnd]
        tokens[tokenName] = ''
        template = template.replace('{{' + tokenName + '}}', '')
    return tokens

def evaluate_tokens(tokens, request):
    for token in tokens.keys():
        value = eval(token.strip())
        tokens[token] = value
    return tokens

def apply_token_values(tokens, response_template):
    for token in tokens.keys():
        response_template = response_template.replace('{{'+token+'}}', tokens[token])
    return response_template

def process_response_template(request, response_template):
    tokens = extract_tokens(response_template)
    tokens = evaluate_tokens(tokens, request)
    template = apply_token_values(tokens, response_template)
    return template

def is_gzipped(response):
    return response[:2].encode('hex') == '1f8b'

def get_live_response(request, path):
    host = config.UPSTREAM_ENDPOINT['host']
    port = config.UPSTREAM_ENDPOINT['port']
    print 'Getting live response from %s:%s/%s' % (host, port, path)
    conn = httplib.HTTPConnection(host, port)
    request_headers = {}
    for key, value in request.headers:
        if key in ["accept-encoding"]:
            continue
        request_headers[key] = value
    conn.request(request.method, '/' + path, body=request.data, headers=request_headers)
    resp = conn.getresponse()
    print 'Response received.'
    contents = resp.read()
    print resp.getheader('content-type')
    if is_gzipped(contents):
        print 'Decoding gzip...'
        gzip_data = gzip.GzipFile(fileobj = StringIO.StringIO(contents))
        contents = gzip_data.read()
    return (contents, resp.getheaders())

def ensure_dir(f):
    d = os.path.dirname(f)
    if not os.path.exists(d):
        os.makedirs(d)

def save_live_response(path, response_data):
    filename = os.path.join(template_folder, path)
    ensure_dir(filename)
    with open(filename, 'w') as output_file:
        output_file.write(response_data)



@app.route('/', defaults={'path': ''}, methods=['GET', 'POST'])
@app.route('/<path:path>', methods=['GET', 'POST'])
def handle_path(path):
    try:
        if not config.BASE_URL_PATH == '':
            path = path.replace(config.BASE_URL_PATH, '')

        response_template = get_response_template(path)
        if len(request.data) > 0:
            request_data = json.loads(request.data)
            response = process_response_template(request_data, response_template)
        else:
            response = response_template
        print 'Serving recorded response.'
        return Response(response, mimetype='application/json')
    except IOError:
        try:
            live_response, headers = get_live_response(request, config.BASE_URL_PATH + path)
            save_live_response(path, live_response)
            resp = Response(live_response, mimetype='application/json')
            for key, value in headers:
                if key in ["set-cookie"]:
                    resp.headers.add(key, value)
            print 'Serving live response.'
            return resp
        except Exception, ex:
            return repr(ex)
    except Exception, e:
        return repr(e)


template_folder = sys.argv[1] if len(sys.argv) > 1 else DEFAULT_TEMPLATE_FOLDER
print ' * Serving data from %s' % template_folder
print ' * Proxying new requests to %s:%s' % (config.UPSTREAM_ENDPOINT['host'], config.UPSTREAM_ENDPOINT['port'])

if __name__ == "__main__":
    app.run(port=config.PORT)