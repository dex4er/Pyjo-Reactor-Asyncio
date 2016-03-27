.. image:: https://img.shields.io/pypi/v/Pyjo-Reactor-Asyncio.png
   :target: https://pypi.python.org/pypi/Pyjo-Reactor-Asyncio
.. image:: https://travis-ci.org/dex4er/Pyjo-Reactor-Asyncio.png?branch=master
   :target: https://travis-ci.org/dex4er/Pyjo-Reactor-Asyncio
.. image:: https://readthedocs.org/projects/pyjo-reactor-asyncio/badge/?version=latest
   :target: http://pyjo-reactor-asyncio.readthedocs.org/en/latest/

Pyjo-Reactor-Asyncio
====================

Low level event reactor with asyncio support for Pyjoyment.


Pyjoyment
=========

An asynchronous, event driver web framework for the Python programming language.

Pyjoyment provides own reactor which handles I/O and timer events in its own
main event loop but it supports other loops, ie. *libev* or *asyncio*.

See http://www.pyjoyment.net/


asyncio
=======

This module provides infrastructure for writing single-threaded concurrent code
using coroutines, multiplexing I/O access over sockets and other resources,
running network clients and servers, and other related primitives.

The asyncio module was designed in PEP3156_. For a motivational primer on
transports and protocols, see PEP3153_.

See http://asyncio.org/

.. _PEP3153: https://www.python.org/dev/peps/pep-3153/
.. _PEP3156: https://www.python.org/dev/peps/pep-3156/


Trollius
========

Trollius is a portage of the asyncio project (PEP3156_) on Python 2.
Trollius works on Python 2.6-3.5.

See https://trollius.readthedocs.org/


Examples
========

Non-blocking TCP client/server
------------------------------

.. code-block:: python

   import Pyjo.Reactor.Asyncio
   import Pyjo.IOLoop


   # Listen on port 3000
   @Pyjo.IOLoop.server(port=3000)
   def server(loop, stream, cid):

       @stream.on
       def read(stream, chunk):
           # Process input chunk
           print("Server: {0}".format(chunk.decode('utf-8')))

           # Write response
           stream.write(b"HTTP/1.1 200 OK\x0d\x0a\x0d\x0a")

           # Disconnect client
           stream.close_gracefully()


   # Connect to port 3000
   @Pyjo.IOLoop.client(port=3000)
   def client(loop, err, stream):

       @stream.on
       def read(stream, chunk):
           # Process input
           print("Client: {0}".format(chunk.decode('utf-8')))

       # Write request
       stream.write(b"GET / HTTP/1.1\x0d\x0a\x0d\x0a")


   # Add a timer
   @Pyjo.IOLoop.timer(3)
   def timeouter(loop):
       print("Timeout")
       # Shutdown server
       loop.remove(server)


   # Start event loop
   Pyjo.IOLoop.start()
