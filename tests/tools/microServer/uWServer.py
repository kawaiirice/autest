import string
import http.client
import cgi
import time
import sys
import json
import os
import threading
from http.server import BaseHTTPRequestHandler, HTTPServer
from socketserver import ThreadingMixIn, ForkingMixIn
from http import HTTPStatus

import sessionvalidation.sessionvalidation as sv


SERVER_PORT = 5005 # default port
HTTP_VERSION = 'HTTP/1.1'
G_replay_dict = {}


class ThreadingServer(ThreadingMixIn, HTTPServer):
    '''This class forces the creation of a new thread on each connection'''
    pass

class ForkingServer(ForkingMixIn, HTTPServer):
    '''This class forces the creation of a new process on each connection'''
    pass


# Warning: if you can't tell already, it's pretty hacky
#
# The standard library HTTP server doesn't exactly provide all the functionality we need from the API it exposes,
# so we have to go in and override various methods that probably weren't intended to be overridden
#
# See the source code (https://hg.python.org/cpython/file/3.5/Lib/http/server.py) if you want to see where all these
# variables are coming from
class MyHandler(BaseHTTPRequestHandler):
    def get_response_code(self, header):
        # this could totally go wrong
        return int(header.split(' ')[1])


    def send_response(self, code, message=None):
        ''' Override `send_response()`'s tacking on of server and date header lines. '''
        #self.log_request(code)
        self.send_response_only(code, message)
    def readChunks(self):
        raw_data=b''
        raw_size = self.rfile.readline(65537)        
        size = str(raw_size, 'UTF-8').rstrip('\r\n')
        print("==========================================>",size)
        size = int(size,16)
        while size>0:
            chunk = self.rfile.read(size)
            print("cuhnk: ",chunk)
            raw_data += chunk
            raw_size = self.rfile.readline(65537)
            size = str(raw_size, 'UTF-8').rstrip('\r\n')
            size = int(size,16)
        print("full chunk",raw_data)
        chunk = self.rfile.readline(size) # read the extra blank newline after the last chunk

    def send_header(self, keyword, value):
        """Send a MIME header to the headers buffer."""
        if self.request_version != 'HTTP/0.9':
            if not hasattr(self, '_headers_buffer'):
                self._headers_buffer = []
            self._headers_buffer.append(
                ("%s: %s\r\n" % (keyword, value)).encode('UTF-8', 'strict')) #original code used latin-1.. seriously?

        if keyword.lower() == 'connection':
            if value.lower() == 'close':
                self.close_connection = True
            elif value.lower() == 'keep-alive':
                self.close_connection = False
    def parse_request(self):
        """Parse a request (internal).

        The request should be stored in self.raw_requestline; the results
        are in self.command, self.path, self.request_version and
        self.headers.

        Return True for success, False for failure; on failure, an
        error is sent back.

        """
        self.command = None  # set in case of error on the first line
        self.request_version = version = self.default_request_version
        self.close_connection = True
        requestline = str(self.raw_requestline, 'UTF-8')
        #print("request",requestline)
        requestline = requestline.rstrip('\r\n')
        self.requestline = requestline
        # Examine the headers and look for a Connection directive.
        try:
            self.headers = http.client.parse_headers(self.rfile,
                                                     _class=self.MessageClass)
        except http.client.LineTooLong:
            self.send_error(
                HTTPStatus.BAD_REQUEST,
                "Line too long")
            return False
        except http.client.HTTPException as err:
            self.send_error(
                HTTPStatus.REQUEST_HEADER_FIELDS_TOO_LARGE,
                "Too many headers",
                str(err)
            )
            return False
        if self.headers.get('Transfer-Encoding',"") == 'chunked':
            #print(self.headers)
            self.readChunks()
        
        words = requestline.split()
        if len(words) == 3:
            command, path, version = words
            if version[:5] != 'HTTP/':
                self.send_error(
                    HTTPStatus.BAD_REQUEST,
                    "Bad request version (%r)" % version)
                return False
            try:
                base_version_number = version.split('/', 1)[1]
                version_number = base_version_number.split(".")
                # RFC 2145 section 3.1 says there can be only one "." and
                #   - major and minor numbers MUST be treated as
                #      separate integers;
                #   - HTTP/2.4 is a lower version than HTTP/2.13, which in
                #      turn is lower than HTTP/12.3;
                #   - Leading zeros MUST be ignored by recipients.
                if len(version_number) != 2:
                    raise ValueError
                version_number = int(version_number[0]), int(version_number[1])
            except (ValueError, IndexError):
                self.send_error(
                    HTTPStatus.BAD_REQUEST,
                    "Bad request version (%r)" % version)
                return False
            if version_number >= (1, 1) and self.protocol_version >= "HTTP/1.1":
                self.close_connection = False
            if version_number >= (2, 0):
                self.send_error(
                    HTTPStatus.HTTP_VERSION_NOT_SUPPORTED,
                    "Invalid HTTP Version (%s)" % base_version_number)
                return False
        elif len(words) == 2:
            command, path = words
            self.close_connection = True
            if command != 'GET':
                self.send_error(
                    HTTPStatus.BAD_REQUEST,
                    "Bad HTTP/0.9 request type (%r)" % command)
                return False
        elif not words:
            return False
        else:
            self.send_error(
                HTTPStatus.BAD_REQUEST,
                "Bad request syntax (%r)" % requestline)
            return False
        self.command, self.path, self.request_version = command, path, version

        # read message body
        if self.command == 'POST' and self.headers.get('Content-Length') != None:
            bodysize = int(self.headers.get('Content-Length'))
            print("length of the body is",bodysize)
            message = self.rfile.read(bodysize)
            print("message body",message)

        conntype = self.headers.get('Connection', "")
        if conntype.lower() == 'close':
            self.close_connection = True
        elif (conntype.lower() == 'keep-alive' and
              self.protocol_version >= "HTTP/1.1"):
            self.close_connection = False
        # Examine the headers and look for an Expect directive
        expect = self.headers.get('Expect', "")
        if (expect.lower() == "100-continue" and
                self.protocol_version >= "HTTP/1.1" and
                self.request_version >= "HTTP/1.1"):
            if not self.handle_expect_100():
                return False
        return True

    def do_GET(self):
        global G_replay_dict
        #print("ATS sent me==================>",self.headers)
        request_hash, __ = cgi.parse_header(self.headers.get('Content-MD5'))
        
        if request_hash not in G_replay_dict:
            self.send_response(404)
            self.send_header('Connection', 'close')
            self.end_headers()

        else:
            resp = G_replay_dict[request_hash]
            headers = resp.getHeaders().split('\r\n')

            # set status codes
            status_code = self.get_response_code(headers[0])
            self.send_response(status_code)

            # set headers
            for header in headers[1:]: # skip first one b/c it's response code
                if header == '':
                    continue
                elif 'Content-Length' in header:
                    # we drop the Content-Length header because the wiretrace JSON files are inaccurate
                    # TODO: run time option to force Content-Length to be in headers
                    length = len(bytes(resp.getBody(),'UTF-8')) if resp.getBody() else 0
                    #print("content lenght === >{0}".format(length))
                    self.send_header('Content-Length', str(length))
                    continue
        
                header_parts = header.split(':', 1)
                header_field = str(header_parts[0].strip())
                header_field_val = str(header_parts[1].strip())
                #print("{0} === >{1}".format(header_field, header_field_val))
                self.send_header(header_field, header_field_val)

            self.end_headers()

            # set body
            response_string = resp.getBody()
            #print("response string: ",response_string)
            self.wfile.write(bytes(response_string, 'UTF-8'))

        return
    def do_HEAD(self):
        global G_replay_dict
        print("head request")
        #print("ATS sent me==================>",self.headers)
        request_hash, __ = cgi.parse_header(self.headers.get('Content-MD5'))
        
        if request_hash not in G_replay_dict:
            self.send_response(404)
            self.send_header('Connection', 'close')
            self.end_headers()

        else:
            resp = G_replay_dict[request_hash]
            headers = resp.getHeaders().split('\r\n')

            # set status codes
            status_code = self.get_response_code(headers[0])
            self.send_response(status_code)

            # set headers
            for header in headers[1:]: # skip first one b/c it's response code
                if header == '':
                    continue
                elif 'Content-Length' in header:
                    # we drop the Content-Length header because the wiretrace JSON files are inaccurate
                    # TODO: run time option to force Content-Length to be in headers
                    length = len(bytes(resp.getBody(),'UTF-8')) if resp.getBody() else 0
                    print("content lenght === >{0}".format(length))
                    self.send_header('Content-Length', str(length))
                    continue
        
                header_parts = header.split(':', 1)
                header_field = str(header_parts[0].strip())
                header_field_val = str(header_parts[1].strip())
                #print("{0} === >{1}".format(header_field, header_field_val))
                self.send_header(header_field, header_field_val)

            self.end_headers()
    def do_POST(self):
        
        #print("ATS sent me==================>",self.headers)
        try:
            if self.headers.get('Content-MD5') == None:
                print("Content-MD5 not found")
                self.send_response(404)
                self.send_header('Connection', 'close')
                self.end_headers()
                return
            print("content-md5 is",self.headers.get('Content-MD5'))
            

            global G_replay_dict
            request_hash, __ = cgi.parse_header(self.headers.get('Content-MD5'))              
            if request_hash not in G_replay_dict:
                self.send_response(404)
                self.send_header('Connection', 'close')
                self.end_headers()

            else:
                resp = G_replay_dict[request_hash]
                resp_headers = resp.getHeaders().split('\r\n')
                # set status codes
                status_code = self.get_response_code(resp_headers[0])
                print("response code",status_code)
                self.send_response(status_code)
                #print("reposen is ",resp_headers)
                # set headers
                for header in resp_headers[1:]: # skip first one b/c it's response code
                    
                    if header == '':
                        continue
                    elif 'Content-Length' in header:
                        # we drop the Content-Length header because the wiretrace JSON files are inaccurate
                        # TODO: run time option to force Content-Length to be in headers
                        length = len(bytes(resp.getBody(),'UTF-8')) if resp.getBody() else 0
                        print("content lenght === >{0}".format(length))
                        self.send_header('Content-Length', str(length))
                        continue
            
                    header_parts = header.split(':', 1)
                    header_field = str(header_parts[0].strip())
                    header_field_val = str(header_parts[1].strip())
                    #print("{0} === >{1}".format(header_field, header_field_val))
                    self.send_header(header_field, header_field_val)

                self.end_headers()

                # set body
                response_string = resp.getBody()
                print("response string: ",response_string)
                if response_string != "":                    
                    print("sending body")
                    self.wfile.write(bytes(response_string, 'UTF-8'))
                return
        except:
            e=sys.exc_info()
            print("Error",e,e.tb_lineno,self.headers)
            self.send_response(400)
            self.send_header('Connection', 'close')
            self.end_headers()

def populate_global_replay_dictionary(sessions):
    ''' Populates the global dictionary of {uuid (string): reponse (Response object)} '''
    global G_replay_dict
    print("size",len(G_replay_dict))
    for session in sessions:
        for txn in session.getTransactionIter():
            G_replay_dict[txn._uuid] = txn.getResponse()


def main():
    if len(sys.argv) < 2:
        print("Usage: ./uWs.py replay_files_dir [server_port] [socket_timeout]")
        sys.exit(1)

    # set up global dictionary of {uuid (string): response (Response object)}
    s = sv.SessionValidator(sys.argv[1])
    populate_global_replay_dictionary(s.getSessionIter())
    print("Dropped {0} sessions for being malformed".format(len(s.getBadSessionList())))

    # start server
    try:
        server_port = SERVER_PORT
        socket_timeout = None

        if len(sys.argv) >= 3:
            server_port = int(sys.argv[2])

        if len(sys.argv) >= 4:
            socket_timeout = int(sys.argv[3])

        MyHandler.protocol_version = HTTP_VERSION
        server = ThreadingServer(('', server_port), MyHandler)
        server.timeout = socket_timeout or 5
        print("=== started httpserver ===")
        server.serve_forever()
    except KeyboardInterrupt:
        print("\n=== ^C received, shutting down httpserver ===")
        server.socket.close()
        sys.exit(0)


if __name__ == '__main__':
    main()
