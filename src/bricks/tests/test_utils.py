from collections import OrderedDict

from bricks.utils import lazy_singledispatch


def test_single_dispatch_example():
    @lazy_singledispatch
    def foo(x):
        return 42

    @foo.register(str)
    def _(x):
        return x

    @foo.register('collections.OrderedDict')
    def _(x):
        return dict(x)

    d = OrderedDict({3: 'three'})
    assert foo(1) == 42
    assert foo('two') == 'two'
    assert foo(d) == d
