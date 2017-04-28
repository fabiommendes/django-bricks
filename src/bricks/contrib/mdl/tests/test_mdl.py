from bricks.contrib.mdl import badge, button, div


class TestGeneric:
    def test_mdl_div_accepts_shadows(self):
        assert str(div()) == '<div></div>'
        assert str(div(shadow=2)) == '<div class="mdl-shadow--2dp"></div>'


class TestButton:
    def test_button_renders_correctly(self):
        btn = button('foo')
        assert btn.classes == ['mdl-button', 'mdl-js-button']
        assert str(
            btn) == '<button class="mdl-button mdl-js-button">foo</button>'

    def test_button_accepts_children(self):
        assert button()['foo'] == button('foo')

    def test_button_modifiers(self):
        btn = button('foo', ripple=True)
        assert btn.classes == ['mdl-button', 'mdl-js-button',
                               'mdl-js-ripple-effect']

        btn = button('foo', raised=True, disabled=True)
        assert btn.classes == ['mdl-button', 'mdl-js-button',
                               'mdl-button--raised']
        assert btn.attrs['disabled'] is True


class TestBadge:
    def test_badge_renders_correctly(self):
        obj = badge('foo', '42')
        assert obj.classes == ['mdl-badge']
        assert str(obj) == '<span class="mdl-badge" data-badge="42">foo</span>'
