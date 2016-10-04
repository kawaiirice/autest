import sessionvalidation.transaction as transaction

class Session(object):
    ''' Session encapsulates a single user session '''

    def getTransactionList(self):
        ''' Returns a list of transaction objects '''
        return self._transaction_list

    def getTransactionIter(self):
        ''' Returns an iterator of transaction objects '''
        return iter(self._transaction_list)

    def __repr__(self):
        return "<Session {{'filename': {0}, 'version': {1}, 'timestamp: {2}, 'encoding': {3}, 'transaction_list': {4}}}>".format(
                  self._filename, self._version, self._timestamp, self._encoding, repr(self._transaction_list)
            )

    def __init__(self, filename, version, timestamp, transaction_list, encoding=None):
        self._filename = filename
        self._version = version
        self._timestamp = timestamp
        self._encoding = encoding
        self._transaction_list = transaction_list
