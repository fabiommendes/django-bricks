from .components.html5_tags import *  # noqa
from .components.text import Text, html  # noqa
from .components import html5_tags as tags


def a_or_p(*args, href=None, **kwargs):
    """
    Return a or p tag depending if href is defined or not.
    """

    if href:
        return tags.a(*args, href=href, **kwargs)
    else:
        return tags.p(*args, href=href, **kwargs)


def a_or_span(*args, href=None, **kwargs):
    """
    Return a or span tag depending if href is defined or not.
    """

    if href:
        return tags.a(*args, href=href, **kwargs)
    else:
        return tags.span(*args, href=href, **kwargs)
