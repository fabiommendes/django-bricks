from .components.text import Text


def query_in_children(node, **attrs):
    sub_queries = []

    for child in node.children:
        if isinstance(child, Text):
            continue

        sub_queries.extend(query(child, **attrs))

    return sub_queries


def query_for_attrs(node, **attrs):
    keys_found = 0

    for key in attrs:
        if key in node.attrs.keys() \
        and attrs[key] == node.attrs[key]:
            keys_found += 1

    return keys_found == len(attrs)


def tag_compare_factory(tag):
    return lambda brick: brick.tag_name == tag


def class_compare_factory(class_):
    return lambda brick: "".join(brick.classes) == class_


def other_attrs_compare_factory(**attrs):
    return lambda brick: query_for_attrs(brick, **attrs)


def join_factories(*factories):
    return lambda brick: all(fn(brick) for fn in factories)


def query(node, **attrs):
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
