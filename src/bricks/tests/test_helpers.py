import pytest
from markupsafe import Markup
from mock import mock

from bricks.helpers import render, attr, attrs, hyperlink, render_tag, safe, \
    markdown, \
    sanitize, join_classes, js_class
from bricks.helpers.attr import html_safe_natural_attr
from bricks.helpers.hyperlink import parse_link
from bricks.helpers.render import pretty
from bricks.tests.testapp.models import RenderableModel


class TestAttrs:
    """
    Test functions on bricks.helpers.attr
    """

    def test_attrs_examples(self):
        assert attrs([('foo', 42), ('bar', 'bar')]) == 'foo="42" bar="bar"'
        assert attrs(None, x=42) == 'x="42"'
        assert attrs({'foo': safe('bar')}) == 'foo="bar"'
        assert attrs({'foo': '<tag>'}) == 'foo="<tag>"'
        assert attrs({'foo': '"quote"'}) == 'foo="&quot;quote&quot;"'
        assert attrs({'foo': True, 'bar': False, 'baz': None}) == 'foo'

    def test_attrs_protocol(self):
        class Foo:
            attrs = [('x', 1), ('y', 2)]

        assert attrs(Foo()) == 'x="1" y="2"'

    def test_attrs_not_supported(self):
        class Foo:
            pass

        for x in [b'bytes', Foo()]:
            with pytest.raises(TypeError):
                print(attr(x))
            with pytest.raises(TypeError):
                print(attrs(x))

        with pytest.raises(TypeError):
            print(attrs('str'))

    def test_attr_examples(self):
        assert attr('foo') == 'foo'
        assert attr({'foo': 'bar'}) == '{&quot;foo&quot;: &quot;bar&quot;}'

    def test_attr_names(self):
        assert html_safe_natural_attr('data-foo') == 'data-foo'
        assert html_safe_natural_attr('data_foo') == 'data-foo'
        assert html_safe_natural_attr('v-bind:foo') == 'v-bind:foo'
        assert html_safe_natural_attr(':foo') == ':foo'
        assert html_safe_natural_attr('@foo') == '@foo'

        invalid = ['foo bar', 'foo"', 'foo=', 'foo\'']
        for name in invalid:
            with pytest.raises(ValueError):
                html_safe_natural_attr(name)

    def test_join_classes(self):
        assert join_classes(['x', 'y', False], None, "foo bar") == \
               ['x', 'y', 'foo', 'bar']
        assert js_class(['x', 'y'], None, "foo bar") == 'x y foo bar'


class TestEscape:
    """
    Tests functions on bricks.helpers.escape
    """

    def test_sanitize(self):
        assert sanitize('<b>foo</b>') == '<b>foo</b>'
        assert '<script>' not in sanitize('<script>foo</script')


class TestExtras:
    """
    Tests functions on bricks.helpers.extra
    """

    def test_tag_examples(self):
        assert render_tag('div', 'foo',
                          class_='c') == '<div class="c">foo</div>'
        assert render_tag('script',
                          src='foo.js') == '<script src="foo.js"></script>'
        assert render_tag('a', ['a', 'b'],
                          children_kwargs={'foo': True}) == '<a>a\nb</a>'

    def test_tag_render_with_request(self):
        assert render_tag('div', 'foo', request='request') == '<div>foo</div>'

    def test_markdown(self):
        assert markdown('#foo\n') == '<h1>foo</h1>'


class TestHyperlink:
    """
    Tests functions on bricks.helpers.hyperlink
    """

    def test_hyperlink_examples(self):
        link = '<a href="bar">foo</a>'
        assert hyperlink('foo') == '<a>foo</a>'
        assert hyperlink('foo', 'bar') == link
        assert hyperlink({'href': 'bar', 'content': 'foo'}) == link
        assert hyperlink('foo', attrs={'href': 'bar'}) == link
        assert hyperlink({'content': 'foo'}, attrs={'href': 'bar'}) == link
        assert hyperlink(RenderableModel()) == '<a href="absolute-url">obj</a>'

    def test_hyperlink_not_supported(self):
        with pytest.raises(TypeError):
            hyperlink(b'sdfsdf')

    def test_parse_link_function(self):
        assert parse_link('foo') == ('foo', None)
        assert parse_link('foo<bar>') == ('foo', 'bar')
        assert parse_link('foo <bar>') == ('foo', 'bar')


class TestRender:
    """
    Tests functions on bricks.helpers.render
    """

    def test_render_examples(self):
        assert render('bar') == 'bar'
        assert render(['foo', 'bar']) == 'foo\nbar'
        assert render(Markup('foo')) == 'foo'

    def test_render_renderable(self):
        class Foo:

            def __str__(self):
                return 'foo'

            __html__ = __str__

            def render(self, request):
                return str(self)

        foo = Foo()
        assert render(foo) == 'foo'

    def test_render_model(self):
        m = RenderableModel(title='foo')
        assert render(m) == '<div class="renderable">foo</div>'

    def test_render_not_supported(self):
        with pytest.raises(TypeError):
            render(b'sdfsdf')

    def test_register_template(self):
        class Foo:
            pass

        render.register_template(Foo)
        result = []

        def f(*args, **kwargs):
            result.append((args, kwargs))
            return ''

        with mock.patch('bricks.helpers.render._render_template', f):
            foo = Foo()
            x = render(foo)
            args, kwargs = result.pop()
            assert args == (['bricks/foo.html', 'bricks/foo.jinja2'],)
            assert sorted(kwargs) == ['context', 'request']
            request = kwargs['context']['request']
            assert hasattr(request, 'POST')
            assert kwargs['context'] == {'foo': foo, 'request': request}

    def test_register_template_using_decorator(self):
        class Foo:
            pass

        @render.register_template(Foo)
        def get_context(x, request, **kwargs):
            return {'x': x, 'request': None}

        result = []

        def f(*args, **kwargs):
            result.append((args, kwargs))
            return ''

        with mock.patch('bricks.helpers.render._render_template', f):
            foo = Foo()
            x = render(foo)
            args, kwargs = result.pop()
            assert kwargs['context'] == {'x': foo, 'request': None}

    def test_pretty_printer(self):
        html = pretty('<div><p>foo</p></div>').strip()
        assert html == '<div>\n  <p>foo</p>\n</div>'