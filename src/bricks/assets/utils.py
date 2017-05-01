import os
from collections import deque

EXT_TO_TYPE_MAPPING = {
    '.css': 'text/css',
    '.txt': 'text',
}
EXT_TO_REL_MAPPING = {
    '.css': 'stylesheet'
}


def require_deep(elem):
    """
    Gather list of requirements by walking through all children starting
    with the given element.
    """

    visited_requires = set()
    reqset = set(elem.requires)
    reqlist = list(elem.requires)
    roots = deque(elem.roots)

    while roots:
        root = roots.popleft()
        for child in root:
            # Adds all direct requirements for the child element
            if id(child.requires) not in visited_requires:
                for label in child.requires:
                    if label not in reqset:
                        reqset.add(label)
                        reqlist.append(label)
                visited_requires.add(id(child.requires))

            # Add all roots to the search list
            roots.extend(child.roots)

    return reqlist


def rel_from_href(href):
    """
    Return the default rel for a given address.
    """
    _, ext = os.path.splitext(href)
    if ext not in EXT_TO_REL_MAPPING:
        raise ValueError('could not determine rel for extension: %r' % ext)
    return EXT_TO_REL_MAPPING[ext]


def type_from_href(href):
    """
    Return the default type for a given address.
    """
    _, ext = os.path.splitext(href)
    try:
        return EXT_TO_TYPE_MAPPING[ext]
    except KeyError:
        return 'text/' + ext[1:]
