import collections
from html import escape

from .attr import attrs as _attrs
from .escape import safe, Markup
from ..utils import lazy_singledispatch


@lazy_singledispatch
def hyperlink(x, href=None, attrs=None, **kwargs):
    """
    Creates an hyperlink string from object and renders it as an <a> tag.

    It implements some common use cases:
        str:
            Renders string as content inside the <a>...</a> tags. Additional
            options including href can be passed as keyword arguments. If no
            href is given, it tries to parse a string of "Value <link>" and
            uses href='#' if no link is found.

        dict or mapping:
            Most keys are interpreted as attributes. The visible content of
            the link must be stored in the 'content' key:

            >>> hyperlink({'href': 'www.python.com', 'content': 'Python'})
            <a href="www.python.com">Python</a>

        django User:
            You must monkey-patch to define get_absolute_url() function.
            This function uses this result as the href field.

            The full name of the user is used as the hyperlink content.

            >>> hyperlink(User(first_name='Joe', username='joe123'))
            <a href="/users/joe123">Joe</a>


    In order to support other types, use the lazy_singledispatch mechanism::

        @hyperlink.register(MyFancyType)
        def _(x, **kwargs):
            return safe(render_object_as_safe_html(x))


    See Also:

        :func:`pyml.helpers.attrs`: See this function for an exact explanation
            of how keyword arguments are translated into HTML attributes.
    """

    raise TypeError('type not supported: %s' % x.__class__.__name__)


@hyperlink.register(Markup)
def _hyperlink_markup(x, href=None, attrs=None, **kwargs):
    if href is None:
        x, href = parse_link(x)
    if href:
        kwargs['href'] = href
    attrs_string = _attrs(attrs, **kwargs)
    if attrs_string:
        attrs_string = ' ' + attrs_string
    return safe('<a%s>%s</a>' % (attrs_string, x))


@hyperlink.register(str)
def _(x, href=None, attrs=None, **kwargs):
    if href is None:
        x, href = parse_link(x)
    return _hyperlink_markup(escape(x), href, attrs, **kwargs)


@hyperlink.register(collections.Mapping)
def _(x, href=None, attrs=None, **kwargs):
    data = dict(x)
    content = data.pop('content', '')
    if attrs:
        data.update(attrs)
    attrs_string = _attrs(data, **kwargs)
    if attrs_string:
        attrs_string = ' ' + attrs_string
    return safe('<a%s>%s</a>' % (attrs_string, content))


@hyperlink.register('django.db.models.Model')
def _(x):
    return safe('<a href="%s">%s</a>' % (x.get_absolute_url(), x))


def parse_link(name):
    """
    Return a tuple with (name, link) from a string of "name<link>".

    If no link is found, the second value is None.
    """

    if name.endswith('>'):
        name, sep, link = name.partition('<')
        if sep:
            return name, link[:-1]
    return name, None
