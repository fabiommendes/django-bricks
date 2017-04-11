from random import choice
from string import ascii_letters, digits

valid_id_chars = ascii_letters + digits + '_-'


def random_id(prefix='id-', size=8):
    """
    Return a random valid HTML id.

    Args:
        prefix:
            A prefix string.
        size:
            The size of the random part of the string. The default value of 8
            gives a collision probability of ~ 3.5e-15, which is good enough for
            most cases.

    Returns:
        A random string.

    """
    if not prefix:
        prefix = choice(ascii_letters)
    return prefix + ''.join(choice(valid_id_chars) for _ in range(size))