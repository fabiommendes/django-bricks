from bricks.helpers import attrs as _attrs
from bricks.helpers import render, safe


def render_tag(tag, data=None, attrs=None, children_kwargs=None, request=None,
               **attrs_kwargs):
    """
    Renders HTML tag.

    Args:
        tag:
            Tag name.
        data:
            Children elements for the given tag. Each element is rendered with
            the render_html() function.
        attrs:
            A dictionary of attributes.
        request:
            A request object that is passed to the render function when it is
            applied to children.
        **attr_kwargs:
            Keyword arguments are converted to additional attributes.

    Examples:
        >>> render_tag('a', 'Click me!', href='www.python.org')
        '<a href="www.python.org">Click me!</a>
    """

    if data is None:
        data = ''
    children_kwargs = children_kwargs or {}
    data = render(data, request=request, **children_kwargs)
    attrs = _attrs(attrs, **attrs_kwargs)
    if attrs:
        attrs = safe(' ') + attrs
    return safe('<%s%s>%s</%s>' % (tag, attrs, data, tag))


def markdown(text, *, output_format='html5', **kwargs):
    """
    Renders Markdown content as HTML and return as a safe string.
    """

    from markdown import markdown

    return safe(markdown(text, output_format=output_format, **kwargs))
