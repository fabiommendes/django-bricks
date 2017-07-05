from .components.html5_tags import *  # noqa
from .components.text import Text, html  # noqa
from .components import html5_tags as tags


def a_or_p(*args, href=None, **kwargs):
    """
    Return a or p tag depending if href is defined or not.
    """

    if href:
        return tags.a(*args, href=href, **kwargs)
    else:
        return tags.p(*args, href=href, **kwargs)


def a_or_span(*args, href=None, **kwargs):
    """
    Return a or span tag depending if href is defined or not.
    """

    if href:
        return tags.a(*args, href=href, **kwargs)
    else:
        return tags.span(*args, **kwargs)




def query(current_node, **kwargs):
    """
    TODO: Doc this
    query(node, tag='', classes=[], attrs={'a:': 'b'})
    from bricks.html5 import div, p, button, query
    a = div(class_="a") [ p(class_="b")[ button(onclick="alert(123)")[ "click" ] ], div() [ p(class_="c")[ "so texto" ] ] ]
    """

    node = None

    if 'tag' in kwargs.keys() and current_node.tag_name == kwargs['tag']:
        node = current_node
    elif 'attrs' in kwargs.keys():
        found = 0
        attrs = kwargs['attrs']

        for key in attrs:
            if key in current_node.attrs.keys() and \
            current_node.attrs[key] == attrs[key]:
                found += 1

        if found == len(kwargs['attrs']):
            node = current_node


    if node is None:
        for child in current_node.children:
            if isinstance(child, Text):
                continue

            found = query(child, **kwargs)

            if found:
                return found

    return node
