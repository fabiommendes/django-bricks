import datetime
from markupsafe import Markup

from bricks.json import register, loads, dumps, encode, decode, JSONDecodeError, JSONEncodeError
import bricks.json.encoders
import pytest


#
# Basic usage
#
def test_encode_non_standard_object_to_json():
    assert encode({1, 2, 3}) == {'@': 'set', 'data': [1, 2, 3]}


def test_decode_non_standard_object_to_json():
    assert decode({'@': 'set', 'data': [1, 2, 3]}) == {1, 2, 3}


def test_load_object_from_string():
    assert loads('[1, 2, 3]') == [1, 2, 3]
    assert loads('{"@": "set", "data": [1, 2, 3]}') == {1, 2, 3}


def test_dumps_object_to_string():
    assert isinstance(dumps([1, 2, 3]), str)
    assert loads(dumps([1, 2, 3])) == [1, 2, 3]
    assert loads(dumps({1, 2, 3})) == {1, 2, 3}


def test_register_new_type():
    class Foo:
        def __eq__(self, other):
            return self.__dict__ == other.__dict__

    def efunc(x):
        return {'data': dict(x.__dict__)}

    def dfunc(data):
        foo = Foo()
        for k, v in data['data'].items():
            setattr(foo, k, v)
        return foo

    register(Foo, 'mod.Foo', encode=efunc, decode=dfunc)
    foo = Foo()

    assert Foo in bricks.json.encoders.CLASS_TO_NAMES
    assert encode(foo) == {'@': 'mod.Foo', 'data': {}}
    assert decode({'@': 'mod.Foo', 'data': {}}) == foo


#
# Test types
#
@pytest.fixture(params=[
    # Basic
    b'foobar',
    Markup('foo'),

    # Composite
    (1, 2, 3),
    {'foo': 1, 'bar': 2},
    {1: 2, 2: 3},
    {'@': 'x', 1: (1, 2, 3)},

    # Other types
    datetime.date(1970, 1, 1),
])
def elem(request):
    return request.param


def test_dict_encode():
    D = {'foo': 1, 'bar': 42}
    assert decode(encode(D)) == D


def test_round_trip(elem):
    assert decode(encode(elem)) == elem
#
# Test errors
#
def test_json_encoding_error():
    class FooBar:
        pass

    with pytest.raises(JSONEncodeError):
        encode(FooBar())


def test_json_decoding_error():
    with pytest.raises(JSONDecodeError):
        decode({'@': 'mod.FooBar', 'x': 1})


def test_register_error():
    class Foo:
        pass

    with pytest.raises(ValueError):
        register(Foo, 'foo-foo', encode=lambda x: None)

    with pytest.raises(ValueError):
        register(Foo, 'foo-foo', decode=lambda x: None)