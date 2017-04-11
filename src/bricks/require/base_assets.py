from collections import defaultdict

from lazyutils import lazy

from bricks.exceptions import AssetNotRegisteredError


class Asset:
    """
    Base class representing an abstract asset.
    """

    _global = defaultdict(list)

    @classmethod
    def load_asset(cls, name):
        """
        Return an asset instance with the given name.
        """

        return cls.possible_assets(name)[-1]

    @classmethod
    def possible_assets(cls, name):
        """
        Return a list of all global assets registered to the given name.
        """

        L = []
        L.extend(cls._global[name])
        if L:
            return L
        else:
            raise AssetNotRegisteredError(name)

    @classmethod
    def clear_assets(cls, *names):
        """
        Clear all assets with the given name from registry.
        """

        for name in names:
            cls._global[name] = []

    @lazy
    def names(self):
        L = [self.name]
        L.extend(self.provides)
        return L

    def __init__(self, name=None, provides=(), requires=()):
        self.name = name
        self.provides = tuple(provides)
        self.requires = tuple(requires)

        # Register on global asset registry
        if name is not None:
            self._global[name].append(self)
            for provided in self.provides:
                self._global[provided].append(self)

            # Register bundle
            basename, sep, ext = name.rpartition('.')
            if not ext.isdigit() and sep:
                try:
                    bundle = self._global[basename][0]
                except IndexError:
                    bundle = Bundle(basename, [self.name])
                else:
                    bundle.add(self.name)
                L = self._global[basename]
                if bundle not in L:
                    L.append(bundle)

    def __repr__(self):
        return '%s(%r)' % (self.__class__.__name__, self.name)

    def __hash__(self):
        return hash(tuple(self.__dict__.items()))

    def __eq__(self, other):
        return self is other

    def provide(self, name):
        """
        Return True if object provide the given asset.

        Args:
            name (str):
                An asset name (e.g.: 'jquery.js')
        """

        return name in self.names

    def require(self, name):
        """
        Return True if object require the given asset.

        Args:
            name (str):
                An asset name (e.g.: 'jquery.js')
        """

        return name in self.requires

    def render(self, context):
        """
        Renders element in the given context.

        Args:
            context (str):
                Name of rendering context (e.g.: 'js', 'css', 'head', etc)
        """

        context = context.replace('-', '_')
        renderer = getattr(self, 'render_' + context, None)
        if renderer is not None:
            return renderer()
        return ''


class Bundle(Asset):
    """
    Provides multiple assets at once.
    """

    def __init__(self, name, assets=(), **kwargs):
        super().__init__(name, **kwargs)
        self.assets = list(assets)

    def __len__(self):
        return len(self.assets)

    def __iter__(self):
        return iter(self.assets)

    def add(self, asset):
        """
        Register new asset to bundle.
        """

        self.assets.append(asset)

    def render(self, name):
        data = [Asset.load_asset(x).render(name) for x in self]
        return '\n'.join(x for x in data if x)
