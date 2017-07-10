from .components.text import Text


def query_for_attrs(node, **attrs):
    keys_found = 0

    for key in attrs:
        if key in node.attrs.keys() \
        and attrs[key] == node.attrs[key]:
            keys_found += 1

    return keys_found == len(attrs)


def query(node, **attrs):
    found = []
    factories = []
    attrs_copy = attrs.copy()

    if 'tag' in attrs.keys():
        attrs_copy.pop('tag')

        factories.append(
            lambda brick: brick.tag_name == attrs['tag']
        )

    if 'class_' in attrs.keys():
        attrs_copy.pop('class_')

        factories.append(
            lambda brick: "".join(brick.classes) == attrs['class_']
        )

    factories.append(
        lambda brick: query_for_attrs(brick, **attrs_copy)
    )

    if all(fn(node) for fn in factories):
        found.append(node)

    for child in node.children:
        if isinstance(child, Text):
            continue

        found.extend(query(child, **attrs))


    return found
