from bricks.js.client import Client, js_compile
from bricks.rpc.views import RPCView


class RPCAPIView(RPCView):
    """
    View to functions registered with the @api decorator.
    """

    bricks = 'api'


class RPCProgramView(RPCView):
    """
    View to functions registered with the @program decorator.
    """

    bricks = 'program'

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


class RPCResponseView(RPCView):
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


class BricksJsView(RPCResponseView):
    """
    View to functions registered with the @js decorator.
    """

    bricks = 'js'
    data_variable = 'js_data'


class BricksHtmlView(RPCResponseView):
    """
    View to functions registered with the @html decorator.
    """

    bricks = 'html'
    data_variable = 'html_data'
