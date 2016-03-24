# Using asyncio as a main module

try:
    import asyncio
except ImportError:
    import trollius as asyncio

import Pyjo.Reactor.Asyncio
import Pyjo.IOLoop


asyncio_loop = asyncio.get_event_loop()

# asyncio.get_event_loop() is used by first Pyjo.Reactor.Asyncio object by
# default. Explicit usage:
# Pyjo.IOLoop.singleton = Pyjo.IOLoop.new(reactor=Pyjo.Reactor.Asyncio.new(loop=loop))


counter = 0


def stop_after_all_events():
    global counter
    counter += 1
    if counter == 2:
        asyncio_loop.stop()


@Pyjo.IOLoop.timer(1)
def hello_pyjo(loop):
    print("This message is from Pyjo")
    stop_after_all_events()


def hello_asyncio_cb():
    print("This message is from asyncio")
    stop_after_all_events()

asyncio_loop.call_later(1, hello_asyncio_cb)


asyncio_loop.run_forever()
