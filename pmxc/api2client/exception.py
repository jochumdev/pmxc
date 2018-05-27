class API2Exception(Exception): pass

class VerifyException(API2Exception): pass

class ConnectionException(API2Exception): pass

class HTTPException(API2Exception):
    def __init__(self, url, code, reason):
        super().__init__("%s: %d %s" % (url, code, reason))

        self._url = url
        self._code = code
        self._reason = reason

    @property
    def code(self):
        return self._code

    @property
    def reason(self):
        return self._reason

    def __unicode__(self):
        return "%s: %d %s" % (self._url, self._code, self._reason)

    def __repr__(self):
        return '<HTTPException %s: %d %s>' % (self._url, self._code, self._reason)

class AuthenticationException(HTTPException): pass