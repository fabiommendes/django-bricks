import collections
import weakref

from bricks.helpers import safe
from bricks.helpers.attr import html_natural_attr, attrs as _attrs


class Attrs(collections.MutableMapping):
    """
    Implements the Component.attrs attribute.
    """

    @property
    def parent(self):
        return self._parent()

    def __init__(self, parent, data=None):
        self._parent = weakref.ref(parent)
        self._data = dict(data or {})

    def __getitem__(self, key):
        try:
            return self._data[key]
        except KeyError:
            if key == 'class' and self.parent.classes:
                return ' '.join(self.parent.classes)
            elif key == 'id' and self.parent.id:
                return self.parent.id
            raise

    def __delitem__(self, key):
        try:
            del self._data[key]
        except KeyError:
            self._key_check_before_mutation(key)
            raise

    def __setitem__(self, key, value):
        self._key_check_before_mutation(key)
        self._data[key] = value

    def __len__(self):
        parent = self.parent
        extra = (parent.id is not None) + (bool(parent.classes))
        return len(self._data) + extra

    def __iter__(self):
        parent = self.parent
        if parent.id is not None:
            yield 'id'
        if parent.classes:
            yield 'class'
        yield from iter(self._data)

    def __eq__(self, other):
        if len(self) != len(other):
            return False
        try:
            for k, v in self.items():
                if other[k] != v:
                    return False
            return True
        except (TypeError, KeyError, IndexError):
            return NotImplemented

    def __repr__(self):
        return repr(dict(self))

    def _key_check_before_mutation(self, key):
        if key == 'class':
            raise KeyError('cannot modify the class via `attrs`.')
        elif key == 'id':
            raise KeyError('cannot modify id via `attrs`.')

    def update(*args, **kwargs):
        """
        Update attributes. It converts keyword arguments to the natural HTML
        names (i.e., replace underscores by dashes and remove trailing
        underscores).
        """
        self, *args = args
        if args:
            super(Attrs, self).update(*args)
        for k, v in kwargs.items():
            self[html_natural_attr(k)] = v

    def to_dict(self, attrs=None, exclude_class=False, exclude_id=False):
        """
        Return a dictionary from attribute values, possibly passing a dictionary
        with extra attributes.

        Args:
            attrs (map):
                A dictionary with additional attributes to include in
                rendering.
            replace_class (bool):
                If True and attrs contain a 'class' key, it will replace the
                class instead of adding new values.
            exclude_class (bool):
                If True, exclude the class attribute.
            exclude_id (bool):
                If True, exclude the id attribute.

        Returns:
            A dictionary of attribute/value pairs.
        """

        data = self._data.copy()
        attrs = attrs or {}
        data.update(attrs)
        parent = self.parent
        if (not exclude_id) and parent.id:
            data['id'] = parent.id
        if (not exclude_class) and parent.classes:
            data['class'] = ' '.join(parent.classes)
        if 'class' in attrs:
            classes = list(parent.classes)
            new_classes = attrs['class']
            if isinstance(new_classes, str):
                new_classes = new_classes.split()
            classes.extend(new_classes)
            data['class'] = ' '.join(classes)
        return data

    def has_own_attrs(self):
        """
        Return True if attrs dict has any attribute besides 'class' and 'id'
        """

        return bool(self._data)

    def own_attrs(self):
        """
        Return a dictionary with only the attributes owned by attrs. (i.e.,
        exclude both 'class' and 'id').
        """

        return dict(self._data)

    def render(self, request, attrs=None, exclude_class=False,
               exclude_id=False, **kwargs):
        """
        Renders attributes, possibly passing a dictionary with extra attributes
        key-values or overrides.
        """

        result = []
        data = self.to_dict(attrs,
                            exclude_class=exclude_class,
                            exclude_id=exclude_id)

        # Draw id and class before
        if 'id' in data:
            result.append('id="%s"' % data.pop('id'))
        if 'class' in data:
            result.append('class="%s"' % data.pop('class'))

        # Draw all other attributes
        tail = _attrs(data)
        if tail:
            result.append(tail)

        return ' '.join(result)

    def copy(self, new_parent):
        """
        Return a copy of attributes dict for the new parent.
        """

        new = object.__new__(self.__class__)
        new._parent = weakref.ref(new_parent)
        new._data = self._data.copy()
        return new

    def _as_inner_repr(self):
        result = []
        classes = self.parent.classes
        if self.parent.id:
            result.append('id=%r' % self.parent.id)
        if classes:
            data = classes[0] if len(classes) == 1 else classes
            result.append('class_=%r' % data)

        # Check safe attributes
        if all('-' not in x for x in self._data):
            result.extend('%s=%r' % item for item in self._data.items())
        else:
            result.extend('attrs=%r' % self._data)
        return ', '.join(result)


class FrozenAttrs(Attrs):
    """
    A immutable version of Attrs.
    """

    def __setitem__(self, key, value):
        raise self._immutable_error()

    def __delitem__(self, key):
        raise self._immutable_error()

    def update(self, *args, **kwargs):
        raise self._immutable_error()

    def _immutable_error(self):
        return TypeError('Attributes are immutable')


@_attrs.register(Attrs)
def _(attrs, request=None, **kwargs):
    return safe(attrs.render(request, **kwargs))
