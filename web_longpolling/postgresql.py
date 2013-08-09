# -*- coding: utf-8 -*-

from contextlib import contextmanager


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

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
