from bricks.require import JsAsset, CssAsset

# Most common javascript libraries as global assets that supports CDN. We try
# to support the latest version and to provide different versions for each
# library. Support may vary between libraries.

# jQuery
JsAsset('jquery.js',
        href='https://code.jquery.com/jquery-2.2.4.min.js')

# jQuery UI
CssAsset('jquery-ui.css',
         href='http://code.jquery.com/ui/1.12.0/'
              'themes/smoothness/jquery-ui.css')
JsAsset('jquery-ui.js',
        href='http://code.jquery.com/ui/1.12.0/jquery-ui.min.js')

# Bootstrap
CssAsset('bootstrap.css',
         href='https://cdnjs.cloudflare.com/ajax/libs/'
              'twitter-bootstrap/4.0.0-alpha.5/css/bootstrap.min.css')
JsAsset('bootstrap.js',
        href='https://cdnjs.cloudflare.com/ajax/libs/'
             'twitter-bootstrap/4.0.0-alpha.5/js/bootstrap.min.js')

# Underscore


# Blackbone


# Handlebars
JsAsset('handlebars.js',
        href='https://cdnjs.cloudflare.com/ajax/libs/'
             'handlebars.js/4.0.6/handlebars.min.js')

# Material Design Lite
JsAsset('material-design-lite.js',
        href='dsfsd.js')
CssAsset('material-design-lite.css',
         href='mdl.css')


# Maybe others ...
# Please contribute!
