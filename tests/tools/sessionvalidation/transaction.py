import sessionvalidation.request as request
import sessionvalidation.response as response

class Transaction(object):
    ''' Tranaction encapsulates a single UA transaction '''

    def getRequest(self):
        return self._request

    def getResponse(self):
        return self._response

    def __repr__(self):
        return "<Transaction {{'uuid': {0}, 'request': {1}, 'response': {2}}}>".format(
            self._uuid, self._request, self._response
        )

    def __init__(self, request, response, uuid):
        self._request = request
        self._response = response
        self._uuid = uuid
