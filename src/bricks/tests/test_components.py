import pytest

from bricks.components.tags import *


@pytest.fixture
def tag():
    return a(cls='foo bar', id='me')['click me']


def test_attr_access(tag):
    assert tag.attrs['id'] == 'me'
    assert tag.attrs['class'] == 'foo bar'


def test_add_attrs(tag):
    tag.attrs['foo-bar'] = 'baz'
    assert tag.attrs.to_dict() == {'class': 'foo bar', 'id': 'me',
                                   'foo-bar': 'baz'}
    assert sorted(tag.attrs) == ['class', 'foo-bar', 'id']
    assert len(tag.attrs) == 3


def test_deleting_attrs(tag):
    with pytest.raises(KeyError):
        del tag.attrs['class']
    with pytest.raises(KeyError):
        del tag.attrs['id']

    tag.attrs['foo-bar'] = 'baz'
    del tag.attrs['foo-bar']
    assert len(tag.attrs) == 2


def test_attrs_to_dict(tag):
    assert tag.attrs.to_dict(attrs={'foo-bar': 'baz'}) == {
        'class': 'foo bar', 'id': 'me', 'foo-bar': 'baz'
    }