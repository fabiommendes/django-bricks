import io
import traceback
from logging import getLogger

import sys
from django import http
from django.utils.html import escape
from django.views.generic import View
from lazyutils import lazy

from bricks.js.client import Client, js_compile
from bricks.json import loads, dumps, register

log = getLogger('bricks.rpc')


class BadResponseError(Exception):
    """
    Exception raised when an bricks API would return an error response
    object.
    """

    def __init__(self, *args, **kwds):
        super().__init__(args)
        for (k, v) in kwds.items():
            setattr(self, k, v)

    @property
    def response(self):
        for arg in self.args:
            if isinstance(arg, http.HttpResponse):
                return arg
        else:
            return http.HttpResponseServerError()


class BadRequestError(Exception):
    """
    Exception raised when users make invalid requests.
    """


class RPCView(View):
    """
    Wraps a Bricks RPC end point into a view.


    Args:
        function:
            (required) The function that implements the given API.
        login_required:
            If True, the API will only be available to logged in users.
        perms_required:
            The list of permissions a user can use in order gain access to the
            API. A non-empty list implies login_required.
    """

    # Class constants and attributes
    valid_request_mimetypes = {
        'application/json',
        'application/javascript',
        'text/x-json'
    }
    bricks = None
    function = None
    action = None
    login_required = None
    perms_required = None
    request_argument = True
    name = None

    @lazy
    def DEBUG(self):
        from django.conf import settings
        return settings.DEBUG

    # Constructor
    def __init__(self, function, action='api', login_required=False,
                 perms_required=None, request_argument=True, **kwds):
        self.function = function
        self.action = action
        self.login_required = login_required
        self.perms_required = perms_required
        self.request_argument = request_argument
        super().__init__(**kwds)

    def get_data(self, request):
        """
        Decode and return data sent by the client.
        """

        # Check if user is using a valid content/type
        mimetype = request.content_type
        if mimetype not in self.valid_request_mimetypes:
            raise BadRequestError('invalid content/type: %r' % mimetype)

        # Decode data
        try:
            data_bytes = request.body
            payload = loads(data_bytes.decode('utf8'))
        except Exception as ex:
            log.info('invalid JSON request at %s: %s' % (request.url, ex))
            raise BadRequestError('invalid JSON')

        # Check for JSON-RPC 2.0 header
        if payload.get('jsonrpc', None) != '2.0':
            raise BadRequestError('not a JSON-RPC 2.0 request')

        return payload

    def execute(self, request, data):
        """
        Execute the API function and return a dictionary with the results.
        """

        id = data.get('id', None)
        params = data.get('params', {})

        # Choose how params are interpreted
        if isinstance(params, (list, tuple)):
            args = params
            kwargs = {}
        else:
            args = params.pop('*args', [])
            kwargs = params

        # Add request first argument
        client = Client(request)
        if self.request_argument:
            args.insert(0, client)

        # Prepare response object
        response = {'jsonrpc': '2.0'}
        if id is not None:
            response['id'] = id

        # Execute function and prepare for any errors
        try:
            result = self.function(*args, **kwargs)
            js_data = js_compile(client)
            response['result'] = \
                JsAction(js=js_data, result=result) if js_data else result
        except Exception as ex:
            response['error'] = self.wrap_error(ex, ex.__traceback__)

        return response

    def wrap_error(self, ex, tb=None, wrap_permission_errors=False):
        """
        Wraps an exception raised during the execution of an API function.
        """

        if not wrap_permission_errors and isinstance(ex, PermissionError):
            response = http.HttpResponseForbidden(ex)
            raise BadResponseError(response)

        # Now we create the error object to be sent to javascript
        ex_class = ex.__class__
        ex_fqualname = ex_class.__module__ + '.' + ex_class.__name__
        error = {
            'code': getattr(ex, 'code', 0),
            'message': str(ex),
            'data': {
                'exception': ex_fqualname,
            }
        }

        # Print traceback if running in debug mode
        if self.DEBUG:
            file = io.StringIO()
            traceback.print_tb(tb or ex.__traceback__, file=file)
            file.write('\n%s: %s' % (ex_fqualname, ex))
            html = '<pre>%s</pre>' % escape(file.getvalue())
            error['data']['traceback_html'] = html
            print(file.getvalue(), file=sys.stderr)
        return error

    def check_credentials(self, request):
        """
        Assure that user has the correct credentials to the process.

        Must raise a BadResponseError if credentials are not valid.
        """

        if request.user is None and (
                    self.login_required or self.perms_required):
            response = http.HttpResponseForbidden('login required')
            raise BadResponseError(response)

        if self.perms_required:
            user = request.user
            for perm in self.perms_required:
                if not user.has_perm(perm):
                    msg = 'user does not have permission: %s' % perm
                    response = http.HttpResponseForbidden(msg)
                    raise BadResponseError(response)
                    # TODO: check csrf token

    def get_raw_response(self, request, data):
        """
        Return the payload that will be sent back to the client.

        The default implementation simply converts data to JSON.
        """

        try:
            return dumps(data)
        except Exception as ex:
            response = http.HttpResponseServerError(ex)
            raise BadResponseError(response)

    def get_content_type(self):
        """
        Content type of the resulting message.

        For JSON, it returns 'application/json'.
        """

        return 'application/json'

    def post(self, request, *args, **kwargs):
        """
        Process the given request, call handler and return result.
        """

        try:
            self.check_credentials(request)
            data = self.get_data(request)
            response = self.execute(request, data)
            raw_response = self.get_raw_response(request, response)
            content_type = self.get_content_type()
        except BadResponseError as ex:
            if hasattr(ex, 'response'):
                return ex.response
            raise

        return http.HttpResponse(raw_response, content_type=content_type)

    def get(self, request, *args, **kwargs):
        return http.HttpResponseForbidden(
            'this api-point does not allow AJAX GET requests.'
        )


def jsonrpc_endpoint(login_required=False, perms_required=None):
    """
    Decorator that converts a function into a JSON-RPC enabled view.

    After using this decorator, the function is not usable as a regular function
    anymore.

    .. code-block:: python

        @jsonrpc_endpoint(login_required=True)
        def add_at_server(request, x=1, y=2):
            return x + y
    """

    def decorator(func):
        view = RPCView.as_view(function=func, login_required=login_required,
                               perms_required=perms_required)
        return view

    return decorator


class JsAction:
    def __init__(self, js, result):
        self.js = js
        self.result = result


@register(JsAction, 'js-action')
def encode_js_action(x):
    return {'@': 'js-action', 'js': x.js, 'result': x.result}


@encode_js_action.register_decoder
def decode_js_action(x):
    return JsAction(js=x['js'], result=x['result'])
