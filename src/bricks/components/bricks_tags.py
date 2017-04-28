"""
These are helper "tags" defined by bricks. All these tags are exposed in the
toplevel bricks.html5 module.
"""

from . import html5_tags as _tag
from ..helpers.hyperlink import parse_link as _parse_link


def link(name, href=None, **kwargs):
    """
    Creates an anchor by parsing the input string looking for a link if ``href``
    is not defined.

    Examples:
       >>> str(link('Python<https://python.org>'))
       <a href="https://python.org">Python</a>
    """
    if href is None:
        name, href = _parse_link(name)
    return _tag.a(name, href=href or '#', **kwargs)
