======================
Srvice Javascript  API
======================

Basic API
=========

.. js:function:: srvice(api, {args})
    This function call a registered function in the server and return
    its result.

    It can be called either with a pure positional or pure named arguments
    form.

    srvice('api-name', {arg1: value1, arg2: value2, ...}):
       The most common form of remote call requires named arguments.

    srvice('api-name*', arg1, arg2, arg3, ...):
       This will call the remote api function with the given arguments and
       return the result. An asterisk in the end of the api function name
       tells that it expect positional arguments only. This is required if
       you want to pass a single positional argument that is an object in
       order to avoid srvice to interpret it as a dictionary of named
       arguments.

    This function returns a promise object and callback functions can be
    attached to it using the ``.then()``, ``.done()``, ``.fail()``, etc methods:

    .. code-block:: javascript

        srvice('get-user-data', 'user123'))
            .then(function(result) {
                // do something with the result
            })
            .then(function(result) {
                // do something else
            });

    In Django, api functions are registered using the ``@srvice.api``
    decorator to a function. These functions always receive a request as
    the first argument, followed by the arguments passed from javascript.
    The return value is transmitted back to the client and returned to the
    caller.

    .. code-block:: python

        import srvice

        @srvice.api
        def function(request, arg1, arg2, arg3, ...):
           ...
           return value

    All exceptions raised in python-land are transmitted to javascript,
    adapted, and re-raised there.

    Remember that all communication is done through JSON streams, hence all
    input arguments and the resulting value must be JSON-encodable.

    See Also:
        :func:`srvice.sync` - Synchronous call (for debug purposes)

.. js:function:: srvice.sync(api, {args})
    This function accepts the same signature but immediately returns the
    result. Synchronous AJAX functions should never be used in production
    since they lock the client until the request is completed, degrading its
    experience.

    This function exists for debug purposes only.
