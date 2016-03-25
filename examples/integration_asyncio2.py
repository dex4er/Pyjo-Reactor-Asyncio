# Using asyncio as a main module

try:
    import asyncio
except ImportError:
    import trollius as asyncio

import Pyjo.Reactor.Asyncio
import Pyjo.IOLoop


asyncio_loop = asyncio.get_event_loop()
pyjo_reactor = Pyjo.Reactor.Asyncio.new(loop=asyncio_loop)
Pyjo.IOLoop.singleton = Pyjo.IOLoop.new(reactor=pyjo_reactor)


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

asyncio_loop.call_later(2, hello_asyncio_cb)


# Pyjo.IOLoop will not stop asyncio loop because was provided as param for Pyjo reactor
asyncio_loop.run_forever()
asyncio_loop.close()
