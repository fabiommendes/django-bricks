from .assets import Asset, Script, BottomScript, Css

# Aliases
js = Script
jsb = BottomScript
css = Css
req = lambda name, *reqs: Asset(name, [name], requires=reqs)

# Most common javascript libraries as global assets that supports CDN. We try
# to support the latest version and to provide different versions for each
# library. Support may vary between libraries.

# Here we declare a few common CDNs
_cloudfare = 'https://cdnjs.cloudflare.com/ajax/libs/'

# ------------------------------------------------------------------------------
# This file is divided in sections:
#
#   * DOM manipulation
#   * Fonts and icons
#   * Frameworks
#   * Functional and algorithms
#   * Templating
#   * Styling
#

# ==============================================================================
# DOM MANIPULATION
#   - jquery, jquery UI
# ==============================================================================


# ------------------------------------------------------------------------------
# jQuery
#
_version = '3.2.1'
jquery_js = \
    jsb('jquery.js',
        src='https://code.jquery.com/jquery-%s.min.js' % _version)
jquery = req('jquery', 'jquery.js')

# ------------------------------------------------------------------------------
# jQuery UI
#
_version = '1.12.1'
_prefix = 'https://code.jquery.com/ui/%s/' % _version

# CSS (all themes from the CDN).
# The default theme is "base". It is ugly, but then almost all themes are :)
_theme = lambda theme: \
    css('jquery-ui-%s.css' % theme,
        href=_prefix + 'themes/%s/jquery-ui.min.css' % theme,
        provides=['jquery-ui-%s.css' % theme, 'jquery-ui.css'])
jquery_ui_css_base = _theme('base')
jquery_ui_css_black_tie = _theme('black-tie')
jquery_ui_css_blitzer = _theme('blitzer')
jquery_ui_css_cupertino = _theme('cupertino')
jquery_ui_css_dark_hive = _theme('dark-hive')
jquery_ui_css_dot_luv = _theme('dot-luv')
jquery_ui_css_eggplant = _theme('eggplant')
jquery_ui_css_excite_bike = _theme('excite-bike')
jquery_ui_css_flick = _theme('flick')
jquery_ui_css_hot_sneaks = _theme('hot-sneaks')
jquery_ui_css_humanity = _theme('humanity')
jquery_ui_css_le_frog = _theme('le-frog')
jquery_ui_css_mint_choc = _theme('mint-choc')
jquery_ui_css_overcast = _theme('overcast')
jquery_ui_css_pepper_grinder = _theme('pepper-grinder')
jquery_ui_css_redmond = _theme('redmond')
jquery_ui_css_smoothness = _theme('smoothness')
jquery_ui_css_south_street = _theme('south-street')
jquery_ui_css_start = _theme('start')
jquery_ui_css_sunny = _theme('sunny')
jquery_ui_css_swanky_purse = _theme('swanky-purse')
jquery_ui_css_trontastic = _theme('trontastic')
jquery_ui_css_ui_darkness = _theme('ui-darkness')
jquery_ui_css_ui_lightness = _theme('ui-lightness')
jquery_ui_css_vader = _theme('vader')
jquery_ui_css = Asset('jquery-ui.css', ['jquery-ui.css'],
                      requires=['jquery-ui-base.css'])

# Javascript
jquery_ui_js = \
    jsb('jquery-ui.js',
        src=_prefix + 'jquery-ui.min.js',
        requires=['jquery'])
jquery_ui = req('jquery_ui', 'jquery-ui.css', 'jquery-ui.js')

# ==============================================================================
# FONTS AND ICONS
#   - font-awesome, google, material-icons
# ==============================================================================

# ------------------------------------------------------------------------------
# Font-awesome
#
_version = '4.7.0'
_prefix = _cloudfare + 'font-awesome/%s/' % _version
font_awesome_css = \
    css('font-awesome.css',
        href=_prefix + 'font-awesome.min.css')
font_awesome = req('font-awesome', 'font-awesome.css')

# ------------------------------------------------------------------------------
# Google fonts
#

_font = lambda x: \
    css('%s-font' % x.lower().replace('+', '-'),
        href='https://fonts.googleapis.com/css?family=%s' % x)

# Just a few random fonts that I happen to use. New contributions are always
# welcome.
roboto_font = _font('Roboto')
roboto_mono_font = _font('Roboto+Mono')
lato_font = _font('Lato')
amatic_sc_font = _font('Amatic+SC')
google_fonts = req('google-fonts', 'roboto-font', 'roboto-mono', 'lato')

# ------------------------------------------------------------------------------
# Material Icons
#
material_icons_css = \
    css('material-icons.css',
        href='https://fonts.googleapis.com/icon?family=Material+Icons')
material_icons = req('material-icons', 'material-icons.css')

# ==============================================================================
# FRAMEWORKS
#   - jquery, jquery UI, (D3, ...)
# ==============================================================================

# ------------------------------------------------------------------------------
# Vue
#
vue_js = jsb('vue.js', src='https://unpkg.com/vue')
vue = req('vue', 'vue.js')

# ==============================================================================
# FUNCTIONAL AND ALGORITHMS
#   - lodash, underscore
# ==============================================================================

# ------------------------------------------------------------------------------
# Materialize
#
_version = '1.8.3'
_prefix = _cloudfare + 'underscore/%s/' % _version

underscore_css = \
    css('underscore.css',
        href=_prefix + 'css/underscore-min.css')
underscore_js = \
    jsb('underscore.js',
        src=_prefix + 'js/underscore-min.js')
underscore = req('underscore', 'underscore.js', 'underscore.css')

# ==============================================================================
# TEMPLATING
#   - handlebars
# ==============================================================================

# ------------------------------------------------------------------------------
# Handlebars
#
handlebars_js = \
    js('handlebars.js',
       src=_cloudfare + 'handlebars.js/4.0.6/handlebars.min.js')
handlebars = req('handlebars', 'handlebars.js')

# ==============================================================================
# STYLING
#   - bootstrap, mdl,
# ==============================================================================

# ------------------------------------------------------------------------------
# Bootstrap
#
_version = '4.0.0-alpha.6'
_prefix = _cloudfare + 'twitter-bootstrap/%s/' % _version
bootstrap_css = \
    css('bootstrap.css',
        href=_prefix + 'css/bootstrap.min.css')
bootstrap_js = \
    jsb('bootstrap.js',
        src=_prefix + 'js/bootstrap.min.js')
bootstrap = req('bootstrap', 'bootstrap.css', 'bootstrap.js')

# ------------------------------------------------------------------------------
# Material Design Lite
#
_version = '1.3.0'
_prefix = 'https://code.getmdl.io/%s/' % _version

# Themes (we only support the default for now).
# See jQuery UI if you want to implement various themes for MDL too.
mdl_css = \
    css('mdl.css',
        href=_prefix + 'material.indigo-pink.min.css',
        requires=['material-icons'])
mdl_js = \
    jsb('mdl.css',
        src=_prefix + 'material.min.js')
mdl = req('mdl', 'mdl.css', 'mdl.js')

# ------------------------------------------------------------------------------
# Materialize
#
_version = '0.98.2'
_prefix = _cloudfare + 'materialize/%s/' % _version

materialize_css = \
    css('materialize.css',
        href=_prefix + 'css/materialize.min.css')
materialize_js = \
    jsb('materialize.js',
        src=_prefix + 'js/materialize.min.js')
materialize = req('materialize', 'materialize.js', 'materialize.css')


# ------------------------------------------------------------------------------
# Other libraries go here...
# Please contribute ;-)
