import io
import traceback

from django import http
from django.utils.html import escape
from django.views.generic import View

import bricks.json.common
from bricks.js.client import Client, js_compile

__all__ = ['BadResponseError', 'SrviceView', 'SrviceAPIView',
           'SrviceProgramView', 'SrviceHtmlView', 'SrviceJsView']


class BadResponseError(Exception):
    """Exception raised when an srvice API would return an error response
    object."""

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


class SrviceView(View):
    """
    Wraps a srvice API/Program/etc into a view.

    Users should more conveniently use the :func:`srvice.program` or
    :func:`srvice.api decorators`.


    Args:
        function:
            (required) The function handle that implements the given API.
        login_required:
            If True, the API will only be available to logged in users.
        perms_required:
            The list of permissions a user can use in order gain access to the
            API. A non-empty list implies login_required.
    """

    # Class constants and attributes
    valid_content_types = {
        'application/json',
        'application/javascript',
        'text/x-json'
    }
    srvice = None
    function = None
    action = None
    login_required = None
    perms_required = None
    name = None

    @property
    def DEBUG(self):
        from django.conf import settings
        return settings.DEBUG

    # Constructor
    def __init__(self, function, action='api', login_required=False,
                 perms_required=None, ignore_url_args=False, **kwds):
        self.function = function
        self.action = action
        self.login_required = login_required
        self.perms_required = perms_required
        self.ignore_url_args = ignore_url_args
        super().__init__(**kwds)

    def get_data(self, request):
        """
        Decode and return data sent by the client.
        """

        try:
            data_bytes = request.body
            payload = bricks.json.common.loads(data_bytes.decode('utf8'))
        except Exception as ex:
            raise BadResponseError(http.HttpResponseServerError(ex))
        return payload

    def process_data(self, request, data):
        """
        Execute the API function and return a dictionary with the results.
        """

        error = result = program = None
        args = data.get('args', ())
        kwargs = data.get('kwargs', {})
        if not self.ignore_url_args:
            if self.args:
                args = self.args + tuple(args)
            if self.kwargs:
                for k, v in self.kwargs.items():
                    kwargs.setdefault(k, v)

        out = {}

        try:
            out.update(self.execute(request, *args, **kwargs))
        except Exception as ex:
            out['error'] = self.wrap_error(ex, ex.__traceback__)

        return out

    def wrap_error(self, ex, tb=None, wrap_permission_errors=False):
        """
        Wraps an exception raised during the execution of an API function.
        """

        if not wrap_permission_errors and isinstance(ex, PermissionError):
            response = http.HttpResponseForbidden(ex)
            raise BadResponseError(response)

        # Now we create the error object to be sent to javascript
        error = {
            'error': type(ex).__name__,
            'message': str(ex)
        }
        if self.DEBUG:
            file = io.StringIO()
            traceback.print_tb(tb or ex.__traceback__, file=file)
            print(ex, file=file)
            error['traceback'] = '<pre>%s</pre>' % escape(file.getvalue())
        return error

    def execute(self, request, *args, **kwargs):
        """
        Execute API action.

        Any exceptions are wrapped into an error dictionary and sent back in
        the final response.
        """

        return {'result': self.function(request, *args, **kwargs)}

    def check_credentials(self, request):
        """
        Assure that user has the correct credentials to the process.

        Must raise a BadResponseError if credentials are not valid.
        """

        if self.login_required or self.perms_required:
            if request.user is None:
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

    def get_payload(self, data):
        """
        Return the payload that will be sent back to the client.

        The default implementation simply converts data to JSON.
        """

        result = data.get('result')
        program = data.get('program')
        error = data.get('error')

        # Encode result value
        if result is not None:
            try:
                result = bricks.json.common.dumps(result)
            except Exception as ex:
                response = http.HttpResponseServerError(ex)
                raise BadResponseError(response)
        if program is not None:
            try:
                program = bricks.json.common.dumps(program)
            except Exception as ex:
                response = http.HttpResponseServerError(ex)
                raise BadResponseError(response)
        if error is not None:
            try:
                error = bricks.json.common.dumps(error)
            except Exception as ex:
                response = http.HttpResponseServerError(ex)
                raise BadResponseError(response)

        # Manually construct the JSON payload
        payload = ['{']
        if result:
            payload.append('"result":%s,' % result)
        if program:
            payload.append('"program":%s,' % program)
        if error:
            payload.append('"error":%s,' % error)
        if payload[-1].endswith(','):
            payload[-1] = payload[-1][:-1]
        payload.append('}')
        payload = ''.join(payload)
        return payload

    def get_content_type(self):
        """Content type of the resulting message.

        For JSON, it returns 'application/json'."""

        return 'application/json'

    def post(self, request, *args, **kwargs):
        """Process the given request, call handler and return result."""

        try:
            self.check_credentials(request)
            data = self.get_data(request)
            out = self.process_data(request, data)
            payload = self.get_payload(out)
            content_type = self.get_content_type()
        except BadResponseError as ex:
            return ex.response

        return http.HttpResponse(payload, content_type=content_type)

    def get(self, request, *args, **kwargs):
        return http.HttpResponseForbidden(
            'this api-point does not allow GET AJAX requests.'
        )


class SrviceAPIView(SrviceView):
    """
    View to functions registered with the @api decorator.
    """

    srvice = 'api'


class SrviceProgramView(SrviceView):
    """
    View to functions registered with the @program decorator.
    """

    srvice = 'program'

    def get_client(self):
        """
        Return a new Client instance.
        """

        return Client(self.request)

    def execute(self, request, *args, **kwargs):
        out = {}
        self.client = self.get_client()
        try:
            out['result'] = self.function(self.client, *args, **kwargs)
        except Exception as ex:
            out['error'] = self.wrap_error(ex, ex.__traceback__)
        out['program'] = js_compile(self.client)
        return out


class SrviceResponseView(SrviceView):
    """
    View to functions that return response objects.
    """

    data_variable = None

    def execute(self, request, *args, **kwargs):
        out = {}
        try:
            key = self.data_variable
            return {key: self.function(request, *args, **kwargs)}
        except Exception as ex:
            return {'error': self.wrap_error(ex, ex.__traceback__)}


class SrviceJsView(SrviceResponseView):
    """
    View to functions registered with the @js decorator.
    """

    srvice = 'js'
    data_variable = 'js_data'


class SrviceHtmlView(SrviceResponseView):
    """
    View to functions registered with the @html decorator.
    """

    srvice = 'html'
    data_variable = 'html_data'