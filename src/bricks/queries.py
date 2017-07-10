from .components.text import Text


def query_in_children(node, **attrs):
    """
    Query in each children of a given node and returns all itens found.

    It will execute query for each child of the given node with the given attrs.
    If a child is a Text tag, it will be ignored.
    If the query return isn't None then it is added to found list.
    """
    sub_queries = []

    for child in node.children:
        if isinstance(child, Text):
            continue

        sub_queries.extend(query(child, **attrs))

    return sub_queries


def query_for_attrs(node, **attrs):
    """
    Verify if the given node, has all the given attribrutes.

    If all given attributes were found in the given node,
    then returns the given node otherwise None

    Ex:
        node = button(class_='btn btn-success', onclick='alert(123)') [ 'Click here !' ]
        query_for_attrs(node, {'onclick': 'alert(123)'})
    """
    keys_found = 0

    for key in attrs:
        if key in node.attrs.keys() \
        and attrs[key] == node.attrs[key]:
            keys_found += 1

    return keys_found == len(attrs)


def tag_compare_factory(tag):
    """
    Verifies if a method receives a tag by parameter and returns True or False.
    """
    return lambda brick: brick.tag_name == tag


def class_compare_factory(class_):
    """
    Verifies if a method receives a class_ by parameter and returns True or False.
    """
    return lambda brick: "".join(brick.classes) == class_


def other_attrs_compare_factory(**attrs):
    """
    Verifies if a method receives an attr by parameter and returns True or False.
    """
    return lambda brick: query_for_attrs(brick, **attrs)


def join_factories(*factories):
    """
    Verifies if all methods that will be used receives attrs, class_ or tags.
    """
    return lambda brick: all(fn(brick) for fn in factories)


def query(node, **attrs):
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
    factories = []
    attrs_copy = attrs.copy()

    if 'tag' in attrs.keys():
        attrs_copy.pop('tag')
        factories.append(tag_compare_factory(attrs['tag']))

    if 'class_' in attrs.keys():
        attrs_copy.pop('class_')
        factories.append(class_compare_factory(attrs['class_']))

    factories.append(other_attrs_compare_factory(**attrs_copy))

    if join_factories(*factories) (node):
        found.append(node)

    found.extend(query_in_children(node, **attrs))

    return found
