from collections import defaultdict
from types import MappingProxyType as mappingproxy

ASSET_REGISTRY = defaultdict(list)


class Asset:
    """
    Base class representing an abstract asset.
    """

    __slots__ = ('name', 'provides', 'requires', 'suggests', '_hash')
    is_concrete = False

    @classmethod
    def load(cls, label):
        """
        Load asset by label.
        """

        try:
            return ASSET_REGISTRY[label][-1]
        except IndexError:
            raise ValueError('no asset provides for %r' % label)

    def __init__(self, name, provides=(), requires=(), suggests=None):
        self.name = name
        self.provides = frozenset(provides or ())
        self.requires = tuple(requires or ())
        self.suggests = mappingproxy(suggests or {})
        self._hash = None

        # Register on global asset registry
        for label in self.provides:
            ASSET_REGISTRY[label].append(self)

    def __repr__(self):
        cname = self.__class__.__name__
        name = self.name

        if self.provides:
            return '%s(%r, %r)' % (cname, name, sorted(self.provides))
        elif self.requires:
            return '%s(%r, requires=%r)' % (cname, name, list(self.requires))
        elif self.suggests:
            data = ('%r: %s' % (k, v.name) for k, v in self.suggests.items())
            data = ', '.join(data)
            return '%s(%r, suggests={%s})' % (cname, name, data)
        else:
            return '%s(%r)' % (cname, name)

    def __hash__(self):
        if self._hash is None:
            self._hash = hash((
                self.name,
                self.provides,
                self.requires,
                tuple(self.suggests.items()),
            ))
        return self._hash

    def __eq__(self, other):
        if type(self) is type(other):
            return (
                self.name == other.name and
                self.provides == other.provides and
                self.requires == other.requires and
                self.suggests == other.suggests
            )
        return NotImplemented
