from .components.html5_tags import Tag
from .components.text import Text
from typing import List


def query_for_attrs(current_node: Tag, attrs) -> Tag:
    """
    Get a nodes by its attribrutes

    Ex:
        query_for_attrs(node, {'onclick': 'alert(123)'})
    """
    found = 0
    node = None

    for key in attrs:
        if key in current_node.attrs.keys() and \
        current_node.attrs[key] == attrs[key]:
            found += 1

    if found == len(attrs):
        node = current_node

    return node


def query_in_children(node: Tag, **kwargs) -> List[Tag]:
    """
    Query in the children of a given node
    """
    found = []

    for child in node.children:
        if isinstance(child, Text):
            continue

        query_result = query(child, **kwargs)

        if query_result != None:
            if isinstance(query_result, list):
                found += query_result
            else:
                found.append(query_result)

    return found


def query(current_node: Tag, **kwargs) -> List[Tag]:
    """
    Get a node by tag, classes or attribrutes

    Ex:
        query(node, tag='span')
        query(node, attrs={'class': 'b'})
        query(node, attrs={'onclick': 'alert(123)'})
    """

    found = []

    if 'tag' in kwargs.keys() and current_node.tag_name == kwargs['tag']:
        found.append(current_node)

    if 'attrs' in kwargs.keys():
        node = query_for_attrs(current_node, kwargs['attrs'])

        if node != None:
            found.append(node)

    found += query_in_children(current_node, **kwargs)

    return found
