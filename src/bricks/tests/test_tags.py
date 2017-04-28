import pytest

from bricks.components.html5_tags import a, div


class TestSimpleTagAttrsOperations:
    """
    Tests for a single tag object.
    """

    @pytest.fixture
    def a(self):
        return a(class_='cls1 cls2', id='id', href='url')['click me']

    def test_correct_tag_name(self, a):
        assert a.tag_name == 'a'

    def test_access_tag_attrs(self, a):
        assert a.attrs['id'] == 'id'
        assert a.attrs['class'] == 'cls1 cls2'
        assert a.attrs['href'] == 'url'

    def test_tag_id_attr(self, a):
        assert a.id == 'id'

    def test_tag_classes_attr(self, a):
        assert a.classes == ['cls1', 'cls2']

    def test_convert_tag_attrs_to_dict(self, a):
        assert a.attrs.to_dict() == {
            'class': 'cls1 cls2', 'id': 'id', 'href': 'url'
        }
        assert a.attrs.to_dict({'foo': 'bar'}) == {
            'class': 'cls1 cls2', 'id': 'id', 'href': 'url', 'foo': 'bar'
        }

    def test_has_own_attrs(self):
        assert div().attrs.has_own_attrs() is False
        assert div(class_='foo').attrs.has_own_attrs() is False
        assert div(style='foo').attrs.has_own_attrs() is True

    def test_own_attrs(self):
        assert div().attrs.own_attrs() == {}
        assert div(class_='foo').attrs.own_attrs() == {}
        assert div(style='foo').attrs.own_attrs() == {'style': 'foo'}

    def test_render(self, a):
        assert a.attrs.render(None) == 'id="id" class="cls1 cls2" href="url"'
        assert a.render(None) == \
               '<a id="id" class="cls1 cls2" href="url">click me</a>'


class TestMutatingTagAttrsOperations:
    """
    Tests for a single tag object (mutable operations).
    """

    a = TestSimpleTagAttrsOperations.a

    def test_can_delete_tag_args(self, a):
        del a.attrs['href']
        assert a.attrs.to_dict() == {'class': 'cls1 cls2', 'id': 'id'}
        assert len(a.attrs) == 2

        with pytest.raises(KeyError):
            del a.attrs['href']

    def test_cannot_delete_id_and_class_attrs(self, a):
        with pytest.raises(KeyError):
            del a.attrs['class']
        with pytest.raises(KeyError):
            del a.attrs['id']

    def test_add_attrs_to_tag(self, a):
        a.attrs['foo'] = 'bar'
        assert a.attrs.to_dict() == {
            'class': 'cls1 cls2', 'id': 'id',
            'href': 'url', 'foo': 'bar'
            }
        assert sorted(a.attrs) == ['class', 'foo', 'href', 'id']
        assert len(a.attrs) == 4

    def test_empty_class_and_id_does_not_count_on_attrs(self):
        elem = div()
        assert list(elem.attrs) == []
        assert len(elem.attrs) == 0


class TestCoreTagFunctionality:
    @pytest.fixture
    def a(self):
        return a(class_='cls', href='url')['click me']

    def test_tag_copy(self, a):
        assert str(a) == str(a.copy())
        assert a == a.copy()

    def test_tag_call_is_a_constructor(self, a):
        new = a(class_='foo', id='id')
        assert new.classes == ['cls', 'foo']
        assert str(new) == '<a id="id" class="cls foo" href="url">click me</a>'

    def test_getitem_creates_new_tag_with_extra_children(self, a):
        new = a['foo']
        assert new is not a
        assert str(new) == \
               '<a class="cls" href="url">click mefoo</a>'


class TestCompositeTags:
    def test_with_syntax(self):
        with div as elem:
            +a('foo')
        assert str(elem) == '<div><a>foo</a></div>'

    def test_nested_withs(self):
        with div(class_='root') as elem:
            with div:
                +a('foo')
        assert str(elem) == '<div class="root"><div><a>foo</a></div></div>'