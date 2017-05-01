from bricks.assets.utils import rel_from_href, type_from_href
from bricks.html5 import script, link
from .asset import Asset


class ConcreteAsset(Asset):
    """
    A concrete asset prevents provides from being empty.

    If no provides is given, provides the asset name.
    """
    is_concrete = True

    def __init__(self, name, provides=None, **kwargs):
        if provides is None:
            provides = (name,)
        super().__init__(name, provides, **kwargs)


class Script(ConcreteAsset):
    """
    Represents external content loaded by an <script> tag.

    This should not be used for inlined scripts.
    """

    def __init__(self, name, src, provides=None,
                 type='text/javascript', **kwargs):
        super().__init__(name, provides, **kwargs)
        self.src = src
        self.type = type

    def tag(self):
        if self.type != 'text/javascript':
            return script(src=self.src, type=self.type)
        return script(src=self.src)


class BottomScript(Script):
    """
    A subclass of Script that marks that it is safe to load in the bottom of
    a page.
    """

    def __init__(self, *args, **kwargs):
        if len(args) == 1 and isinstance(args[0], Script):
            script, = args
            args = script.name + '-bottom', script.src, script.provides
            kwargs = dict(
                type=script.type,
                requires=script.requires,
                suggests=script.suggests,
            )
        super().__init__(*args, **kwargs)


class Link(ConcreteAsset):
    """
    A generic <link> asset.
    """

    def __init__(self, name, href, provides=None, rel=None, type=None,
                 **kwargs):
        super().__init__(name, provides, **kwargs)
        self.href = href
        self.rel = rel_from_href(href) if rel is None else rel
        self.type = type_from_href(href) if type is None else href

    def tag(self):
        return link(href=self.href, rel=self.rel, type=self.type)


class Css(Asset):
    """
    Links to an stylesheet.
    """

    def __init__(self, name, href, provides=None, **kwargs):
        super().__init__(name, provides, **kwargs)
        self.href = href

    def tag(self):
        return link(href=self.href, rel='stylesheet', type='text/css')
