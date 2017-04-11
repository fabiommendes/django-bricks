import collections
import re

from . import safe
from bricks.json import dumps as json_dump
from bricks.utils import lazy_singledispatch

SAFE_ATTRIBUTE_NAME = re.compile(r'^[^\s\=\<\>\&\"\']+$')


@lazy_singledispatch
def attr(x, **kwargs):
    """
    Renders object as an HTML attribute value.

    It define the following dispatch rules:

    str:
        Quotations and & are escaped, any other content, including <, >, is
        allowed.
    numeric types:
        Are simply converted to strings.
    lists and mappings:
        Are converted to JSON and returned as safe strings. This is used in
        some modern javascript frameworks reads JSON from tag attributes.

    """
    raise TypeError('%s objects are not supported' % x.__class__.__name__)


@attr.register(bytes)
def _(x):
    raise TypeError('%s objects are not supported' % x.__class__.__name__)


@attr.register(str)
def _(x):
    return x.replace('&', '&amp;').replace('"', '&quot;')


# Register numeric types and all trivial conversions
for _tt in [int, float, complex, 'decimal.Decimal']:
    attr.register(_tt, str)


# JSON conversions
@attr.register(collections.Sequence)
@attr.register(collections.Mapping)
def _(x, **kwargs):
    return attr(json_dump(x, **kwargs))


def html_natural_attr(x):
    """
    Convert string to a natural HTML attribute or tag name.

    This function replaces underscores by dashes.
    """
    return x.rstrip('_').replace('_', '-')


def html_safe_natural_attr(x):
    """
    Convert string to html natural name and check if the resulting string is
    valid.
    """
    return check_html_safe_name(html_natural_attr(x))


def check_html_safe_name(x):
    """
    Raises a ValueError if string is not a valid html attribute or tag name.
    """

    if not SAFE_ATTRIBUTE_NAME.match(x):
        raise ValueError('invalid html attribute name: %r' % x)
    return x


@lazy_singledispatch
def attrs(x, **kwargs):
    """
    Convert object into a list of key-value HTML attributes.

    Args:
        It uses multiple dispatch, so the behaviour might differ a little bit
        depending o the first argument.

        mappings:
            Renders key-values into the corresponding HTML results.
        sequences:
            Any non-string sequence is treated as sequence of (key, value)
            pairs. If any repeated keys are found, it keeps only the last value.
        *attrs* protocol:
            Any object that define an ``attrs`` attribute that can be either a
            mapping or a sequence of pairs.

        In all cases, ``attrs`` takes arbitrary keyword attributes that are
        interpreted as additional attributes. PyML converts all underscores
        present in the attribute names to dashes since this is the most common
        convention in HTML.
    """

    try:
        data = x.attrs
    except AttributeError:
        raise TypeError('%s objects are not supported' % x.__class__.__name__)
    else:
        return attrs(data)


@attrs.register(type(None))
def _(none, **kwargs):
    return _attrs_maping({}, **kwargs)


@attrs.register(collections.Mapping)
def _attrs_maping(map, **kwargs):
    if kwargs:
        kwargs = {html_natural_attr(k): v for k, v in kwargs.items()}
        map = collections.OrderedDict(map, **kwargs)
    elems = []
    for k, v in map.items():
        if v is False or v is None:
            continue
        elif v is True:
            elems.append(k)
        else:
            elems.append('%s="%s"' % (k, attr(v)))
    return safe(' '.join(elems))


@attrs.register(collections.Sequence)
def _(map, **kwargs):
    if isinstance(map, (str, bytes)):
        raise TypeError('strings are not supported')
    return _attrs_maping(collections.OrderedDict(map), **kwargs)
