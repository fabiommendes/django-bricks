Creating components
===================

Generating HTML is only a part of a pluggable component.

Take a simple HTML reusable component such as a jQuery date picker. In Bricks
we can provide a nice functional interface that creates a datepicker <input>
element such as

.. code-block:: html

    <input class="jquery-ui-datepicker" id="birthday">

While this is simple enough to generate, it is still very much inadequate. It
order to use the component, we need to take care of a few things

* Load the correct jQuery-ui Javascript.
* Initialize the jQuery component in Javascript.

The component must somehow advertise that it requires some assets and that some
actions must be taken to correctly initialize the component. This is acomplished
by the requires + init interfaces.


Requires
--------

Each component in Bricks defines a .requires attribute that is a simple sequence
describing all assets required by the component to properly function. Each
asset is represented by a simple string, such as in the example.

>>> from bricks.contrib.jquery_ui import DatePicker
>>> datepicker = DatePicker()
>>> datepicker.requires
['jquery-ui-datepicker']

The :func:`bricks.requires.collect` collects the list of all requirements from
a root element. It walks through all nodes and adds the requirement strings in
order.

This method, per se, does not accomplish anything. Elements can advertise what
they need, but we do not have any way of actually loading these dependencies on
a page. The second part is the responsibility of asset managers.

An Asset instance represents a resource associated with some labels. Assets can
have dependencies and may require other elements using asset label strings.
We can, for instance, provide a ``jquery_cdn_asset``, that tells how to download
jQuery from the CDN and we might associate it with the 'jquery.js' asset label.
So an element that requires 'jquery.js' can have this requirement fulfilled by
the ``jquery_cdn_asset`` object.

This is coordinated by an instance of :cls:`bricks.assets.AssetManager`:

>>> from bricks.assets import AssetManager
>>> manager = AssetManager()

Once we have a manager, it is time to load some assets:

>>> from bricks.contrib.jquery_ui import cdn_asset
>>> manager.load(cdn_asset)

This method will load the cdn_asset of jquery_ui and automatically register all
of its dependencies. Any asset instance or the asset manager itself have three
attributes, ``.requires``, ``.provides`` and ``.suggests``. The first two are
a sequence of labels required or provided by the given asset. The later one is a
dictionary mapping labels with suggested assets:

>>> cdn_asset.requires
['jquery.js']
>>> cdn_asset.provides
{'jquery-ui', 'jquery-ui.css', 'jquery-ui.js'}
>>> cdn_asset.suggests
{}

The ``.requires`` attribute of a manager is just a list of all requirements that
were not resolved yet. Once it loads an asset that provides any of those
requirements, they disappear from the ``.requires`` list. The manager have a
``.resolve()`` method that will try to load all necessary assets by searching
for assets in a global registry. If it succeeds, the ``.requires`` list will be
empty.

>>> manager.resolve()  # this will trigger loading some assets
>>> manager.requires
[]
>>> manager.assets                                          # doctest: +ELLIPSIS
[CdnAsset('jquery'), ...]

A second important way of interacting with the manager is pushing some
requirements explicitly. The ``.require()`` method adds some requirements to
the ``.requires`` list and immediately calls the ``.resolve()`` method.

>>> manager.require(['mdl.js', 'mdl.css'])

Similarly, we can require dependencies from an HTML component. The manager will
walk through all children and collect all dependencies it finds:

>>> manager.require_from(my_page)                               # doctest: +SKIP
