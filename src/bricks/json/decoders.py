#
# JSON decode: convert JSON structures to Python objects.
#
import datetime

from bricks.json.util import normalize_class_name
from .exceptions import JSONDecodeError

NoneType = type(None)
CLASSNAME_TO_DECODER = {}


#
# Registration and basic APIs
#
def decode(data):
    """
    Decode a JSON-like structure into the corresponding Python data.
    """

    if isinstance(data, dict):
        if '@' in data:
            data_type = data['@']
            try:
                decoder = CLASSNAME_TO_DECODER[data_type]
            except KeyError:
                msg = 'invalid type: {"@": "%s", ...}' % data_type
                raise JSONDecodeError(msg)
            return decoder({k: v for (k, v) in data.items() if k != '@'})
    return data


def register(cls, name=None, func=None):
    """
    Decorator that register decoding functions.
    """

    name = normalize_class_name(cls, name)
    CLASSNAME_TO_DECODER[name] = func


decode.register = register
