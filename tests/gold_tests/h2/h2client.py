import json
from hyper import HTTPConnection
import hyper
import argparse

def getResponseString(response):
    typestr = str(type(response))
    if typestr.find('HTTP20') != -1:
        string = "HTTP/2 {0}\r\n".format(response.status)
    else:
        string = "HTTP {0}\r\n".format(response.status)
    string+='date: '+response.headers.get('date')[0].decode('utf-8')+"\r\n"
    string+='server: '+response.headers.get('Server')[0].decode('utf-8')+"\r\n"
    return string

def makerequest(port):
    hyper.tls._context = hyper.tls.init_context()
    hyper.tls._context.check_hostname = False
    hyper.tls._context.verify_mode = hyper.compat.ssl.CERT_NONE

    conn = HTTPConnection('localhost:{0}'.format(port), secure=True)

    sites={'/'}
    responses = []
    request_ids = []
    for site in sites:
            request_id = conn.request('GET',url=site)
            request_ids.append(request_id)

    # get responses
    for req_id in request_ids:
        response = conn.get_response(req_id)    
        print(getResponseString(response))

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--port","-p",
                        type=int,                        
                        help="Port to use")
    args=parser.parse_args()
    makerequest(args.port)

if __name__ == '__main__':
    main()
    
