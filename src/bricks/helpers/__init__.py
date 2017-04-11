"""
Helper functions generate safe HTML code fragments for several useful
situations.

Rendering
---------

.. autofunction:: bricks.helpers.render
.. autofunction:: bricks.helpers.render_tag
.. autofunction:: bricks.helpers.markdown

Escaping
--------

.. autofunction:: bricks.helpers.safe
.. autofunction:: bricks.helpers.escape
.. autofunction:: bricks.helpers.escape_silent
.. autofunction:: bricks.helpers.unescape
.. autofunction:: bricks.helpers.sanitize


Utilities
---------

.. autofunction:: bricks.helpers.attr
.. autofunction:: bricks.helpers.attrs
.. autofunction:: bricks.helpers.hyperlink
"""

from .escape import safe, escape, escape_silent, unescape, sanitize
from .attr import attr, attrs
from .hyperlink import hyperlink
from .render import render
from .extras import render_tag, markdown
