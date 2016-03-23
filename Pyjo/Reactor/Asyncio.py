"""
Pyjo.Reactor.Asyncio - Low-level event reactor with asyncio support
===================================================================
::

    import Pyjo.Reactor.Asyncio

    # Watch if handle becomes readable or writable
    reactor = Pyjo.Reactor.Asyncio.new()

    def io_cb(reactor, writable):
        if writable:
            print('Handle is writable')
        else:
            print('Handle is readable')

    reactor.io(io_cb, handle)

    # Change to watching only if handle becomes writable
    reactor.watch(handle, read=False, write=True)

    # Add a timer
    def timer_cb(reactor):
        reactor.remove(handle)
        print('Timeout!')

    reactor.timer(timer_cb, 15)

    # Start reactor if necessary
    if not reactor.is_running:
        reactor.start()

:mod:`Pyjo.Reactor.Asyncio` is a low-level event reactor based on :mod:`asyncio`.

:mod:`Pyjo.Reactor.Asyncio` will be used as the default backend for
:mod:`Pyjo.IOLoop` if it is loaded before any module using the loop or if
the ``PYJO_REACTOR`` environment variable is set to ``Pyjo.Reactor.Asyncio`` value.

Debugging
---------

You can set the ``PYJO_REACTOR_DEBUG`` environment variable to get some
advanced diagnostics information printed to ``stderr``. ::

    PYJO_REACTOR_DEBUG=1

You can set the ``PYJO_REACTOR_DIE`` environment variable to make reactor die if task
dies with exception. ::

    PYJO_REACTOR_DIE=1

Events
------

:mod:`Pyjo.Reactor.Asyncio` inherits all events from :mod:`Pyjo.Reactor.Select`.

Classes
-------
"""

import Pyjo.Reactor.Base
import Pyjo.Reactor.Select

import importlib

try:
    import asyncio
except ImportError:
    try:
        import trollius as asyncio
    except ImportError:
        import asyncio  # again for better error message

import weakref

from Pyjo.Util import getenv, setenv, warn


WATCHER_DELAY = 0.01
DEBUG = getenv('PYJO_REACTOR_DEBUG', False)

loop = None

setenv('PYJO_REACTOR', getenv('PYJO_REACTOR', 'Pyjo.Reactor.Asyncio'))


class Pyjo_Reactor_Asyncio(Pyjo.Reactor.Select.object):
    """
    :mod:`Pyjo.Reactor.Asyncio` inherits all attributes and methods from
    :mod:`Pyjo.Reactor.Select` and implements the following new ones.
    """

    def __new__(cls, **kwargs):
        global loop

        # Fallback to standard reactor if another on Python 2.x
        if asyncio.__name__ != 'asyncio' and loop:
            module = importlib.import_module(Pyjo.Reactor.Base.detect(''))
            return module.new(**kwargs)
        else:
            return super(Pyjo_Reactor_Asyncio, cls).__new__(cls, **kwargs)

    def __init__(self, **kwargs):
        """

            reactor = Pyjo.Reactor.Asyncio.new()
            reactor2 = Pyjo.Reactor.Asyncio.new(loop=asyncio.get_event_loop())

        Creates new reactor based on asyncio main loop. It uses existing
        asyncio loop for first object and create new async io loop for another.
        """
        super(Pyjo_Reactor_Asyncio, self).__init__(**kwargs)

        global loop

        self.loop = None
        """::

            loop = asyncio.get_event_loop()

        asyncio main event loop.
        """

        if loop:
            self.loop = asyncio.new_event_loop()
        else:
            self.loop = asyncio.get_event_loop()
            loop = self.loop

    def again(self, tid):
        """::

            reactor.again(tid)

        Restart active timer.
        """
        timer = self._timers[tid]
        timer['handler'].cancel()
        timer['handler'] = self.loop.call_later(timer['after'], timer['cb'], self)

    @property
    def is_running(self):
        """::

            boolean = reactor.is_running

        Check if reactor is running.
        """
        return self.loop.is_running()

    def one_tick(self):
        """::

            reactor.one_tick()

        Run reactor until an event occurs. Note that this method can recurse back into
        the reactor, so you need to be careful. Meant to be overloaded in a subclass.
        """
        loop = self.loop
        if not loop.is_running():
            loop.stop()
            loop.run_forever()

    def recurring(self, cb, after):
        """::

            tid = reactor.recurring(cb, 0.25)

        Create a new recurring timer, invoking the callback repeatedly after a given
        amount of time in seconds.
        """
        return self._timer(cb, True, after)

    def remove(self, remove):
        """::

            boolean = reactor.remove(handle)
            boolean = reactor.remove(tid)

        Remove handle or timer.
        """
        if isinstance(remove, str):
            if remove in self._timers:
                if 'handler' in self._timers[remove]:
                    self._timers[remove]['handler'].cancel()
                    del self._timers[remove]['handler']

        elif remove is not None:
            fd = remove.fileno()
            if fd in self._ios:
                if 'has_reader' in self._ios[fd]:
                    self.loop.remove_reader(fd)
                    del self._ios[fd]['has_reader']
                if 'has_writer' in self._ios[fd]:
                    self.loop.remove_writer(fd)
                    del self._ios[fd]['has_writer']

        super(Pyjo_Reactor_Asyncio, self).remove(remove)

    def reset(self):
        """::

            reactor.reset()

        Remove all handles and timers.
        """
        loop = self.loop
        for fd in self._ios:
            io = self._ios[fd]
            if 'has_reader' in io:
                loop.remove_reader(fd)
                del io['has_reader']
            if 'has_writer' in io:
                loop.remove_writer(fd)
                del io['has_writer']
        for tid in self._timers:
            timer = self._timers[tid]
            if 'handler' in timer:
                timer['handler'].cancel()
        loop.stop()
        self.loop = asyncio.new_event_loop()
        super(Pyjo_Reactor_Asyncio, self).reset()

    def start(self):
        """::

            reactor.start()

        Start watching for I/O and timer events, this will block until :meth:`stop` is
        called or there is no any active I/O or timer event.
        """
        loop = self.loop

        if loop.is_running():
            return

        def watcher_cb():
            if self._ios or self._timers:
                loop.call_later(WATCHER_DELAY, watcher_cb)
            else:
                loop.stop()

        loop.call_later(WATCHER_DELAY, watcher_cb)
        loop.run_forever()

    def stop(self):
        """::

            reactor.stop()

        Stop watching for I/O and timer events.
        """
        self.loop.stop()

    def timer(self, cb, after):
        """::

            tid = reactor.timer(cb, 0.5)

        Create a new timer, invoking the callback after a given amount of time in
        seconds.
        """
        return self._timer(cb, False, after)

    def watch(self, handle, read, write):
        """::

            reactor = reactor.watch(handle, read, write)

        Change I/O events to watch handle for with true and false values. Note
        that this method requires an active I/O watcher.
        """
        fd = handle.fileno()
        self = weakref.proxy(self)

        def io_cb(self, message, is_write, fd):
            if fd in self._ios:
                io = self._ios[fd]
                self._sandbox(io['cb'], message, is_write)

        if fd not in self._ios:
            self._ios[fd] = {}
        io = self._ios[fd]

        if read:
            if 'has_reader' in io:
                self.loop.remove_reader(fd)
            else:
                io['has_reader'] = True
            self.loop.add_reader(fd, io_cb, self, "Read fd {0}".format(fd), False, fd)
        elif 'has_reader' in io:
            self.loop.remove_reader(fd)
            del io['has_reader']

        if write:
            if 'has_writer' in io:
                self.loop.remove_writer(fd)
            else:
                io['has_writer'] = True
            self.loop.add_writer(fd, io_cb, self, "Write fd {0}".format(fd), True, fd)
        elif 'has_writer' in io:
            self.loop.remove_writer(fd)
            del io['has_writer']

        return self

    def _timer(self, cb, recurring, after):
        tid = super(Pyjo_Reactor_Asyncio, self)._timer(cb, recurring, after)
        self = weakref.proxy(self)

        def timer_cb(self):
            timer = self._timers[tid]
            if DEBUG:
                warn("-- Alarm timer[{0}] = {1}".format(tid, timer))
            if recurring:
                handler = self.loop.call_later(timer['recurring'], timer_cb, self)
                timer['handler'] = handler
            else:
                self.remove(tid)
            self._sandbox(timer['cb'], 'Timer {0}'.format(tid))

        self._timers[tid]['handler'] = self.loop.call_later(after, timer_cb, self)

        return tid


new = Pyjo_Reactor_Asyncio.new
object = Pyjo_Reactor_Asyncio
