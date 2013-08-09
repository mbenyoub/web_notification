# -*- coding: utf-8 -*-

from .postgresql import rollback_and_close
from gevent import sleep


CURSORLIMIT = {}


class OpenERPObject(object):

    def __init__(self, registry, uid, model):
        self.registry = registry
        self.uid = uid
        self.obj = registry.get(model)
        # serialized = False => put the the isolation level
        # READ_COMMITED, without it option, the other commit can not be
        # used and we have always got the same result for each read

    def __getattr__(self, fname):
        def wrappers(*args, **kwargs):
            while CURSORLIMIT[self.registry.db_name] <= 0:
                sleep(0.1)
            CURSORLIMIT[self.registry.db_name] -= 1
            cursor = self.registry.db.cursor
            with rollback_and_close(cursor(serialized=False)) as cr:
                res = getattr(self.obj, fname)(cr, self.uid, *args, **kwargs)
            CURSORLIMIT[self.registry.db_name] += 1
            return res
        return wrappers


class OpenERPRegistry(object):

    registries = {}  # {db: cls}

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
