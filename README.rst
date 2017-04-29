.. image:: https://readthedocs.org/projects/bricks/badge/?version=latest
    :target: http://bricks.readthedocs.io/en/latest/?badge=latest
    :alt: Documentation Status
.. image:: https://travis-ci.org/fabiommendes/django-bricks.svg?branch=master
    :target: https://travis-ci.org/fabiommendes/django-bricks
    :alt: Build status
.. image:: https://codeclimate.com/github/fabiommendes/django-bricks/badges/gpa.svg
    :target: https://codeclimate.com/github/fabiommendes/django-bricks
    :alt: Code Climate
.. image:: https://codecov.io/gh/fabiommendes/django-bricks/branch/master/graph/badge.svg
    :target: https://codecov.io/gh/fabiommendes/django-bricks
    :alt: Code coverage
.. image:: https://www.quantifiedcode.com/api/v1/project/ee91ade50a344c87ac99638670c76580/badge.svg
    :target: https://www.quantifiedcode.com/app/project/ee91ade50a344c87ac99638670c76580
    :alt: Code issues


Django web components
---------------------

Django-brick is a library that implements server-side web components for
your Django application. The goal is to reuse code by building simple pluggable
pieces. Think of Lego bricks for the web.

.. image:: media/legos.jpg
:alt: https://upload.wikimedia.org/wikipedia/commons/thumb/3/32/Lego_Color_Bricks.jpg/1024px-Lego_Color_Bricks.jpg

Client-side programming has plenty responses for this task: React, Polymer,
Vue.js, X-tag etc. Django Bricks provides a server-side alternative that
can free you from writing some JavaScript and HTML ;).


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
``.pretty`` method:

>>> print(fragment.pretty())
<div class="alert-box">
  <h1>Hello Python</h1>
  <p>Now you can write HTML in Python!</p>
</div>

This is useful for debugging but, it is recommend to never output prettified
HTML in production. This just stresses the rendering engine and produces larger
files for no real gain for our end users and developers.
