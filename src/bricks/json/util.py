def normalize_class_name(cls, name=None):
    """
    Return the default class name from the given type.
    """

    if name:
        return name
    return cls.__name__.lower()