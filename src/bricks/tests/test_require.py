from bricks.require import Asset, possible_assets, require_assets, AssetManager, \
    JsAsset, CssAsset


def test_require_simple_library():
    assert require_assets('jquery.js') == possible_assets('jquery.js')


def test_require_simple_library_by_bundle():
    assert require_assets('jquery') == possible_assets('jquery.js')


def test_require_bundled_library():
    assert require_assets('bootstrap') == possible_assets('bootstrap.css') + \
                                          possible_assets('bootstrap.js')


def test_multiple_requires():
    assert require_assets('bootstrap', 'jquery') == \
           possible_assets('bootstrap.css') + \
           possible_assets('bootstrap.js') + \
           possible_assets('jquery.js')


def test_asset_with_deps():
    main = JsAsset('with-deps.js',
                   requires=['jquery', 'bootstrap'],
                   static='with-deps.js')
    assets = require_assets('with-deps.js')
    expected = possible_assets('jquery.js') + \
               possible_assets('bootstrap.css') + \
               possible_assets('bootstrap.js') + \
               [main]
    print(assets)
    print(expected)
    assert assets == expected
    Asset.clear_assets('with-deps.js', 'with-deps')


def test_complex_asset():
    mgm = AssetManager()
    JsAsset('main.js',
            provides=['jquery.js', 'material-design-lite.js'],
            static='/static/js/main.js')
    CssAsset('main.css',
             provides=['material-design-lite.css'],
             static='/static/css/main.css')

    mgm.require('main', 'jquery', 'material-design-lite', 'handlebars')
    assets = mgm.resolve_dependencies()
    expected = possible_assets('main.js') + possible_assets(
        'main.css') + possible_assets('handlebars.js')
    print(assets)
    print(expected)
    assert assets == expected
