"""
JSON-RPC 2.0 utilities.

Functions and decorators
------------------------

.. autofunction:: jsonrpc_endpoint

Generic views
-------------

.. autoclass:: RPCView
   :members:

"""

from .views import RPCView, jsonrpc_endpoint
from .decorators import route
