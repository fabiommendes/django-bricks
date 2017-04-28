============================
Remote Procedure Calls (RPC)
============================

Bricks provides a module for simple RPC based on the `JSON-RPC 2.0 spec <http://www.jsonrpc.org/specification>`. The
module implements views that can be used either by the frontend through our
JavaScript library or by other Python programs to call Bricks RPC endpoints.
The later can be useful in a distributed server architecture, where one server
can call endpoints defined by other.

