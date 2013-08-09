# -*- coding: utf-8 -*-

from contextlib import contextmanager
import gevent_psycopg2
from gevent.socket import wait_read, wait_write
from psycopg2 import extensions, OperationalError


@contextmanager
def rollback_and_close(registry, CURSORLIMIT):
    from gevent import sleep
    try:
        while CURSORLIMIT[registry.db_name] <= 0:
            sleep(0.1)
        CURSORLIMIT[registry.db_name] -= 1
        cursor = registry.db.cursor(serialized=False)
        yield cursor
    finally:
        cursor.rollback()
        cursor.close()
        CURSORLIMIT[registry.db_name] += 1


def gevent_wait_callback(conn, timeout=None):
    """A wait callback useful to allow gevent to work with Psycopg."""
    while 1:
        state = conn.poll()
        if state == extensions.POLL_OK:
            break
        elif state == extensions.POLL_READ:
            wait_read(conn.fileno(), timeout=timeout)
        elif state == extensions.POLL_WRITE:
            wait_write(conn.fileno(), timeout=timeout)
        else:
            raise OperationalError("Bad result from poll: %r" % state)


def patch():
    gevent_psycopg2.monkey_patch()
    extensions.set_wait_callback(gevent_wait_callback)

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
