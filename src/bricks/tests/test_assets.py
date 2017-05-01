import pytest

from bricks.assets import Asset, AssetManager, require_deep, lib, Link, Script, \
    BottomScript
from bricks.assets.asset import ASSET_REGISTRY
from bricks.assets.utils import rel_from_href, type_from_href
from bricks.html5 import div, p, h1


@pytest.yield_fixture
def registry_rollback(self):
    registry = ASSET_REGISTRY.copy()
    ASSET_REGISTRY.clear()
    yield ASSET_REGISTRY
    ASSET_REGISTRY.clear()
    ASSET_REGISTRY.update(registry)


@pytest.fixture
def elem():
    elem = \
        div()[
            p('foo'),
            h1('bar'),
            p('foo bar'),
        ]
    elem.requires = ['foo']
    elem.children[0].requires = ['bar']
    return elem


class TestTools:
    def test_require_deep_in_a_simple_element(self, elem):
        assert require_deep(elem) == ['foo', 'bar']

    def test_rel_from_href_known(self):
        assert rel_from_href('main.css') == 'stylesheet'

    def test_rel_from_invalid_href(self):
        with pytest.raises(ValueError):
            rel_from_href('main.pytg')

    def test_type_from_href_known(self):
        assert type_from_href('main.css') == 'text/css'
        assert type_from_href('main.pytg') == 'text/pytg'


class TestAsset:
    """
    Test asset instances
    """

    pytestmark = pytest.mark.usefixtures(registry_rollback)

    @pytest.fixture
    def asset(self):
        return Asset('asset', ['spam', 'eggs'])

    @pytest.fixture
    def full_asset(self, asset):
        return Asset('full_asset',
                     requires=['foo', 'bar'],
                     provides=['ham', 'spam'],
                     suggests={'eggs': asset})

    def test_can_load_global_asset(self, asset):
        assert Asset.load('eggs') == asset

    def test_fails_for_unknown_asset(self):
        with pytest.raises(ValueError):
            Asset.load('unknown-asset')

    def test_basic_hash_and_equality(self, asset):
        a1 = Asset('foo')
        a2 = Asset('foo')
        assert a1 == a2
        assert a1 != asset
        assert a1 != None
        assert hash(a1) == hash(a2)
        assert hash(a1) != hash(asset)

    def test_asset_repr(self, full_asset, asset):
        st = repr(full_asset)
        assert st == "Asset('full_asset', ['ham', 'spam'])"
        assert str(Asset('foo')) == "Asset('foo')"
        assert str(Asset('foo', requires=['bar'])) == \
               "Asset('foo', requires=['bar'])"
        assert str(Asset('foo', suggests={'ham': asset})) == \
               "Asset('foo', suggests={'ham': asset})"

    def test_make_link_asset(self):
        css = Link('style', href='css/main.css')
        tag = css.tag()
        assert tag.tag_name == 'link'
        assert tag.attrs == {
            'href': 'css/main.css',
            'rel': 'stylesheet',
            'type': 'text/css',
        }

    def test_make_bottom_script_asset_from_script_asset(self):
        a1 = Script('foo', 'foo.js')
        a2 = BottomScript(a1)
        assert a2.name == 'foo-bottom'
        assert a2.provides == {'foo'}


class TestAssetManager:
    pytestmark = pytest.mark.usefixtures(registry_rollback)
    asset = TestAsset.asset
    full_asset = TestAsset.full_asset

    @pytest.fixture
    def manager(self):
        return AssetManager()

    def test_manager_loads_asset_requires(self, manager, asset):
        manager.load(asset)
        assert asset in manager.assets
        assert manager.requires == list(asset.requires)
        assert manager.provides == set(asset.provides)
        assert manager.suggests == dict(asset.suggests)
        assert manager.assets == [asset]

    def test_manager_loading_asset_is_idempotent(self, manager, asset):
        manager.load(asset)
        manager.load(asset)
        assert manager.assets == [asset]

    def test_manager_loads_asset_properties(self, manager, full_asset):
        self.test_manager_loads_asset_requires(manager, full_asset)

    def test_load_global_after_requiring_deps(self, manager):
        asset1 = Asset('asset1', provides=['foo', 'bar'], requires=['ham'])
        asset2 = Asset('asset2', provides=['ham', 'eggs'])

        manager.load(asset1)
        manager.resolve()
        assert manager.provides == {'foo', 'bar', 'ham', 'eggs'}
        assert manager.requires == []
        assert manager.assets == [asset1, asset2]

    def test_manager_require(self, manager):
        asset1 = Asset('asset1', provides=['foo', 'bar'], requires=['ham'])
        asset2 = Asset('asset2', provides=['ham', 'eggs'])

        manager.require('foo', 'bar')
        assert manager.provides == {'foo', 'bar', 'ham', 'eggs'}
        assert manager.requires == []
        assert manager.assets == [asset1, asset2]

    def test_manager_repr(self, manager, full_asset):
        manager.load(full_asset)
        assert repr(manager) == \
               "AssetManager([full_asset], requires=['foo', 'bar'], " \
               "provides={'ham', 'spam'}, suggests={'eggs': asset})"

    def test_manager_require_from_element(self, manager, elem):
        asset1 = Asset('asset1', provides=['foo', 'bar'])
        manager.require_from(elem)
        assert manager.assets == [asset1]

    def test_prefers_later_assets(self, manager):
        a1 = Asset('a1', ['foo'])
        a2 = Asset('a2', ['foo'])
        manager.require('foo')
        assert manager.assets == [a2]

    def test_loads_suggested_assets_first(self, manager):
        a1 = Asset('a1', ['foo'])
        a2 = Asset('a2', ['foo'])
        a3 = Asset('a3', requires=['foo'], suggests={'foo': a1})
        manager.load(a3)
        manager.resolve()
        assert manager.assets == [a3, a1]

    def test_incomplete_suggestions(self, manager):
        a1 = Asset('a1', ['foo'], requires=['bar'])
        manager.load(a1)
        manager.resolve_suggested()
        assert manager.requires == ['bar']


class TestCommonAssets:
    pytestmark = pytest.mark.usefixtures(registry_rollback)

    def test_render_js_tag(self):
        asset = lib.jquery_js
        tag = asset.tag()
        assert tag.attrs['src'].startswith('https://code.jquery.com/jquery-')
        assert not tag.children
        assert 'type' not in tag.attrs

    def test_render_css_tag(self):
        asset = lib.jquery_ui_css_base
        tag = asset.tag()
        assert tag.attrs['href'].startswith('https://code.jquery.com/ui/')
        assert sorted(tag.attrs.keys()) == ['href', 'rel', 'type']
        assert tag.tag_name == 'link'
