"""
Utility functions for working with the Block-Element-Modifier (BEM) CSS
methodology.
"""


def bem_modifiers(base, map=None, **states):
    """
    Return a list with BEM modifiers for a given class if marked states
    are enabled.

    Examples:

        >>> bem_modifiers('block', state_1=False, state_2=True)
        ['block--state-2']
    """

    if states and not map:
        return bem_modifiers(base, states)
    elif states and map:
        return bem_modifiers(base, map) + bem_modifiers(base, states)
    else:
        result = []
        for name, enabled in map.items():
            if enabled is False or enabled is None:
                continue
            elif enabled is True:
                name = name.replace('_', '-')
                result.append('%s--%s' % (base, name))
            elif isinstance(enabled, str):
                result.append(enabled)
            else:
                raise TypeError('invalid element: %s=%r' % (name, enabled))
        return result


def bem_with_modifiers(base, map=None, **states):
    """
    Return a list with BEM modifiers prefixed by the main block element.

    Examples:

        >>> bem_with_modifiers('block', state_1=False, state_2=True)
        ['block', 'block--state-2']
    """

    result = [base]
    result.extend(bem_modifiers(base, map, **states))
    return result
