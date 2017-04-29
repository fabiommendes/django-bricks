import abc
import collections
import copy
import threading

from markupsafe import Markup

from bricks.helpers import render_tag, join_classes
from bricks.helpers.render import pretty
from bricks.mixins import Renderable
from bricks.require import Requirable
from bricks.require.requirable import RequirableMeta
from bricks.utils import dash_case
from bricks.utils.sequtils import flatten
from .attrs import Attrs
from .children import Children


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

    _thread_local = threading.local()

    def __init__(cls, name, bases, namespace):
        super().__init__(name, bases, namespace)
        if 'tag_name' not in namespace:
            for subclass in reversed(cls.mro()[1:]):
                if (hasattr(subclass, 'tag_name') and
                            subclass.tag_name != dash_case(subclass.__name__)):
                    break
            else:
                cls.tag_name = dash_case(name)

    def __getitem__(cls, item):
        obj = cls()
        return obj[item]

    def __enter__(cls, *args):
        obj = cls()
        return obj.__enter__(*args)

    def __exit__(cls, *args):
        last = cls._thread_local.stack[-1]
        return last.__exit__(*args)


class BaseComponent(Requirable,
                    Renderable, metaclass=ComponentMeta):
    """
    Common functionality to Element and Tag
    """

    def __init__(self, children=None, *, class_=None, id=None, attrs=None,
                 **kwargs):
        Requirable.__init__(self)
        self.id = id
        if isinstance(class_, str):
            self.classes = class_.split()
        elif class_ is None:
            self.classes = []
        else:
            self.classes = list(class_)

        self.attrs = Attrs(self, attrs or {})
        self.attrs.update(**kwargs)

        self.children = Children(self)
        if children is None:
            pass
        elif isinstance(children, (str, Markup, BaseComponent)):
            self.children.append(children)
        elif isinstance(children, collections.Iterable):
            self.children.extend(children)
        else:
            self.children.append(children)

    def __getitem__(self, item):
        new = self.copy()
        if isinstance(item, (tuple, list)):
            item = flatten(item)
            new.children.extend([x for x in item if x is not None])
        elif item is not None:
            new.children.append(item)
        return new

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
        name = self.__class__.__name__
        if not self.attrs and not self.children:
            return '%s()' % name
        elif self.attrs and not self.children:
            return '%s(%s)' % (name, self.attrs._as_inner_repr())
        elif not self.attrs and self.children:
            fmt = '%s(%s)' if len(self.children) == 1 else '%s([%s])'
            return fmt % (name, self.children._as_inner_repr())
        else:
            fmt = (name, self.attrs._as_inner_repr(),
                   self.children._as_inner_repr())
            return '%s(%s)[%s]' % fmt

    def __call__(self, children=None, **kwargs):
        new = self.copy()
        if 'id' in kwargs:
            new.id = kwargs.pop('id')
        if 'class_' in kwargs:
            new.add_class(*join_classes(kwargs.pop('class_')))
        if children:
            new = new[children]
        new.attrs.update(kwargs)
        return new

    def __enter__(self, *args):
        cls = type(self)
        try:
            stack = getattr(cls._thread_local, 'stack')
        except AttributeError:
            stack = cls._thread_local.stack = []
        if stack:
            self.__pos__()  # adds to the end of the stack
        stack.append(self)
        return self

    def __exit__(self, *args):
        cls = type(self)
        stack = cls._thread_local.stack
        stack.remove(self)

    def __pos__(self):
        cls = type(self)
        stack = cls._thread_local.stack
        if stack:
            parent = stack[-1]
            parent.children.append(self)
        else:
            raise RuntimeError('unary operator only works inside a with block.')
        return self

    def copy(self, keep_id=True):
        """
        Return a copy of object.

        If keep_id is False, resets the id attribute.
        """

        new = copy.copy(self)
        new.attrs = self.attrs.copy(new)
        new.children = type(self.children)(new)
        new.children.extend([child.copy() for child in self.children])
        new.classes = self.classes.copy()
        new.id = self.id if keep_id else None
        return new

    def add_class(self, cls, *extra_classes):
        """
        Add classes to the class list.

        Does nothing if class is already present.
        """

        if cls not in self.classes:
            self.classes.append(cls)
        if extra_classes:
            cls_set = set(self.classes)
            classes = [cls for cls in extra_classes if cls not in cls_set]
            self.classes.extend(classes)

    def render(self, request=None, id=None, cls=None, **kwargs):
        """
        Renders element as HTML.
        """

        content = self.children.render(request, **kwargs)
        return render_tag(self.tag_name, content, self.attrs, request=request)

    def pretty(self):
        """
        Render a pretty printed HTML.

        This method is less efficient than .render(), but is useful for
        debugging
        """

        return pretty(self)

    def json(self, **kwargs):
        """
        JSON-compatible representation of object.
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


class VoidTag(Tag):
    """
    Base class for self closing tags such as <input>, <br>, <meta>, etc.
    """
