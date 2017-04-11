"""
==============================================
Srvice: Javascript and Django working together
==============================================

The srvice framework corresponds of a small javascript library and a python
counterpart that makes javascript integrate well with django. The core
functionality is the ability to call python server-side functions and scripts
from client in a very transparent way.

All communication between the client and the server is done through JSON. The
client calls a server-side API as if it were a Javascript function and the
server may implement client-side behaviors in Python functions that are
transmitted back to the user and executed in Javascript. On top of this
functionality, srvice also implements some sugar.

How does it work?
=================

Srvice uses JSON to communicate between client and server. Even making some
"extensions" to JSON, this implies that there is a limitation in what kind of
objects can be transmitted from the client to the server and vice-versa. First
we extend JSON so all objects/dictionaries that have a "@" key are handled
as some kind of specialized python or javascript object. For instance, datetime
objects are encoded as::

    {
        '@': 'datetime',
        'data': 1232434342,      // number of seconds since Unix time
        'timezone': 120,         // number of minutes after UTC
    }

(In case you are curious, a dictionary with a '@type' key is encoded as
``{'@type': 'dict', 'data': {...whatever was in the dictionary...}}``).

Hence, the first step after the client makes a remote call to the server is to
encode all arguments using this scheme and wrap it in a structure like the one
bellow

::

    {
        'api': 'some-registered-server-side-function',
        'args': [arg1, arg2, arg3, ...],
        'kwargs': {
            'namedArg1': value1,
            'namedArg2': value2,
            ...
        },
        'action': 'api/program/js/html',
    }

This data is POST'ed into the server as JSON. The server should respond with
another JSON structure like this::

    {
        'result': <result from function call>,
        'program': [
            {'action': 'alert', 'message': 'hello world'},
            {'action': 'jqueryChain', 'selector': 'main', ...},
            ...
        ],
        'error': {
            'error': <error raised during server side execution>,
            'message': <error message>
            'traceback': <full python traceback (only if DEBUG=True)>
        }
    }

The first part to be processed is the "critical" key. If present, it encodes
any internal error that has occurred in the process of calling the server-side
function (but not errors raised by the function). These errors can be:

1. Invalid method used in HTTP request. In most cases, srvice expect POST
   requests.
2. Could not decode input arguments or the resulting value to JSON.
3. The user is not allowed to call the given method.
4. The input parameters do not match the function signature.
5. Invalid API function name.

In Javascript, any of theses errors throw a ??Error, with a `message` attribute
explaining the reason of the error and a numeric `code` attribute with the
number given in parenthesis.

If the server-side function raises an error (with the exception of
PermissionError's, which are always considered to be critical), the error
is encoded in the "error" key. These errors are also re-raised (or thrown) in
javascript, but as a generic Error() class. If Django is running in debug mode,
it also prepends a string with the full Python traceback before the error
message.

These errors are actually processed **after** the "program" part of the
response. The program is a sequence of instructions to be executed in the
client as if it were a javascript function. The srvice.js library can handle
several instructions, which are documented in ???. In the server, these
instructions are codified in the :class:`srvice.Client`.

Finally, the "result" key stores the JSON-encoded return value for the function.


Model query
===========

With srvice, javascript can query and modify registered models in the database.
For obvious security reasons, we do not expose any model by default, but rather,
the user must register explicitly each model that can be transmitted or modified
by the client. This process allows one to specify explicitly which fields
should be available to each user.

**Under construction.**

"""
from functools import wraps, partial

from bricks.views import (SrviceAPIView, SrviceProgramView,
                          SrviceJsView)

__all__ = ['api', 'program', 'js', 'html']


def decorator(decorator_func):
    """
    Makes a function behave like a decorator.
    """

    @wraps(decorator_func)
    def decorated(*args, **kwargs):
        if not args:
            def decorator(func):
                return decorator_func(func, **kwargs)
        elif len(args) == 1:
            func, = args
            if callable(func):
                return decorator_func(func, **kwargs)
            else:
                arg, = args

                def decorator(func):
                    return decorator_func(func, arg, **kwargs)
        else:
            raise TypeError('invalid number of positional arguments')
        return decorator

    return decorated


def make_view(view_cls, func, **kwargs):
    """
    Decorate view function from view class and regular Python function.
    """

    def as_view(**initkwargs):
        initkwargs.update(kwargs)
        view = view_cls.as_view(function=func, **initkwargs)
        return view

    func.as_view = as_view
    return func


@decorator
def api(func, pattern=None, **kwargs):
    """
    Convert a regular Python function in a remote function that can be called
    from Javascript using the :js:func:`srvice()` function. Communication
    between client and server is done through JSON.

    On views.py::

        @srvice.api
        def fib(request, n):
            if n <= 1:
                return 1
            else:
                return fib(request, n - 1) + fib(request, n - 2)

    On urls.py::

        from views import fib

        urlpatterns = [
            url(r'^fib-func/$', fib.as_view()),
        ]

    From javascript (async)::

    .. code:: javascript

        srvice('/fib-func', 5)
            .then(function(result) {
                alert("Fib(5) = " + result);
            });

    Or synchronous::

    .. code:: javascript

        var result = srvice('/fib-func', 5).value();
        alert("Fib(5) = " + result);

    Keyword Args:
        name:
            Name of the API entry point. By default, srvice uses the a
            "app-label.func-name" convention, in which the "app-label"
            corresponds to the root level of the module path in which the
            function was defined and "func-name" is the Python function name.
            In both strings, underscores are replaced by dashes.
        login_required:
            If True (default is False), the API will only work if the user is
            logged-in.
        perm_required:
            A list of required permissions that a logged in user must have in
            order to access the API.
    """

    return make_view(SrviceAPIView, func, **kwargs)


@decorator
def program(func, pattern=None, **kwargs):
    """
    Register a program API.

    This function can be used as a decorator or as a regular function call::

        @srvice.program
        def fat(request, client, n):
            result = 1
            for i in range(1, n + 1):
                result *= i
            client.alert('Factorial of %s = %s' % (n, result))
            return result


    """

    return make_view(SrviceProgramView, func, **kwargs)


@decorator
def html(func, pattern=None, **kwargs):
    """
    Register an HTML API point.
    """

    return make_view(SrviceHTMLView, func, **kwargs)


@decorator
def js(func, pattern=None, **kwargs):
    """
    Register a javascript API point.
    """

    return make_view(SrviceJsView, func, **kwargs)


def route(pattern, *, name=None, method='program', **kwargs):
    """
    Uses Wagtail's RouterPage route decorator and marks the method as a srvice
    API.
    """

    from wagtail.contrib.wagtailroutablepage.models import route

    # Mapping from names to srvice decorators
    srvice_decorator = {
        'api': api,
        'program': program,
        'html': html,
        'js': js,
    }[method]
    srvice_kwargs = kwargs

    # We create a wrapped method that is decorated with the @route decorator
    # from wagtailroutablepage.
    #
    # Inside the wrapped method, we choose some specific srvice decorator
    # and apply the correct srvice decorator, instantiate the view and call
    # it with the proper request.
    def decorator(func):
        @route(pattern, name=name)
        def wrapped_method(self, request, *args, **kwargs):
            bind_method = partial(func, self)
            srvice_function = srvice_decorator(**srvice_kwargs)(bind_method)
            srvice_view = srvice_function.as_view()
            response = srvice_view(request, *args, **kwargs)
            return response

        func.__dict__.update(wrapped_method.__dict__)
        return func

    return decorator


def srvice_register(view_cls, *args, name=None, register=True, **kwargs):
    """
    Worker function for api and program callbacks.
    """

    # Decorator form
    if not args or isinstance(args[0], str):
        if args:
            name, *args = args

        def decorator(func):
            srvice_register(view_cls, func, *args, name=name)
            return func
        return decorator

    # Register SrviceView
    if len(args) == 2:
        if name is None:
            name, *args = args
        else:
            raise TypeError('function expect a single positional argument')
    if len(args) != 1:
        raise TypeError('invalid number of positional arguments')

    # Compute the default name, if not given
    func = args[0]

    if name is None:
        func_name = func.__qualname__
        mod_name = func.__module__
        name = ('%s.%s' % (func_name, mod_name)).replace('_', '-')

    # Create view and register
    view = view_cls.as_view(func, name=name, **kwargs)

    if register:
        if name in __srvice_registry__:
            raise ValueError('api %r already exists' % name)
        __srvice_registry__[name] = view
    return view

__srvice_registry__ = {}
