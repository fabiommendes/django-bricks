====
PyML
====

PyML is a format to write HTML documents and web components in Python using
objects instead of senseless HTML string manipulations. It serves a more
sophisticated purpose than a template language such as Jinja2 or Mako by
coordinating components, their dependencies, and representations in various
formats (where HTML is just one of them). At some point, PyML + srvice can be
used as a mix of Python + Javascript proto-framework.

Basic syntax
============

Consider a very basic HTML5 document

.. code-block:: html

    <!DOCTYPE html>
    <html>
      <head>
        <title>Hello HTML!</title>
      </head>

      <body>
        <h1 class="main-title">HTML Demo</h1>
        <p>Hello <em>World!</em></p>
      </body>
    </html>

HTML uses tags for defining both the macro document structure and lower level
text formats such as emphasis, bold text, superscripts, subscripts, etc. Usually,
PyML should concern only with structural tags, so the above example could
be translated as:

.. code-block:: python

    from bricks.tags import *

    document = \
        document [
            head [
                title("Hello HTML!"),
            ],
            body [
                h1("HTML Demo", cls="main-title"),
                p(html="Hello <em>World!</em>"),
            ],
        ]

    print(document)  # prints document as HTML!


Basically, HTML tags become Python objects that use square brackets for
delimiting blocks. If your tag define attributes and child nodes, use a function
call followed by square brackets:

.. code-block:: python

    element = \
        div(cls="contact-card") [
            span("john", cls="contact-name"),
            span("555-1234", cls="contact-phone"),
        ]

This translates to

.. code-block:: html

    <div class="contact-card">
        <span class="contact-name">John</span>
        <span class="contact-phone">555-1234</span>
    </div>

Tag attributes are defined with Python's call-by-name syntax. We can specify any
attribute of an element using ``div(id="main-nav")[...]``. Usually both the
Python and the HTML attributes will have the same names, but due to discrepancies
between Python and HTML, we have to make a few adjustments. PyML assumes properties
always use dashes instead of underscores to split words, so ``data-type="contact"``
in HTML becomes ``data_type="contact"`` in Python. Besides that, HTML attributes
might also correspond to Python keywords, which cannot be used as variable names.
We treat "class" attribute to be synonym to "cls", but in general a trailing
underscore is simply ignored so ``label("foo", for_="id-bar")`` becomes
``<label for="id-bar">foo</label>``.


.. this is disabled now
    Context managers
    ----------------

    Tags can also be defined using ``with`` clauses. This is useful to mix Python
    code that generates elements programatically:


    .. code-block:: python

        with div(id="nav-bar") as element:
            for link in links:
                a(link.title, href=link.address)

    The resulting HTML is similar to this:

    .. code-block:: html

        <div id="nav-bar">
            <a href="address-1">Title-1</a>
            <a href="address-2">Title-2</a>
            <a href="address-3">Title-3</a>
            ...
        </div>

    All tags inside a ``with`` block have an implicit parent element. We can set a
    different parent explicitly, but it breaks the natural use of indentation to
    denote the document structure::

        with article as element:
            with div as block:
                h1('title', parent=element)
                p('some paragraph')

    The h1 element will be a direct child of ``<article>``, instead of ``<div>``.
    The final HTML will be

    .. code-block:: html

        <article>
            <div>
                <p>some paragraph</p>
            </div>
            <h1>title</h1>
        </article>

    Of course this kind of use is confusing and should be avoided.


How does it work?
-----------------

PyML is obviously just regular Python, so how can these syntax extensions work?
Take the example::

    element = \
        div(cls="contact-card") [
            span("john", cls="contact-name"),
            span("555-1234", cls="contact-phone"),
        ]

This element could be created in a more regular imperative fashion::

    element = div(cls="contact-card")
    span1 = span("john", cls="contact-name")
    span2 = span("555-1234", cls="contact-phone")
    element.add_children([span1, span2])

This is not as expressive as the first case and forces us to think *imperative*
instead of thinking in *declarative markup*, which is not very useful in web development.
The "square bracket syntax" is in fact just regular Python indexing syntax
abused to call the ``.add_children`` method to insert child elements to a tag.

The source of :class:`pyml.Component` (the base class for all tags), looks
something like this::

    class Component:
        # ... many other methods ...

        def __getitem__(self, children):
            self.add_children(children)
            return self

In reality, things are a little more complicated, and we have to override the
``__getitem__()`` method of both Component and its metaclass to make tags without
attributes work too.


From tags to components
=======================

Until now, PyML works just as a templating language, not very different from Jade,
Jinja or Mako. It has the advantage of being pure Python, so it is very easy to
integrate with your server-side application. It also means that the syntax can
be a little awkward at times since we are much more limited in terms of syntax
than specialized markup languages. PyML is also restricted to HTML, while many
template languages can easily handle any kind of textual data.

So lets say you defined a Contact component that exhibits contact info:

.. TODO: disabled code-block:: python
    class Contact(BlockElement):
        def __init__(self, name, phone, email, **kwargs):
            super().__init__(**kwargs)
            self.name = name
            self.phone = phone
            self.email = email

        def content(self):
            return [
                p(cls='contact--name')[
                    label('Name'), span(self.name),
                ],
                p(cls='contact--phone')[
                    label('Phone'), span(self.phone),
                ],
                p(cls='contact--email')[
                    label('E-mail'), span(self.email),
                ]
            ]


This will create a nice contact card similar to this

.. code-block:: html

    <div class="contact">
        <p><label>Name</label><span>Guido van Russom</span></p>
        <p><label>Phone</label><span>555 1234</span></p>
        <p><label>E-mail</label><span>guido@python.org</span></p>
    </div>

In most cases, we might also want to define some Css and Javascript and
associate it with the component. This could be done during class creation using
the static_media dictionary


.. TODO: disabled code-block:: python
    class Contact(BlockElement):
        static_media = {
            'contact.js': js(),
            'contact.css': css({
                'self': {
                    'font-family': 'Comic Sans',
                    'font-size': '1.1em',
                    'padding': '20px',
                }
            }),
        }


        ...


PyML is a language to build pluggable *web components*.


Assets
======

A web component is a bundle of HTML, JavaScript, CSS and possibly other assets
such as images, fonts, sounds etc. Usually the entry point of a web component
is its HTML part, although many modern frameworks are now migrating to pages
written entirely in Javascript. PyML assumes the former: we declare and register
a web component inside a HTML page. This page should load all resources and
dependencies required to run the component. This usually means loading some
JavaScript files, CSS, images, fonts and so on. PyML defines an interface that
components can expose these dependencies in an practical way.






