def ifset(a, b):
    """
    Returns the second argument if the first is not None or False. Return
    None otherwise.

    This is mostly equivalent to "a and b" but only recognizes None and False
    as "falsy" values.
    """
    return None if a is None or a is False else b