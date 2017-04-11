from collections import OrderedDict
from functools import singledispatch


class HTMLRenderMixin:
    """
    Basic Markup interface.
    """

    def __str__(self):
        return str(self.__html__())

    def __html__(self):
        return self.render()

    def render(self, **kwargs):
        raise NotImplementedError


class Css(HTMLRenderMixin):
    """
    Represents a Css structure.
    """

    def __init__(self):
        self._definitions = []

    def __len__(self):
        return len(self._definitions)

    def __iter__(self):
        return iter(self._definitions)

    def add(self, block):
        if not isinstance(block, CssBlock):
            raise TypeError
        self._definitions.append(block)

    def render(self):
        return '\n\n'.join(x.render() for x in self._definitions)


class CssBlock(HTMLRenderMixin):
    """
    A block of Css definitions such as


    .contact span {
        font-size: 0.9em;
    }
    """
    def __init__(self, name, data=None, **kwargs):
        self.name = name
        self._data = OrderedDict()
        if data is not None:
            self._data.update(data)
        if kwargs:
            self._data.update(kwargs)

    def render(self):
        return '%s {%s\n}' % (self.render_head(), self.render_data())

    def render_head(self):
        return self.name

    def render_data(self):
        return ''.join('\n    %s: %s;' % item for item in self._data.items())


class CssId(CssBlock):
    def render_head(self):
        return '#' + self.name


class CssClass(CssBlock):
    def render_head(self):
        return '.' + self.name


@singledispatch
def css_render(obj):
    """
    Renders object as CSS source.
    """

    return str(obj)


def dict_to_css(dict):
    """
    Convert a Python dictionary structure to a CSS object.
    """

    css = Css()
    for key, value in dict.items():
        cls, key = parse_css_head(key)
        css.add(cls(key, value))

    return css


def parse_css_head(head):
    """
    Return a tuple with (cls, name) from the given head.

    Unrecognized heads will return a generic (CssBlock, head) value.
    """

    return CssBlock, head
