import collections
import weakref

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
            if key == 'class':
                return ' '.join(self.parent.classes)
            elif key == 'id':
                return self.parent.id
            raise

    def __delitem__(self, key):
        try:
            del self._data[key]
        except KeyError:
            self._key_check(key)
            raise

    def __setitem__(self, key, value):
        self._key_check(key)
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

    def _key_check(self, key):
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
            super().update(*args)
        for k, v in kwargs.items():
            self[html_natural_attr(k)] = v

    def to_dict(self, attrs=None, replace_class=False, exclude_class=False,
                exclude_id=False):
        """
        Return a dictionary from attribute values, possibly passing a dictionary
        with extra attributes.

        Args:
            attrs (map):
                A dictionary with additional attributes to include in
                rendering.
            replace_class (bool):
                If True and attrs contain a 'class' key, it will replace the
                class instead of adding a new value.
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
        if (not replace_class) and 'class' in attrs:
            classes = attrs['class']
            parent_classes = ' '.join(parent.classes)
            if not isinstance(classes, str):
                classes = ' '.join(classes)
            if parent_classes:
                classes = '%s %s' % (parent_classes, classes)
            data['class'] = classes
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

    def render(self, attrs=None, append_class=True, **kwargs):
        """
        Renders attributes, possibly passing a dictionary with extra attributes
        key-values or overrides.
        """

        data = self.to_dict(attrs, append_class)
        if not data.get('class'):
            data.pop('class', None)
        return _attrs(data)

    def copy(self, new_parent):
        """
        Return a copy of attributes dict for the new parent.
        """

        new = object.__new__(self.__class__)
        new._parent = weakref.ref(new_parent)
        new._data = self._data.copy()
        return new


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