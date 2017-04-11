from lazyutils import lazy

from bricks.require import Asset


class DataAsset(Asset):
    """
    Base class for all assets that provide a link to a static resource.
    """

    @lazy
    def link(self):
        if self.href:
            return self.href
        else:
            return 'static/' + self.static

    def __init__(self, name, static=None, source=None, href=None, **kwargs):
        count = (static is not None) + (source is not None) + (href is not None)
        if count != 1:
            raise TypeError(
                'must define one and at most one of static, source, '
                'href arguments')
        self.static = static
        self.source = source
        self.href = href
        super().__init__(name, **kwargs)


class JsAsset(DataAsset):
    """
    Javascript file or <script> tag resource.
    """

    def __init__(self, name, header=True, **kwargs):
        super().__init__(name, **kwargs)
        self.header = header

    def render_js(self):
        if self.link:
            return '<script src="%s"></script>' % self.link
        elif self.source:
            return '<script>%s</script>' % self.source
        else:
            raise ValueError('invalid js asset')

    def render_js_header(self):
        if self.header:
            return self.render_js()

    def render_js_footer(self):
        if not self.header:
            return self.render_js()


class JsOnLoadAsset(Asset):
    """
    Javascript source that must be inserted inside a load callback.
    """


class CssAsset(DataAsset):
    """
    CSS file or <style> tag resource.
    """

    def render_css(self):
        if self.href:
            return '<link rel="stylesheet" href="%s"/>' % self.href
        elif self.source:
            return '<style>%s</style>' % self.source
        else:
            raise ValueError('invalid css asset')