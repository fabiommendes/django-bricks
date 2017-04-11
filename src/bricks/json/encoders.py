#
# JSON encode: convert Python types to JSON structures.
#
from functools import singledispatch

from bricks.json.util import normalize_class_name
from .exceptions import JSONEncodeError

NoneType = type(None)
CLASS_TO_NAMES = {
    dict: 'dict',
}


def register(cls, name=None, func=None):
    """
    Register an encoding function for the given class.
    """

    name = normalize_class_name(cls, name)
    CLASS_TO_NAMES[cls] = name
    _encode_single_dispatch.register(cls)(func)


def encode(data):
    """
    Encode some arbitrary Python data into a JSON-compatible structure.

    This naive implementation does not handle recursive structures. This might
    change in the future.

    This function encode subclasses of registered types as if they belong to
    the base class. This is convenient, but is potentially fragile and make
    the operation non-invertible.
    """

    cls = data.__class__
    if cls in {int, float, str, bool, NoneType}:
        return data

    try:
        json = _encode_single_dispatch(data)
    except TypeError as ex:
        raise JSONEncodeError(str(ex))
    if (isinstance(json, dict) and
                '@' not in json and
            not isinstance(data, dict)):
        json['@'] = CLASS_TO_NAMES[type(data)]
    return json


@singledispatch
def _encode_single_dispatch(data):
    type_name = type(data).__name__
    raise TypeError('could not encode %s object: %s' % (type(data), type_name))


encode.register = register
