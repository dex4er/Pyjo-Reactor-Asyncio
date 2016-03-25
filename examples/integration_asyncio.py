# Using Pyjo.Reactor.Asyncio as a main module

import Pyjo.Reactor.Asyncio
import Pyjo.IOLoop


asyncio_loop = Pyjo.IOLoop.singleton.reactor.loop


@Pyjo.IOLoop.timer(2)
def hello_pyjo(loop):
    print("This message is from Pyjo")


def hello_asyncio_cb():
    print("This message is from asyncio")

asyncio_loop.call_later(1, hello_asyncio_cb)


# Pyjo.IOLoop will stop asyncio loop if there is no Pyjo timers or io watchers
Pyjo.IOLoop.start()
