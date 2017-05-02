from .asset import Asset

from .utils import require_deep


class AssetManager:
    """
    Specify assets necessary to render a given set of components.
    """

    def __init__(self, assets=(), requires=(), provides=(), suggests=None):
        self.assets = list(assets)
        self.requires = list(requires)
        self.provides = set(provides)
        self.suggests = dict(suggests or {})

    def __repr__(self):
        data = []

        if self.assets:
            body = ', '.join(map(lambda x: x.name, self.assets))
            data.append('[%s]' % body)

        if self.requires:
            data.append('requires=%r' % self.requires)

        if self.provides:
            set_data = str(sorted(self.provides))[1:-1]
            data.append('provides={%s}' % set_data)

        if self.suggests:
            dic_data = ', '.join('%r: %s' % (k, v.name)
                                 for k, v in sorted(self.suggests.items()))
            data.append('suggests={%s}' % dic_data)

        return '%s(%s)' % (type(self).__name__, ', '.join(data))

    def load(self, asset):
        """
        Load an asset and update the requires, provides and suggests lists.
        """

        if asset in self.assets:
            return

        provides = self.provides
        requires = self.requires
        suggests = self.suggests

        for label in asset.provides:
            provides.add(label)
            try:
                requires.remove(label)
            except ValueError:
                pass
            suggests.pop(label, None)

        for label in asset.requires:
            if label not in provides:
                requires.append(label)

        for label, sub_asset in asset.suggests.items():
            suggests[label] = sub_asset

        self.assets.append(asset)

    def resolve(self):
        """
        Resolve all dependencies by searching for assets in suggestions and
        then in the global registry.
        """

        self.resolve_suggested()
        self._resolve_global()

    def resolve_suggested(self):
        """
        Resolve all requirements that can be resolved by loading a suggested
        asset.
        """

        suggests = self.suggests
        missing = set()

        while set(self.requires) - missing:
            for label in self.requires:
                if label in missing:
                    continue
                if label in suggests:
                    self.load(suggests[label])
                missing.add(label)

    def _resolve_global(self):
        """
        Resolve all requirements using the global registry.

        Used by resolve() after resolving suggested dependencies.
        """

        requires = self.requires
        while requires:
            label = requires.pop(0)
            asset = Asset.load(label)
            self.load(asset)

    def require(self, *assets, resolve=True):
        """
        Requires the given asset.
        """

        # Normalize args
        if len(assets) == 1:
            arg, = assets
            if not isinstance(arg, str):
                assets = arg

        # Add requirements
        requires = self.requires
        for asset in assets:
            if asset not in requires:
                requires.append(asset)

        if resolve:
            self.resolve()

    def require_from(self, elem, resolve=True):
        """
        Fetches list of requirements from the given component.
        """

        requirements = require_deep(elem)
        self.require(requirements, resolve=resolve)
