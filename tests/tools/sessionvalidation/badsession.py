class BadSession(object):
    ''' 
    Session encapsulates a single BAD user session. Bad meaning that for some reason the session is invalid.

    _filename is the filename of the bad JSON session 
    _reason is a string with some kind of explanation on why the session was bad
    '''

    def __repr__(self):
        return "<Session {{'filename': {0}, 'reason': {1}>".format(
            self._filename, self._reason
        )

    def __init__(self, filename, reason):
        self._filename = filename
        self._reason = reason
