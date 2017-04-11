Django web components
---------------------

Django-brick is a library that implements web components at server-side for
your Django application. The goal is to reuse code by building simple pluggable
pieces, think of Lego bricks for the web.

.. image:: media/legos.jpg
   :alt: https://upload.wikimedia.org/wikipedia/commons/thumb/3/32/Lego_Color_Bricks.jpg/1024px-Lego_Color_Bricks.jpg

Client-side has plenty responses: think of JavaScript libraries
such as ReacJS, Polymer, Vue.js, X-tag etc. Django Bricks tries to give a
server-side alternative that can free you from writing a lot of JavaScript ;).

Enter the brick
---------------

A brick is a Python component with a a well defined interface to present itself
to the client. Usually this means that it can render itself as
HTML5 (but sometimes we may need more complicated behaviors). Pehaps the most
simple brick that you can use is just a HTML5 tag. Django-bricks implement these
building blocks in the :mod:`bricks.tags` module. The most important action a
:class:`bricks.Tag` brick can make is to render itself as HTML:

>>> from bricks import tags
>>> print(tags.p("Hello World!", class_='hello'))
<p class="hello">Hello World!</p>

Python and HTML have very different semantics. Indeed, HTML's syntax gravitates around
tag attributes + children nodes and does not have a very natural counterpart in most
programming languages. Of course we can build a tag in a imperative style,
but the end result often feels awkward. We introduce a mini-language to declare
HTML fragments in a much more natural way:

>>> from bricks.tags import div, p, h1
>>> doc = \
...     div(class_='foo')[
...         h1('Hello World'),
...         p('This is a simple HTML fragment written in Python!'),
...     ]

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