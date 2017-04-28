import collections
import weakref

from markupsafe import Markup

from bricks.helpers import render, safe
from bricks.request import request


class Children(collections.MutableSequence):
    """
    Controls the obj.children attribute of a component.
    """

    _component_classes = ()

    @property
    def parent(self):
        return self._parent()

    def __init__(self, parent, data=()):
        self._parent = weakref.ref(parent)
        self._data = list(data)

    def __len__(self):
        return len(self._data)

    def __iter__(self):
        return iter(self._data)

    def __getitem__(self, i):
        return self._data[i]

    def __setitem__(self, i, value):
        value = self._convert(value)
        self._attach(value)
        self._detach(self._data[i])
        self._data[i] = value

    def __delitem__(self, i):
        self._detach(self._data[i])
        del self._data[i]

    def __repr__(self):
        return repr(self._data)

    def __str__(self):
        return str(self.render(request))

    def __html__(self):
        return self.render()

    def _attach(self, obj):
        pass

    def _detach(self, obj):
        pass

    def _convert(self, value, escape=True):
        if isinstance(value, self._component_classes):
            return value
        elif isinstance(value, str):
            return self._text_factory(value, escape=escape)
        elif (isinstance(value, type) and
              issubclass(value, self._component_classes)):
            return value()
        else:
            type_name = value.__class__.__name__
            raise TypeError('cannot insert child of type %r' % type_name)

    def _text_factory(self, value, escape):
        raise NotImplementedError(
            'please set the ._text_factory attribute of Children to the Text '
            'component class.'
        )

    def _as_inner_repr(self):
        """
        Used by repr to properly repr children nodes.
        """

        def inner_repr(x):
            return repr(str(x)) if isinstance(x, (str, Markup)) else repr(x)
        return ', '.join(map(inner_repr, self))

    def extend(self, values, escape=True):
        self._data.extend(self._convert(x) for x in values)

    def insert(self, i, obj, escape=True):
        obj = self._convert(obj, escape)
        self._attach(obj)
        self._data.insert(i, obj)

    def append(self, obj, escape=True):
        obj = self._convert(obj, escape)
        self._attach(obj)
        self._data.append(obj)

    def render(self, request, **kwargs):
        return safe(''.join(render(x, request=request, **kwargs) for x in self))


class FrozenChildren(Children):
    """
    An immutable Children list.
    """

    def __setitem__(self, i, value):
        raise self._immutable_error()

    def __delitem__(self, i):
        raise self._immutable_error()

    def insert(self, i, value):
        raise self._immutable_error()

    def append(self, value):
        raise self._immutable_error()

    def _immutable_error(self):
        return TypeError('Children are immutable')
