import base64
import collections
import datetime
import json as _json
import numbers

from markupsafe import Markup

from bricks.json.util import normalize_class_name
from .decoders import decode, register as register_decode
from .encoders import encode, register as register_encode


def register(cls, name=None, encode=None, decode=None):
    """
    Register encode/decode pair of functions for the given Python type.
    Registration extends Bricks flavored JSON to handle arbitrary python
    objects.

    Args:
        cls:
            python data type
        name:
            name associated with the '@' when encoded to JSON.
        encode:
            the encode function; convert object to JSON. The resulting JSON can
            have non-valid JSON types as long as they can be also converted
            to JSON using the :func:`bricks.json.encode` function.
        decode:
            decode function; converts JSON back to Python. The decode function
            might assume that all elements were already converted to their most
            Pythonic forms (i.e., all dictionaries with an '@' key were already
            decoded to their Python forms).

    See also:
        :ref:`json-custom-types`
    """

    name = normalize_class_name(cls, name)

    if (encode is None and decode is not None or
            decode is None and encode is not None):
        raise ValueError('encoder and decoder must be given')

    if encode is None:
        def decorator(func):
            def decode(dec_func):
                register_decode(cls, name, dec_func)
                return dec_func
            func.register_decoder = decode
            register_encode(cls, name, func)
            return func

        return decorator

    register_decode(cls, name, decode)
    register_encode(cls, name, encode)


def loads(data):
    """
    Load a string of JSON-encoded data and return the corresponding Python
    object.
    """

    return decode(_json.loads(data))


def dumps(obj):
    """
    Return a JSON string dump of a Python object.
    """

    return _json.dumps(encode(obj))


#
# Python builtin types
#
@register(bytes)
def encode_bytes(data):
    data = base64.b64encode(data).decode('ascii')
    return {'@': 'bytes', 'data': data}


@encode_bytes.register_decoder
def decode_bytes(data):
    data = data['data'].encode('ascii')
    return base64.b64decode(data)


@register(set)
def encode_set(data):
    return {'data': list(data)}


@encode_set.register_decoder
def decode_set(data):
    return set(data['data'])


@register(tuple)
def encode_tuple(data):
    return {'data': list(data)}


@encode_tuple.register_decoder
def decode_tuple(data):
    return tuple(data['data'])


@register(list)
def encode_list(data):
    return [encode(x) for x in data]



# Dictionaries need special treatment because we want to be able to serialize
# dictionaries with non-string key. Dictioaries with an '@' must also be
# supported
@register(dict, 'dict')
def encode_dict(data):
    if '@' in data or not all(isinstance(k, str) for k in data.keys()):
        result = {'data': [[decode(k), decode(v)] for (k, v) in data.items()]}
        result['@'] = 'dict'
        return result
    return {k: decode(v) for (k, v) in data.items()}


@encode_dict.register_decoder
def decode_dict(data):
    return dict(decode(x) for x in data['data'])


#
# Common Python types (not builtins)
#
@register(datetime.date, 'date')
def encode_datetime(date):
    return {
        '@': 'date',
        'year': date.year,
        'month': date.month,
        'day': date.day
    }


@encode_datetime.register_decoder
def decode_datetime(data):
    return datetime.date(data['year'], data['month'], data['day'])



#
# Contrib types (not on standard lib)
#
@register(Markup, 'markup')
def encode_markup(x):
    return {'data': str(x)}


@encode_markup.register_decoder
def decode_markup(x):
    return Markup(x['data'])

