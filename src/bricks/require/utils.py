from contextlib import contextmanager

from bricks.require import Asset, AssetManager


def possible_assets(name):
    """
    Return all assets associated with the given name.
    """

    return Asset.possible_assets(name)


def require(asset, context):
    """
    Requires asset
    """


def require_assets(*args):
    """
    Return a list of assets that fulfill the given requirements.

    Example:

        >>> require_assets('jquery')
        [JsAsset('jquery.js')]
    """

    manager = AssetManager()
    manager.require(*args)
    return manager.assets


def require_to_html(*args):
    """
    Return a tuple with (head, foot) parts of HTML strings that should be
    included both in the <head> of an HTML document and in the end of its <body>
    tag.

    Example:
        >>> head, foot = require_to_html('jquery', 'bootstrap')
        >>> print('''<html>
        ...   <head>
        ...     {head}
        ...   </head>
        ...   <body>
        ...     <h1>Hello world!</h1>
        ...     {foot}
        ...   </body>
        ... </html>
        ... '''.format(head=head, foot=foot))
        <html>
          <head>
            <...>
          </head>
          <body>
            <h1>Hello world!</h1>
            ...
          </body>
        </html>
    """

    manager = AssetManager()
    manager.require(*args)
    return manager.render_head(), manager.render_foot()


@contextmanager
def capture_assets():
    """
    Capture assets required for all components declared within the with block.
    """

    mgm = AssetManager()
    mgm.capture()
    try:
        yield mgm
    finally:
        mgm.release()