from lazyutils import lazy

from bricks.utils import dash_case


EMPTY_META = object()


class MetaInfo:
    """
    Class for the ._meta attribute of a component.
    """

    @lazy
    def requires(self):
        requires = []
        for base in self.bases:
            meta = base._meta._meta
            if meta:
                extra = [x for x in meta.requires if x not in requires]
                requires.extend(extra)
        return requires

    @lazy
    def bases(self):
        return [cls for cls in self.base.mro() if issubclass(cls, Requirable)]

    @lazy
    def classname(self):
        try:
            return self._meta.classname
        except AttributeError:
            return dash_case(self.base.__name__)

    def __init__(self, cls=None, meta=EMPTY_META):
        self.base = cls
        self._meta = meta


class RequirableMeta(type):
    """
    Metaclass for Component.
    """

    meta_info_class = MetaInfo

    def __init__(cls, name, bases, ns):
        meta_class = ns.pop('Meta', object)
        if not isinstance(meta_class, type):
            raise ValueError('the Meta attribute must be a type.')
        meta = meta_class()
        super().__init__(name, bases, ns)
        cls._meta = cls.meta_info_class(cls, meta)


class Requirable(metaclass=RequirableMeta):
    """
    Defines the component interface for assets.
    """

    _meta = MetaInfo()

    @classmethod
    def required_class_assets(cls):
        """
        Class method that returns a list of all requirements for the component.
        """

        return cls._meta.requires

    def required_assets(self):
        """
        Return a list with the required assets for components.

        This list should not include assets shared between all instances of
        the same class.
        """

        return []
