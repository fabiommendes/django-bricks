Django web components
---------------------

Django-brick is a library that implements server-side web components for
your Django application. The goal is to reuse code by building simple pluggable
pieces. Think of Lego bricks for the web.

.. image:: media/legos.jpg
:alt: https://upload.wikimedia.org/wikipedia/commons/thumb/3/32/Lego_Color_Bricks.jpg/1024px-Lego_Color_Bricks.jpg

Client-side programming has plenty responses for this task: React, Polymer,
Vue.js, X-tag etc. Django Bricks tries to give a server-side alternative that
can free you from writing a lot of JavaScript and HTML ;).


Enter the brick
---------------

A brick is a Python component with a a well defined interface to present itself
for the client. Usually this means that it can render itself as HTML5 (but
sometimes we may need more complicated behaviors). Pehaps the most
simple brick that you can use is just a HTML5 tag. Django-bricks implement these
building blocks in the :mod:`bricks.html5` module. The most important action a
:class:`bricks.Tag` brick can make is to render itself as HTML:

>>> from bricks.html5 import p
>>> elem = p("Hello World!", class_='hello')

This can be converted to HTML by calling ``str()`` on the element:

>>> print(str(elem))
<p class="hello">Hello World!</p>

Python and HTML have very different semantics. HTML's syntax gravitates
around tag attributes + children nodes and does not have a very natural
counterpart in most programming languages. Of course we can build a tag in a
imperative style, but the end result often feels awkward. We introduce a
mini-language to declare HTML fragments in a more natural way:

>>> from bricks.html5 import div, p, h1
>>> fragment = \
...     div(class_="alert-box")[
...         h1('Hello Python'),
...         p('Now you can write HTML in Python!'),
...     ]

By default, bricks convert it to a very compact HTML; we insert no indentation
and only a minimum whitespace. We can pretty print the fragment using the
render function with an optional attribute:

>>> print(fragment.render(pretty=True))
<div class="alert-box">
    <h1>Hello Python</h1>
    <p>Now you can write HTML in Python!</p>
</div>

The render function can tweak the way the final markup is produced. It might
receive an optional "request" argument that custom components can use to
control how the final HTML string is produced.


Templating
----------

The goal of ``bricks.html5`` is to replace your template engine by Python code
that generates HTML fragments. This approach removes the constraints imposed by
the template language and makes integration with surrounding Python code trivial.

I know what you are thinking: *"it is a really bad idea to mix template with
logic"*. Bricks obviously don't prevents you from shooting yourself on the foot
and you can make really messy code if you want. However, things can be very
smooth if you stick to focused and simple components that adopt a more
functional style.

Our advice is: *break your code in small pieces and compose these pieces in
simple and predictable ways*. Incidentally, this is a good advice for any form
of code ;).

The fact is that our good old friend "a function" is probably simpler to use
and composes much better than anything your templating engine has come up with.
Let us dive in!

We want to do a little bootstrap element that show a menu with actions (this is
a random example taken from Bootstrap website).

.. code-block:: html

    <div class="btn-group">
      <button type="button"
              class="btn btn-default dropdown-toggle"
              data-toggle="dropdown"
              aria-haspopup="true"
              aria-expanded="false">
        Action <span class="caret"></span>
      </button>
      <ul class="dropdown-menu">
        <li><a href="#">Action</a></li>
        <li><a href="#">Another action</a></li>
        <li><a href="#">Something else here</a></li>
        <li role="separator" class="divider"></li>
        <li><a href="#">Separated link</a></li>
      </ul>
    </div>

Of course we could translate this directly into bricks code by calling the
right ``div()``'s, ``button()``'s, etc. But first, let us break up this mess
into smaller pieces.

.. code-block:: python

    from bricks.html5 import button, div, p, ul, li, span

    def menu_button(name, caret=True):
        return \
            button(type='button',
                   class_='btn btn-default dropdown-toggle',
                   data_toggle="dropdown",
                   aria_haspopup="true",
                   aria-expanded="false")[
                name,
                span(class_='caret') if caret else None,  # Nones are ignored
            ]

Ok, it looks more trouble. But now we can reuse this piece and easily make as
many buttons as we like: ``menu_button('File'), menu_button('Edit'), ...``.
The next step is to create a function that takes a list of strings and return
the corresponding menu (in the real world we might also want to control the href
attribute). We are also going to be clever and use the Ellipsis (``...``) as
a menu separator.

.. code-block:: python

    def menu_data(values):
        def do_item(x):
            if x is ...:
                return li(role='separator', class='divider')
            else:
                # this could parse the href from string, or take a tuple
                # input, or whatever you like.
                return li[a(href='#')[x]]

        return \
            ul(class_='dropdown-menu')[
                map(do_item, values)
            ]

And we glue both together...

.. code-block:: python

    def menu(name, values, caret=True):
        return \
            div(class_='btn-group')[
                menu_button(name, caret=True),
                menu_data(values),
            ]

and start creating as many new menu buttons as we like:

.. code-block:: python

    menubar = \
        div(id='menubar')[
            menu('File', ['New', 'Open', ..., 'Exit']),
            menu('Edit', ['Copy', 'Paste', ..., 'Preferences']),
            menu('Help', ['Manual', 'Topics', ..., 'About']),
        ]

Look how nice it is in the end :)

The with statement
------------------

If you have more complex logic the "with" syntax can be handy.

>>> with div(class_='card') as fragment:
...     +h1('Multi-hello')
...     for i in range(1, 4):
...         +p('hello %s' % i)
>>> print(fragment.render(pretty=True))
<div class="card">
    <h1>Multi-hello</h1>
    <p>hello 1</p>
    <p>hello 2</p>
    <p>hello 3</p>
</div>

The unary + operator says *"add me to the node defined in the last with
statement"*.


.. disabled
|The most simple interface a Brick object can expose is to render itself as HTML.
|All bricks should define a `.render(request)` method that renders the brick as
|an HTML string:
|
|>>> bricks.request import FakeRequest
|>>> request = FakeRequest()
|>>> doc.render(request)
|'<div class="foo"><h1>Hello World</h1><p>This is a simple HTML fragment written in Python!</p></div>'
|
|In Django, this is accomplished by a template filter:
|
|.. code-block:: html
|
|    <html>
|    <body>
|        {{ doc|render }}
|    </body>
|    </html>
|
|
|:class:`bricks.Tag` objects may use a declarative syntax more similar to HTML
|
|
|.. comment
|    Srvice is a library that aims to integrate a Python server with a Javascript
|    client via remote calls. With Srvice, the client can transparently call
|    functions defined in server. The server might also respond with instructions
|    that execute arbitrary Javascript code in the client.
|
|    Let us define a function in the client:
|
|    .. code-block:: python
|
|        from import srvice
|
|        @srvice.api
|        def get_user_email(request, username):
|            if can_read_email(request.user, username):
|                return email_from_username(username)
|            else:
|                raise PermissionError
|
|        # This function must be associated with some url in your application
|        urlpatterns [
|            ...,
|            '^get-user-email/$', get_user_email.as_view(),
|        ]
|
|
|    In the client, we call the function defined in the some URL point using the
|    srvice object:
|
|    .. code-block:: javascript
|
|        srvice.call('get-user-email', 'paulmcartney').then(function (email) {
|            var contact = currentContact();
|            contact.email = email;
|        })
|
|
|    Communication is done using JSON strings that pass function arguments and
|    results from client to server and vice-versa.
|
|    This is only the very basic that Srvice can do. Please check the documentation
|    for more information.
|