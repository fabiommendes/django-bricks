from .components.text import Text


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


def query_in_children(node, **kwargs):
    """
    Query in each children of a given node and returns all found.

    It will execute query for each child of the given node with the given kwargs.
    If a child is a Text tag, it will be ignored.
    If the query return isn't None then it is added to found list.
    """
    found = []

    for child in node.children:
        if isinstance(child, Text):
            continue

        found += query(child, **kwargs)

    return found


def query(current_node, **kwargs):
    """
    Get a node by tag, classes and attributes.
    It will also look in the children of the given node.
    If no node is found, it will returns an empty list.

    Ex:
        # All nodes that has a span tag
        query(node, tag='span')

        # All nodes that has a class 'b'
        query(node, attrs={'class': 'b'})

        # All nodes that has an onclick attr with value 'alert(123)'
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
