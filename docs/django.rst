====================
Django configuration
====================

The first step is to add Bricks to your installed apps::

    # settings.py
    # ...

    INSTALLED_APPS = [
        'bricks.app',
    ]


Django Bricks requires a working Jinja2 template engine, even if your project
only uses Django templates as the main rendering engine.