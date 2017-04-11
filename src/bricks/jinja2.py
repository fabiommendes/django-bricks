"""
Functions that help define a Bricks flavored Jinja2 environment.
"""

import functools

from jinja2 import contextfilter, contextfunction

from bricks.helpers import attrs, render, hyperlink, render_tag


def pyml_request(func):
    """
    A decorator that passes a request keyword argument for the rendering
    function.
    """

    def decorated(ctx, obj, *args, **kwargs):
        kwargs['request'] = ctx.get('request', None)
        return func(obj, *args, **kwargs)
    return functools.wraps(func)(decorated)

env_filters = {
    'attrs': attrs,
    'render': contextfilter(pyml_request(render)),
    'hyperlink': hyperlink,
}

env_globals = {
    'attrs': attrs,
    'hyperlink': hyperlink,
    'tag': contextfunction(pyml_request(render_tag)),
    'render': contextfunction(pyml_request(render)),
}
