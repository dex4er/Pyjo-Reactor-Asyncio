try:
    import asyncio
except ImportError:
    import trollius as asyncio


loop = asyncio.get_event_loop()


def writer_cb(loop):
    print("A")
    loop.call_soon(writer_cb, loop)

loop.call_soon(writer_cb, loop)


def timeouter_cb(loop):
    loop.stop()

loop.call_later(1, timeouter_cb, loop)

loop.run_forever()
