import re
from collections import UserString
from functools import singledispatch

from lazyutils import lazy

import bricks.json.common
from bricks.exceptions import EvalError, InternalError, RangeError, ReferenceError, \
    URIError
from bricks.json import decoders

is_var_name_re = re.compile(r'^[a-zA-Z_]+[a-zA-Z0-9_]*$')


class JsSource(UserString):
    """
    A string of javascript source code.
    """

    def  __init__(self, source, client):
        self.client = client
        self.client._actions.append(self)
        super().__init__(source)

    def _js_source_(self):
        return str(self)


class JsVariable:
    """
    A javascript variable.
    """

    def __init__(self, name, client):
        self._name = name
        self._client = client
        self._varname = None
        self._client._actions.append(self)

    def __getattr__(self, attr):
        if attr.startswith('_'):
            raise AttributeError(attr)

        return JsVariable(self._name + '.' + attr, self._client)

    def __call__(self, *args, **kwargs):
        function = JsFunctionCall(self._name, self._client, args, kwargs)

        if function._returns:
            return function

    def _js_source_(self):
        return None


class JsFunctionCall(JsVariable):
    """
    Represents a Javascript function call.
    """

    # List of functions that are known for not returning anything.
    _impure_functions = [
        'alert', 'console.log',
        'srvice.go',
    ]

    def __init__(self, name, client, args, kwargs):
        super().__init__(name, client)
        self._args = args
        self._kwargs = kwargs

    def __getattr__(self, attr):
        if attr.startswith('_'):
            raise AttributeError(attr)
        varname = '%s.%s' % (self._var_name, attr)
        return JsVariable(varname, self._client)

    def __call__(self, *args, **kwargs):
        return self._result_var(*args, **kwargs)

    @lazy
    def _returns(self):
        return self._name not in self._impure_functions

    @lazy
    def _var_name(self):
        return self._client._next_var_name()

    @lazy
    def _result_var(self):
        return JsVariable(self._var_name, self)

    @lazy
    def _js_args(self):
        args = ', '.join(js_source(x) for x in self._args)
        if self._kwargs:
            if args:
                args += ', %s' % js_source(self._kwargs)
            else:
                args = js_source(self._kwargs)
        return args

    def _js_source_(self):
        fcall = '%s(%s);' % (self._name, self._js_args)
        if self._returns:
            return 'var %s = %s' % (self._var_name, fcall)
        else:
            return fcall


class JsFunctionDef:
    def __init__(self, client, name=None):
        self._client = client
        self._name = name
        self._args = None
        self._body = None

    def __call__(self, *args):
        self._args = args
        return self

    def __getitem__(self, key):
        if isinstance(key, str):
            key = (key,)
        self._body = key
        return self

    def __getattr__(self, attr):
        if attr.startswith('_'):
            raise ValueError('function name cannot start with "_"')
        return JsFunctionDef(self._client, attr)

    def _js_source_(self):
        args = ','.join(self._args)
        if self._name is None:
            head = 'function(%s)' % args
        else:
            head = 'function %s(%s)' % (self._name, args)
        name = self._name or ''
        args = ', '.join(self._args)
        body = ''.join('    %s;\n' % x for x in self._body)
        return '%s {\n%s}' % (head, body)


class JQuerySelection(JsVariable):
    def __init__(self, name, client, selector):
        super().__init__(name, client)
        self.selector = selector


class Client:
    """
    Represents an RPC session with a client.
    """

    _ERROR_MAP = {
        TypeError: 'TypeError',
        SyntaxError: 'SyntaxError',
        IndexError: 'RangeError',
        OverflowError: 'RangeError',
        RuntimeError: 'InternalError',
        EvalError: 'EvalError',
        InternalError: 'InternalError',
        RangeError: 'RangeError',
        ReferenceError: 'ReferenceError',
        URIError: 'URIError',
    }

    def __init__(self, request):
        self.request = request
        self._actions = []
        self._var_index = 0

    def __getattr__(self, attr):
        return self[attr]

    def __getitem__(self, name):
        return JsVariable(name, self)

    def __call__(self, selector):
        return self.jQuery(selector)

    # Delegate some attributes to the request object
    COOKIES = property(lambda x: x.request.COOKIES)
    FILES = property(lambda x: x.request.FILES)
    GET = property(lambda x: x.request.GET)
    POST = property(lambda x: x.request.POST)
    META = property(lambda x: x.request.META)
    LANGUAGE_CODE = property(lambda x: x.request.LANGUAGE_CODE)
    user = property(lambda x: x.request.user)

    @property
    def function(self):
        """
        This implements the idiom to define simple javascript functions with a
        javascript-like syntax::

            client.function('x', 'y')['''
                var z = x + y;
                return x * z + y;
            ''']

        This syntax abuses Python's getitem to define simple javascript
        functions in a slightly more convenient way than explicit manipulation
        of strings with javascript source code.

        Argument names should be passed as strings to the self.function object
        and square brackets should contain strings with lines of javascript
        source. You may put the whole body of the function inside a single
        string or separate each line as a different string argument.
        """

        return JsFunctionDef(self)

    def _next_var_name(self):
        """
        Return the next available generic variable name.

        Variables are created as __vX, where X is a number.
        """

        self._var_index += 1
        return '__v%s' % self._var_index

    def call(self, function, *args, **kwargs):
        """
        Calls the javascript function with the given arguments.
        """

        if kwargs:
            args += (kwargs,)
        return JsFunctionCall(function, self, args)

    def error(self, exception, message=None):
        """
        Function is used to raise an error in the client after executing
        some functions::

            @srvice.program
            def sqrt(js, x):
                value = math.sqrt(x) if x >=0 else None

                if value is not None:
                    js.alert(math.sqrt(x))
                else:
                    js.error(ValueError, 'cannot compute square root of '
                                         'a negative number')
        """

        if isinstance(exception, Exception):
            js_error = self._ERROR_MAP.get(type(exception), 'Error')
            if message is None:
                message = str(exception)
        elif isinstance(exception, str):
            js_error = exception
        elif issubclass(exception, Exception):
            js_error = self._ERROR_MAP.get(exception, 'Error')
        else:
            raise TypeError('invalid exception: %r' % exception)

        src = 'throw %s(%r);' % (js_error, str(message))
        JsSource(src, self)

    def js(self, source):
        """
        Evaluate string of javascript source.
        """

        JsSource(source, self)

    def html(self, source, element=None):
        """
        Replace html code of the given element or jquery selector.

        If no element is given, uses the element which called the function.
        """

        if element is None:
            element = JsVariable('this', self)
        return self.jQuery(element).html(source)

    def redirect(self, url, link=True):
        """
        Redirect to the given url.

        If ``as_link=True``, make a redirect as if the user had clicked on a
        link. Otherwise, make a new http request.
        """

        return self.srvice.go(url, link)

    def dialog(self, html=None, *,
               dialog='dialog',
               container=None,
               action='open',
               source=None):
        """
        Controls dialog box.

        Args:
            action:
                An action to perform on the dialog. It can be either 'open',
                'close' or 'toggle'.
            dialog:
                The id to the dialog element.
            container:
                The id to a child element in the dialog that should receive
                the new html data. If no element is given, uses the dialog
                element itself.
            html:
                The inner HTML text that will be inserted in the container
                element.
            source:
                The id to the source element. You can pass an element in the
                DOM to have its HTML copied into the dialog.
        """

        # Choose the srvice method associated with the action
        if action == 'open':
            method = self.srvice.dialog
        elif action == 'close':
            method = self.srvice.closeDialog
        elif action == 'toggle':
            method = self.srvice.toggleDialog
        else:
            raise ValueError('invalid action: %r' % action)

        kwargs = {}
        if html: kwargs['html'] = str(html)
        if dialog != 'dialog': kwargs['dialogId'] = dialog
        if container: kwargs['dialogContentId'] = container
        if source: kwargs['sourceId'] = source
        return method(**kwargs)


def js_compile(client):
    """
    Compile all instructions in the client into a valid javascript source.
    """

    lines = []
    for action in client._actions:
        source = action._js_source_()
        if source:
            lines.append(source)
    js_source = '\n'.join(lines)
    return js_source


@singledispatch
def js_source(x):
    """
    Returns the Javascript source representation/equivalence of the given
    object.
    """

    if hasattr(x, '_js_source_'):
        return x._js_source_()
    else:
        return 'srvice.json.decode(%s)' % bricks.json.common.dumps(x)


@js_source.register(str)
@js_source.register(int)
@js_source.register(float)
def _(x):
    return repr(x)


@js_source.register(type(None))
def _(x):
    return 'null'


@js_source.register(bool)
def _(x):
    return str(x).lower()


@js_source.register(list)
@js_source.register(tuple)
def _(seq):
    return '[%s]' % (', '.join(map(js_source, seq)))


@js_source.register(dict)
def _(map):
    data = []
    for k, v in map.items():
        if not isinstance(k, str):
            raise TypeError('Javascript dicts only accept string keys')
        if is_var_name(k):
            data.append('%s: %s' % (k, js_source(v)))
        else:
            data.append('%r: %s' % (k, js_source(v)))

    return '{%s}' % (', '.join(sorted(data)))


@js_source.register(JsVariable)
def _(x):
    return x._name


def is_var_name(st):
    """Return True if string is a valid js variable name."""

    return bool(is_var_name_re.match(st))