===============
Javascript  API
===============

Basic API
=========

.. js:function::
    bricks(api_name, {args})

    This function call a registered function in the server and return
    its result.

    It can be called either with a pure positional or pure named arguments
    form.

    bricks('api-name', {arg1: value1, arg2: value2, ...}):
       The most common form of remote call requires named arguments.

    bricks('api-name*', arg1, arg2, arg3, ...):
       This will call the remote api function with the given arguments and
       return the result. An asterisk in the end of the api function name
       tells that it expect positional arguments only. This is required if
       you want to pass a single positional argument that is an object in
       order to avoid bricks RPC to interpret it as a dictionary of named
       arguments.

    This function returns a jQuery promise and callbacks can be attached to it
    using the ``.then()``, ``.done()``, ``.fail()``, etc methods:

    .. code-block:: javascript

        bricks('get-user-data', 'user123'))
            .then(function(result) {
                // do something with the result
            })
            .then(function(result) {
                // do something else
            });

    In Django, api functions are registered using the ``@bricks.rpc.api``
    decorator to a function. These functions always receive a request as
    the first argument, followed by the arguments passed from javascript.
    The return value is transmitted back to the client and returned to the
    caller.

    .. code-block:: python

        import bricks

        @bricks.rpc.api
        def function(request, arg1, arg2, arg3, ...):
           ...
           return value

    All exceptions raised in python-land are transmitted to javascript,
    adapted, and re-raised there.

    Remember that all communication is done through JSON streams, hence all
    input arguments and the resulting value must be JSON-encodable.

    See Also:
        :js:func:`bricks.sync` - Synchronous call (for debug purposes)


.. js:function::
    bricks.sync(api_name, {args})

    This function accepts the same signature but immediately returns the
    result. Synchronous AJAX functions should never be used in production
    since they lock the client until the request is completed, degrading user
    experience. You won't notice it testing locally since the latency is so low, but
    surely a client in a slow internet connection with think your site is broken.

    This function exists for debug purposes only.

.. js:function::
    bricks.call(api_name, {args})

    Like the regular bricks function, but will not run any program returned by
    the server.

    .. code-block:: python

        import bricks

        @bricks.api
        def crazy_function(client, arg1, arg2, ...):
            client.alert("The server is crazy!")
            client.jquery('div').hide()
            return 42


    Using ``bricks.call()`` prevents the client code from executing.

    .. code-block:: javascript

        bricks.call('crazy-function')
            .then(function(result) {
                console.log('the answer is ' + result)
            })

    It will not hide any div or show any javascript alert.


.. js:function::
    bricks.js(api_name, {args})

    Consumes an API entry point that simply returns some javascript code and
    immediately execute it.

    In Django, functions those entry points are registered using the
    ``@bricks.rpc.js`` decorator:

    .. code-block :: python

        import bricks

        @bricks.rpc.js
        def js_maker(request, arg1, arg2, arg3, ...):
            return string_of_javascript_code()


.. js:function::
    bricks.rpc(api_name, options)

    The workhorse behind :js:func:`bricks`, :js:func:`bricks.call`,
    :js:func:`bricks.js` and :js:func:`bricks.html` functions. It receives a
    single object argument that understands the following parameters

    Args:
        api:
           Api name of the called function/program
        params:
           List of positional arguments to be passed to the calling function.
        kwargs:
           An object with all the named arguments.
        server:
           Override the default server root. Usually bricks will open the URL
           at http://<localdomain>/bricks/api-function-name.
        async:
            If true, returns a promise. Otherwise, it blocks execution and
            returns the result of the function call.
        method:
           Can be any of 'api', 'program', 'js', or 'html'.
        program:
            If true (default), execute any received programmatic instructions.
        error:
            If true (default), it will raise any exceptions raised by the remote
            call.
        result:
           If given, will determine the result value of the function call.
        timeout:
           Maximum amount of time (in seconds) to wait for a server response.
           Default to 30.0.
        converter:
            A function that process the resulting JSON result and convert it
            to the desired value.


The ``bricks.json`` module
==========================

The ``bricks.json`` module defines a few functions for handling the bricks
flavored JSON. The API was modeled after Python's json module rather than
Javascript.

Supported types
---------------

Besides regular JSON types, the js-client for bricks also implement a few
additional data types.

+---------------+-------------------+----------------+-------------------------------+
| Type name (@) | Python            | Javascript     | Notes                         |
+===============+===================+================+===============================+
| datetime      | datetime.datetime | Date           |                               |
+---------------+-------------------+----------------+-------------------------------+


.. js:function::
    bricks.json.encode(obj)

    Encode object into a bricks-flavored JSON-compatible structure.


.. js:function::
    bricks.json.decode(obj)

    Return the Javascript object equivalent to the given bricks-flavored
    JSON-compatible structure.


.. js:function::
    bricks.json.dumps(obj)

    Stringfy javascript object to a bricks-flavored JSON stream.


.. js:function::
    bricks.json.loads(String data)

    Load javascript object from a bricks-flavored JSON encoded string.
