from .components.text import Text
from collections import Sequence

class Query(Sequence):
    def __init__(self,query_list):
        self._data = query_list

    def __len__(self):
        return len(self._data)

    def __iter__(self):
        return iter(self._data)

    def __getitem__(self, index):
        return self._data[index]

    def find(self):
        query = query_in_list(self._data)
        return query

def query_for_attrs(node, attrs):
    """
    Verify if the given node, has all the given attribrutes.

    If all given attributes were found in the given node,
    then returns the given node otherwise None

    Ex:
        node = button(class_='btn btn-success', onclick='alert(123)') [ 'Click here !' ]
        query_for_attrs(node, {'onclick': 'alert(123)'})
    """
    attrs_found = 0

    for key in attrs:
        # For each attr found, it increments the attrs_found
        if key in node.attrs.keys() and \
        node.attrs[key] == attrs[key]:
            attrs_found += 1

    # The attrs_found length must match the given attrs length
    if attrs_found == len(attrs):
        return node
    else:
        return None


def query_in_list(nodes, tag=None, **attrs):
    """
    Query in each children of a given node and returns all found.

    It will execute query for each child of the given node with the given attrs.
    If a child is a Text tag, it will be ignored.
    If the query return isn't None then it is added to found list.
    """
    found = []

    for child in nodes:
        if isinstance(child, Text):
            continue
        
        found.extend(query(child, tag, **attrs))

    return found

def has_tag_factory(tag):
    return lambda b: b.tag == tag

def has_attrs_factory(attrs):
    def has_attrs(b):
        """
        Verify if the given node, has all the given attribrutes.

        If all given attributes were found in the given node,
        then returns the given node otherwise None

        Ex:
            node = button(class_='btn btn-success', onclick='alert(123)') [ 'Click here !' ]
            query_for_attrs(node, {'onclick': 'alert(123)'})
        """
        attrs_found = 0

        for key in attrs:
            # For each attr found, it increments the attrs_found
            if key in b.attrs.keys() and \
            b.attrs[key] == attrs[key]:
                attrs_found += 1

        # The attrs_found length must match the given attrs length
        if attrs_found == len(attrs):
            return b
        else:
            return None
    
    return has_attrs

def join_factory(*funcs):
    """
    TODO: Botar em inglês
    pega um brik e executa ele em todas as funcoes
    vai dar uma lista de boleanos [True, True, False]
    então reduz tudo a um unico boolean
    """

    return lambda brick: all(fn(brick) for fn in funcs)

def query(current_node, tag=None, **attrs):
    """
    Get a node by tag, classes and attributes.
    It will also look in the children of the given node.
    If no node is found, it will returns an empty list.

    Ex:
        # All nodes that has a span tag
        query(node, tag='span')

        # All nodes that has a class 'b'
        query(node, class='b')

        # All nodes that has an onclick attr with value 'alert(123)'
        query(node, onclick='alert(123)')
    """

    

    found = []
    tag_found = False
    attrs_found = False

    if tag and current_node.tag_name == tag:
        tag_found = True

    if attrs:
        node = query_for_attrs(current_node, attrs)

        if node != None:
            attrs_found = True

    # Tag and Attrs
    if tag and attrs and \
    tag_found and attrs_found:
        found.append(current_node)

    # Tag and not Attrs
    elif tag and attrs is None and \
    tag_found and not attrs_found:
        found.append(current_node)

    # Attrs and not Tag
    elif tag is None and attrs and \
    not tag_found and attrs_found:
        found.append(current_node)

    found.extend(query_in_list(current_node.children, tag, **attrs))

    return found
