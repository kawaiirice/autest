import hashlib

class Request(object):
    ''' Request encapsulates a single request from the UA '''

    def getTimestamp(self):
        return self._timestamp

    def getHeaders(self):
        return self._headers

    def getBody(self):
        return self._body

    def getHeaderMD5(self):
        ''' Returns the MD5 hash of the headers

        This is used to do a unique mapping to a request/response transaction '''
        return hashlib.md5(self._headers.encode()).hexdigest()

    def __repr__(self):
        #return str(self._timestamp)
        return "<Request: {{'timestamp': {0}, 'headers': {1}, 'body': {2}}}>".format(
            str(self._timestamp), str(self._headers), str(self._body)
        )

    def __init__(self, timestamp, headers, body):
        self._timestamp = timestamp
        self._headers = headers
        self._body = body
