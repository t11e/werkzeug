# -*- coding: utf-8 -*-
"""
    werkzeug.exceptions
    ~~~~~~~~~~~~~~~~~~~

    This module implements a number of Python exceptions you can raise from
    within your views to trigger a standard non 200 response::


    Usage Example
    -------------

    ::

        from werkzeug import BaseRequest, responder
        from werkzeug.exceptions import HTTPException, NotFound

        def view(request):
            raise NotFound()

        @responder
        def application(environ, start_response):
            request = BaseRequest(environ)
            try:
                return view(request)
            except HTTPException, e:
                return e


    As you can see from this example those exceptions are callable WSGI
    applications.  Because of Python 2.3 / 2.4 compatibility those do not
    extend from the response objects but only from the python exception
    class.

    As a matter of fact they are not Werkzeug response objects.  However you
    can get a response object by calling ``get_response()`` on a HTTP
    exception.

    Keep in mind that you have to pass an environment to ``get_response()``
    because some errors fetch additional information from the WSGI
    environment.

    If you want to hook in a different exception page to say, an 404 status
    code, you can add a second except for a specific subclass of an error::

        @responder
        def application(environ, start_response):
            request = BaseRequest(environ)
            try:
                return view(request)
            except NotFound, e:
                return not_found(request)
            except HTTPException, e:
                return e

    Custom Errors
    -------------

    As you can see from the list above not all status codes are available as
    errors.  Especially redirects and ather non 200 status codes that
    represent do not represent errors are missing.  For redirects you can use
    the `redirect` function from the utilities.

    If you want to add an error yourself you can subclass `HTTPException`::

        from werkzeug.exceptions import HTTPException

        class PaymentRequred(HTTPException):
            code = 402
            description = '<p>Payment required.</p>'

    This is the minimal code you need for your own exception.  If you want to
    add more logic to the errors you can override the `get_description()`,
    `get_body()`, `get_headers()` and `get_response()` methods.  In any case
    you should have a look at the sourcecode of the exceptions module.

    **New in Werkzeug 0.2** You can override the default description in the
    constructor with the `description` parameter (it's the first argument for
    all exceptions except of the `MethodNotAllowed` which accepts a list of
    allowed methods as first argument)::

        raise BadRequest('Request failed because X was not present')


    :copyright: 2007 by Armin Ronacher.
    :license: BSD, see LICENSE for more details.
"""
from werkzeug.utils import escape
from werkzeug.wrappers import BaseResponse
from werkzeug.http import HTTP_STATUS_CODES


class HTTPException(Exception):
    """
    Baseclass for all HTTP exceptions.
    """

    code = None
    description = None

    def __init__(self, description=None):
        Exception.__init__(self, '%d %s' % (self.code, self.name))
        if description is not None:
            self.description = description

    def name(self):
        """The status name."""
        return HTTP_STATUS_CODES[self.code]
    name = property(name, doc=name.__doc__)

    def get_description(self, environ):
        """Get the description."""
        return self.description

    def get_body(self, environ):
        """Get the HTML body."""
        return (
            '<!DOCTYPE HTML PUBLIC "-//W3C//DTD HTML 3.2 Final//EN">\n'
            '<title>%(code)s %(name)s</title>\n'
            '<h1>%(name)s</h1>\n'
            '%(description)s\n'
        ) % {
            'code':         self.code,
            'name':         escape(self.name),
            'description':  self.get_description(environ)
        }

    def get_headers(self, environ):
        """Get a list of headers."""
        return [('Content-Type', 'text/html')]

    def get_response(self, environ):
        """Get a response object."""
        headers = self.get_headers(environ)
        return BaseResponse(self.get_body(environ), self.code, headers)

    def __call__(self, environ, start_response):
        response = self.get_response(environ)
        return response(environ, start_response)


class _ProxyException(HTTPException):
    """
    An http exception that expands renders a WSGI application on error.
    """

    def __init__(self, response):
        Exception.__init__(self, 'proxy exception for %r' % response)
        self.response = response

    def get_response(self, environ):
        return self.response


class BadRequest(HTTPException):
    """
    *400* `BadRequest`

    Raise if the browser send something to the application the application
    or server cannot handle.
    """
    code = 400
    description = (
        '<p>The browser (or proxy) sent a request that this server could '
        'not understand.</p>'
    )


class Unauthorized(HTTPException):
    """
    *401* `Unauthorized`

    Raise if the user is not authorized.  Also used if you want to use HTTP
    basic auth.
    """
    code = 401
    description = (
        '<p>The server could not verify that you are authorized to access '
        'the URL requested.  You either supplied the wrong credentials (e.g.'
        ', bad password), or your browser doesn\'t understand how to supply '
        'the credentials required.</p><p>In case you are allowed to request '
        'the document, please check your user-id and password and try '
        'again.</p>'
    )


class Forbidden(HTTPException):
    """
    *403* `Forbidden`

    Raise if the user doesn't have the permission for the requested resource
    but was authenticated.
    """
    code = 403
    description = (
        '<p>You don\'t have the permission to access the requested resource. '
        'It is either read-protected or not readable by the server.</p>'
    )


class NotFound(HTTPException):
    """
    *404* `NotFound`

    Raise if a resource does not exist and never existed.
    """
    code = 404
    description = (
        '<p>The requested URL was not found on the server.</p>'
        '<p>If you entered the URL manually please check your spelling and '
        'try again.</p>'
    )


class MethodNotAllowed(HTTPException):
    """
    *405* `MethodNotAllowed`

    Raise if the server used a method the resource does not handle.  For
    example `POST` if the resource is view only.  Especially useful for REST.

    The first argument for this exception should be a list of allowed methods.
    Strictly speaking the response would be invalid if you don't provide valid
    methods in the header which you can do with that list.
    """
    code = 405

    def __init__(self, valid_methods=None, description=None):
        """
        takes an optional list of valid http methods
        starting with werkzeug 0.3 the list will be mandatory
        """
        HTTPException.__init__(self, description)
        self.valid_methods = valid_methods

    def get_headers(self, environ):
        headers = HTTPException.get_headers(self, environ)
        if self.valid_methods:
            headers.append(('Allow', ', '.join(self.valid_methods)))
        return headers

    def get_description(self, environ):
        m = escape(environ.get('REQUEST_METHOD', 'GET'))
        return '<p>The method %s is not allowed for the requested URL.</p>' % m


class NotAcceptable(HTTPException):
    """
    *406* `Not acceptable`

    Raise if the server cant return any content conforming to the
    `Accept` headers of the client.
    """
    code = 406

    description = (
        '<p>The resource identified by the request is only capable of '
        'generating response entities which have content characteristics '
        'not acceptable according to the accept headers sent in the '
        'request.</p>'
        )


class RequestTimeout(HTTPException):
    """
    *408* `RequestTimeout`

    Raise to signalize a timeout.
    """
    code = 408
    description = (
        '<p>The server closed the network connection because the browser '
        'didn\'t finish the request within the specified time.</p>'
    )


class Gone(HTTPException):
    """
    *410* `Gone`

    Raise if a resource existed previously and went away without new location.
    """
    code = 410
    description = (
        '<p>The requested URL is no longer available on this server and '
        'there is no forwarding address.</p><p>If you followed a link '
        'from a foreign page, please contact the author of this page.'
    )


class LengthRequired(HTTPException):
    """
    *411* `LengthRequired`

    Raise if the browser submitted data but no ``Content-Length`` header which
    is required for the kind of processing the server does.
    """
    code = 411
    description = (
        '<p>A request with this method requires a valid <code>Content-'
        'Lenght</code> header.</p>'
    )


class PreconditionFailed(HTTPException):
    """
    *412* `PreconditionFailed`

    Status code used in combination with ``If-Match``, ``If-None-Match``, or
    ``If-Unmodified-Since``.
    """
    code = 412
    description = (
        '<p>The precondition on the request for the URL failed positive '
        'evaluation.</p>'
    )


class RequestEntityTooLarge(HTTPException):
    """
    *413* `RequestEntityTooLarge`

    The status code one should return if the data submitted exceeded a given
    limit.
    """
    code = 413
    description = (
        '<p>The data value transmitted exceed the capacity limit.</p>'
    )


class RequestURITooLarge(HTTPException):
    """
    *414* `RequestURITooLarge`

    Like *413* but for too long URLs.
    """
    code = 414
    description = (
        '<p>The length of the requested URL exceeds the capacity limit '
        'for this server.  The request cannot be processed.</p>'
    )


class UnsupportedMediaType(HTTPException):
    """
    *415* `UnsupportedMediaType`

    The status code returned if the server is unable to handle the media type
    the client transmitted.
    """
    code = 415
    description = (
        '<p>The server does not support the media type transmitted in '
        'the request.</p>'
    )


class InternalServerError(HTTPException):
    """
    *500* `InternalServerError`

    Raise if an internal server error occoured.  This is a good fallback if an
    unknown error occoured in the dispatcher.
    """
    code = 500
    description = (
        '<p>The server encountered an internal error and was unable to '
        'complete your request.  Either the server is overloaded or there '
        'is an error in the application.</p>'
    )


class NotImplemented(HTTPException):
    """
    *501* `NotImplemented`

    Raise if the application does not support the action requested by the
    browser.
    """
    code = 501
    description = (
        '<p>The server does not support the action requested by the '
        'browser.</p>'
    )


class BadGateway(HTTPException):
    """
    *502* `BadGateway`

    If you do proxing in your application you should return this status code
    if you received an invalid response from the upstream server it accessed
    in attempting to fulfill the request.
    """
    code = 502
    description = (
        '<p>The proxy server received an invalid response from an upstream '
        'server.</p>'
    )


class ServiceUnavailable(HTTPException):
    """
    *503* `ServiceUnavailable`

    Status code you should return if a service is temporarily unavailable.
    """
    code = 503
    description = (
        '<p>The server is temporarily unable to service your request due to '
        'maintenance downtime or capacity problems.  Please try again '
        'later.</p>'
    )


default_exceptions = {}
for exception in HTTPException.__subclasses__():
    if exception.__module__ == 'werkzeug.exceptions' and \
       exception.code is not None:
        default_exceptions[exception.code] = exception
del exception


class Aborter(object):
    """
    When passed a dict of code -> exception items it can be used as
    callable that raises exceptions.  If the first argument to the
    callable is a integer it will be looked up in the mapping, if it's
    a WSGI application it will be raised in a proxy exception.

    The rest of the arguments are forwarded to the exception constructor.
    """

    def __init__(self, mapping=None, extra=None):
        if mapping is None:
            mapping = default_exceptions
        self.mapping = dict(mapping)
        if extra is not None:
            self.mapping.update(extra)

    def __call__(self, code, *args, **kwargs):
        if not args and not kwargs and not isinstance(code, (int, long)):
            raise _ProxyException(code)
        if code not in self.mapping:
            raise LookupError('no exception for %r' % code)
        raise self.mapping[code](*args, **kwargs)


abort = Aborter()
