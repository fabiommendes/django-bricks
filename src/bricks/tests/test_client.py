import pytest

from bricks.js.client import Client, js_compile


@pytest.fixture
def client():
    return Client(None)


def test_client_simple_function(client):
    client.alert('hello')
    assert js_compile(client) == "alert('hello');"


def test_client_namespace(client):
    client.console.log('hello')
    assert js_compile(client) == "console.log('hello');"


def test_client_args(client):
    client.func('a', 42, None, True, False)
    assert js_compile(client) == "var __v1 = func('a', 42, null, true, false);"


def test_client_js(client):
    js = "function f(x) {return x * x}"
    client.js(js)
    assert js_compile(client) == js


def test_client_error(client):
    client.error(TypeError('x is not an integer'))
    client.error(TypeError, message='x is not an integer')
    client.error('Error', message='x is not an integer')

    assert js_compile(client) == "throw TypeError('x is not an integer');\n" \
                                 "throw TypeError('x is not an integer');\n" \
                                 "throw Error('x is not an integer');"


def test_chain(client):
    client.srvice('foo', 1, 2, 3)\
        .then(client.function('x')[
           'alert(x)'
        ])
    assert js_compile(client) == "var __v1 = srvice('foo', 1, 2, 3);\n"\
                                 "var __v2 = __v1.then(function(x) {\n" \
                                 "    alert(x);\n" \
                                 "});"


def test_dialog(client):
    client.dialog(html='Hello world!')
    assert js_compile(client) == "var __v1 = srvice.dialog({"\
                                 "html: 'Hello world!'});"
