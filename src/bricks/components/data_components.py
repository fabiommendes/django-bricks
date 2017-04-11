import collections

from bricks.components import Component, ComponentMeta
from bricks.helpers import escape

MutableMeta = type(collections.MutableMapping)


class DictMeta(ComponentMeta, MutableMeta):
    def __init__(self, name, bases, ns):
        ComponentMeta.__init__(self, name, bases, ns)
        MutableMeta.__init__(self, name, bases, ns)


class Mapping(Component, collections.MutableMapping, metaclass=DictMeta):
    """
    A dict-like structure that prints as a definition list.
    """

    class Meta:
        tag = 'dl'

    _tag_name = 'dl'
    _classname = 'dict'

    @property
    def children(self):
        return list(self._items())

    @children.setter
    def children(self, value):
        if self.__has_init:
            raise AttributeError('cannot set children')

    def __init__(self, data, cls='pyml-mapping', **kwargs):
        # Specific init parameters
        escape_keys = kwargs.pop('escape_keys', None)
        escape_values = kwargs.pop('escape_values', None)
        escape = kwargs.pop('escape', None)

        # Start component avoiding children initialization
        self.__has_init = False
        super().__init__(cls=cls, **kwargs)
        self.__has_init = True

        # Sets escaping configurations
        if escape_keys is None:
            self.escape_keys = True if escape is None else escape
        if escape_values is None:
            self.escape_values = True if escape is None else escape
        self._data = collections.OrderedDict(data)

    def __delitem__(self, key):
        del self._data[key]

    def __setitem__(self, key, value):
        self._data[key] = value

    def __getitem__(self, key):
        return self._data[key]

    def __iter__(self):
        return iter(self._data)

    def __len__(self):
        return len(self._data)

    def render_children(self, request=None, **kwargs):
        lines = ['']
        key_trans = escape if self.escape_keys else str
        value_trans = escape if self.escape_values else str
        for k, v in self._data.items():
            data = key_trans(k), value_trans(v)
            lines.append('<dt>%s</dt><dd>%s</dd>' % data)
        lines.append('')
        return '\n'.join(lines)


class Table(Component):
    pass

if __name__ == '__main__':
    d = Mapping({'foo': 42, 'bar': 'foo'})
    d[32] = 'foo'
    d['bar'] = Mapping(d)
    print(d)
    print(escape(d))