class Response(object):
    ''' Response encapsulates a single request from the UA '''

    def getTimestamp(self):
        return self._timestamp

    def getHeaders(self):
        return self._headers

    def getBody(self):
        return self._body

    def __repr__(self):
        return "<Response: {{'timestamp': {0}, 'headers': {1}, 'body': {2}}}>".format(
            self._timestamp, self._headers, self._body
        )

    def __init__(self, timestamp, headers, body):
        self._timestamp = timestamp
        self._headers = headers
        self._body = body
