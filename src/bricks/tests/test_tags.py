from pprint import pprint

import pytest

from bricks.components import Text
from bricks.components.tags import *
from bricks.helpers import safe
from bricks.request import request as request_factory


@pytest.fixture
def request():
    return request_factory()


def test_nested_tag_sets_parent():
    tag1 = div('foo')
    assert tag1.parent is None
    tag2 = div(tag1, cls='bar')
    assert tag1.parent is tag2


def test_json_conversion():
    tag = div(cls='foo')[
        h1('bar'),
        safe('foo <b>bar</b>')
    ]
    pprint(tag.json())
    assert tag.json() == {
        'tag': 'div',
        'classes': ['foo'],
        'children': [
            {'tag': 'h1',
             'children': [{'tag': 'text', 'text': 'bar'}]},
            {'tag': 'text', 'text': 'foo <b>bar</b>'},
        ]
    }


def test_simple_tag_without_context_manager(request):
    tag = div('foo', cls='title')
    assert tag.render(request) == '<div class="title">foo</div>'


def test_nested_tag_without_context_manager(request):
    tag = div(cls='title')[
        h1('foobar'),
        a('bar', href='foo/')
    ]
    html = tag.render(request)
    assert html == '<div class="title"><h1>foobar</h1><a href="foo/">bar</a></div>'


def test_create_tag_with_single_child(request):
    tag = p['foo']
    assert tag.render(request) == '<p>foo</p>'

    tag = p(cls='bar')['foo']
    assert tag.render(request) == '<p class="bar">foo</p>'


def test_tag_representation():
    assert repr(p()) == '<p object>'


def test_element_equality():
    assert Text('foo') == Text('foo')
    assert p['foo'] == p['foo']


def test_classes_and_props_effect_on_equality_tests():
    assert p(cls='foo')['foo'] != p['foo']
    assert p(my_prop='bar')['foo'] != p['foo']


def test_children_effect_on_equality_tests():
    a, b = p['foo', 'bar'], p['bar', 'foo']
    assert a.children != b.children
    assert a != b


def test_copy_is_equal_to_original():
    root = div[p['foo']]
    tag = root.children[0]
    assert root == root.copy()
    assert tag == tag.copy()


def test_children_behaves_as_list():
    children = p['foo', 'bar', 'baz'].children
    assert len(children) == 3
    assert children[0] == 'foo'
    assert children[1] == 'bar'
    assert children[2] == 'baz'
    assert len(list(children)) == 3
