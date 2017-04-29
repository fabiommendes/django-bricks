.. _json:

====================
Bricks flavored JSON
====================

Bricks uses JSON as a data serialization format for server/client and P2P
communication. JSON is obviously constrained to just a few primitive data types.
In order to serialize more complex data, it is usually necessary to transform it
to a JSON-friendly format such as a dictionary or list (a.k.a Objects and
Arrays, in JavaScript parlance).

This approach is fine if the receiving end of communication knows exactly which
kind of data to expect and how to construct the desired object from JSON. Bricks
defines a simple protocol to handle extension types: all non-primitive types
must define an '@' key mapping to the extension type name.

.. code-block:: python

   {
      '@': 'datetime',
      'year': 1982,
      'month': 1,
      'day': 6,
      'hour': 12,
      'minute': 52,
      'second': 0,
      'microsecond': 0,
   }

Of course both ends of communication must still agree on how to
serialize/deserialize this data type. Bricks makes no attempt to define an schema
or any kind of formal description of a data type and its validation. These are
orthogonal concerns that could be handled by third party libraries.

Bricks implements transformation for a few common Python types (such as the
datetime example given bellow) and **bricks.js** handles them in Javascript when
feasible.


The :mod:`bricks.json` module
=============================

The :mod:`bricks.json` provides basic functions for manipulating JSON data.

Conversion from/to JSON is handled by the :func:`bricks.json.decode` and :func:`brick.json.encode`
functions:

>>> from bricks.json import encode, decode
>>> encode({1, 2, 3})                                           # doctest: +SKIP
{
    '@': 'set',
    'data': [1, 2, 3],
}
>>> decode({'@': 'set', 'data': [1, 2, 3]})                     # doctest: +SKIP
{1, 2, 3}


.. _json-custom-types:


Custom types
============

Support for custom types is given by the