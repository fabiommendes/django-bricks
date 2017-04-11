import weakref


class HasParentMixin:
    @property
    def parent(self):
        if self._parent is None:
            return None
        try:
            return self._parent()
        except ReferenceError:
            return None

    @parent.setter
    def parent(self, value):
        if value is None:
            self._parent = None
        else:
            self._parent = weakref.ref(value)

    def __init__(self, parent):
        self.parent = parent