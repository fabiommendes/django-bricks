from bricks.components.css import Css, CssId, dict_to_css


def src(st):
    """
    Normalize source results.
    """

    return '\n'.join(line[4:] for line in st[1:].splitlines())[:-1]


def test_can_create_css_manually():
    css = Css()
    css.add(CssId('foo', {'font-size': '1em'}))
    assert str(css) == src('''
    #foo {
        font-size: 1em;
    }
    ''')


def test_can_convert_dict_to_css():
    css = dict_to_css({
        '#foo': {
            'font-family': 'Verdana sans',
        }
    })

    assert len(css) == 1
    assert str(css) == src("""
    #foo {
        font-family: Verdana sans;
    }
    """)
