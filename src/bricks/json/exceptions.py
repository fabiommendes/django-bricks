class JSONEncodeError(TypeError):
    """
    Error raised when encoding a Python object to JSON.
    """


class JSONDecodeError(ValueError):
    """
    Error raised when decoding a JSON structure to a Python object.
    """