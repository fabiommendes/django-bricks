from .attrs import Attrs, FrozenAttrs
from .children import Children, FrozenChildren
from .text import Text
from .core import Component, Tag, VoidTag, BaseComponent

Children._text_factory = Text
Children._component_classes += (BaseComponent, Text)
