"""
Serialize/deserialize Bricks flavored JSON (see :ref:`json`).

Functions
---------

.. autofunction:: bricks.json.encode
.. autofunction:: bricks.json.decode
.. autofunction:: bricks.json.dumps
.. autofunction:: bricks.json.loads
.. autofunction:: bricks.json.register


Errors
------

.. autoclass:: JSONDecodeError
.. autoclass:: JSONEncodeError

"""
from .exceptions import JSONDecodeError, JSONEncodeError
from .encoders import encode
from .decoders import decode
from .common import register, dumps, loads
