import abc
import collections
import copy

from bricks.components import Attrs, Children
from bricks.helpers import render_tag
from bricks.components.mixins import HasParentMixin
from bricks.mixins import Renderable
from bricks.require import RequirableMeta, Requirable
from bricks.utils import dash_case


class MetaInfo:
    """
    MetaInfo is the base class for the _meta attribute of components.
    """

    children_factory = Children
    attrs_factory = Attrs
    _valid_vars = {var for var in locals() if not var.startswith('_')}

    def __init__(self, meta):
        names = [x for x in dir(meta) if not x.startswith('_')]
        for name in names:
            if name not in self._valid_vars:
                raise AttributeError('invalid variable for Meta: %r' % name)
            setattr(self, name, getattr(meta, name))


class ComponentMeta(RequirableMeta, abc.ABCMeta):
    """
    Metaclass for Element and HTMLTag classes.
    """

    def __init__(cls, name, bases, namespace):
        super().__init__(name, bases, namespace)
        cls.tag_name = dash_case(cls._tag_name or name)

    def __getitem__(cls, item):
        obj = cls()
        if isinstance(item, tuple):
            obj.children.extend(item)
        else:
            obj.children.append(item)
        return obj


class BaseComponent(HasParentMixin,
                    Requirable,
                    Renderable, metaclass=ComponentMeta):
    """
    Common functionality to Element and Tag
    """

    _tag_name = None

    def __init__(self, data=None, cls=None, classes=(), id=None, attrs=None,
                 parent=None, **kwargs):
        Requirable.__init__(self)
        self.id = id
        self.classes = cls.split() if cls else []
        self.classes.extend(classes)

        self.attrs = Attrs(self, attrs or {})
        self.attrs.update(**kwargs)

        HasParentMixin.__init__(self, parent)
        self.children = Children(self)
        if data is None:
            pass
        elif isinstance(data, str):
            self.children.append(data)
        elif isinstance(data, collections.Iterable):
            self.children.extend(data)
        else:
            self.children.append(data)

    def __getitem__(self, item):
        if isinstance(item, tuple):
            self.children.extend(item)
        else:
            self.children.append(item)
        return self

    def __eq__(self, other):
        if other.__class__ is self.__class__:
            if self.classes != other.classes:
                return False
            if self.attrs != other.attrs:
                return False
            if len(self.children) != len(other.children):
                return False
            if any(x != y for (x, y) in zip(self.children, other.children)):
                return False
            return True
        return NotImplemented

    def __repr__(self):
        attrs = self.attrs.render()
        if attrs:
            return '<%s object (%s)>' % (self.__class__.__name__, attrs)
        else:
            return '<%s object>' % self.__class__.__name__

    def copy(self, parent=None, keep_id=False):
        """
        Return a copy of object, possibly setting a new parent.

        Id is not the same.
        """

        new = copy.copy(self)
        new._parent = None
        new.parent = parent
        new.attrs = self.attrs.copy(new)
        new.children = type(self.children)(new)
        new.children.extend([child.copy() for child in self.children])
        new.classes = self.classes.copy()
        if keep_id:
            new.id = self.id
        return new

    def add_class(self, cls, *extra_classes):
        """
        Add classes to the class list.
        """

        self.classes.append(cls)
        if extra_classes:
            self.classes.extend(extra_classes)

    def render(self, request, id=None, cls=None, **kwargs):
        """
        Renders element as HTML.
        """

        content = self.children.render(**kwargs)
        return render_tag(self.tag_name, content, self.attrs)

    def json(self, **kwargs):
        """
        JSON representation of object.
        """

        json = {'tag': self.tag_name}
        if self.classes:
            json['classes'] = list(self.classes)
        if self.id is not None:
            json['id'] = self.id
        if self.attrs.has_own_attrs():
            json['attrs'] = self.attrs.own_attrs()
        if self.children:
            json['children'] = [x.json() for x in self.children]
        return json


class Component(BaseComponent):
    """
    Base class for all custom elements.
    """


class Tag(BaseComponent):
    """
    Base class for all HTML tag elements.
    """


class SelfClosingTag(Tag):
    """
    Base class for self closing tags such as <input>, <br>, <meta>, etc.
    """
