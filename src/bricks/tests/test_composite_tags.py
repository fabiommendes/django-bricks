from pprint import pprint

import pytest

from bricks.components import Text
from bricks.components.html5_tags import div, h1, p, a
from bricks.helpers import safe


def test_nested_is_in_children():
    tag1 = div('foo')
    tag2 = div(tag1, cls='bar')
    assert tag1 in tag2.children


def test_json_conversion():
    tag = div(class_='foo')[
        h1('bar'),
        safe('foo <b>bar</b>')
    ]
    pprint(tag.json())
    assert tag.json() == {
        'tag': 'div',
        'classes': ['foo'],
        'children': [
            {
                'tag': 'h1',
                'children': [{'tag': 'text', 'text': 'bar'}]
                },
            {'tag': 'text', 'text': 'foo <b>bar</b>'},
        ]
    }


def test_simple_tag_with_content():
    tag = div('foo', class_='title')
    assert tag.render(None) == '<div class="title">foo</div>'


def test_nested_tags():
    tag = div(class_='title')[
        h1('foobar'),
        a('bar', href='foo/')
    ]
    html = tag.render(None)
    assert html == '<div class="title"><h1>foobar</h1><a href="foo/">bar</a></div>'


def test_create_tag_with_single_child():
    tag = p['foo']
    assert tag.render(None) == '<p>foo</p>'

    tag = p(class_='bar')['foo']
    assert tag.render(None) == '<p class="bar">foo</p>'


def test_tag_representation():
    assert repr(p()) == 'p()'
    assert repr(p(class_='foo')) == "p(class_='foo')"
    assert repr(div[p, p('foo')]) == 'div([p(), p(\'foo\')])'


def test_tag_str_representation():
    assert str(p()) == '<p></p>'
    assert str(div[p, p('foo')]) == '<div><p></p><p>foo</p></div>'


def test_element_equality():
    assert Text('foo') == Text('foo')
    assert p['foo'] == p['foo']


def test_classes_and_props_effect_on_equality_tests():
    assert p(class_='foo')['foo'] != p['foo']
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
