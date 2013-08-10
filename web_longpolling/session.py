# -*- coding: utf-8 -*-

from openerp.modules.registry import RegistryManager
from .postgresql import rollback_and_close


class OpenERPObject(object):

    def __init__(self, registry, uid, model):
        self.registry = registry
        self.uid = uid
        self.obj = registry.registry.get(model)
        # serialized = False => put the the isolation level
        # READ_COMMITED, without it option, the other commit can not be
        # used and we have always got the same result for each read

    def __getattr__(self, fname):
        def wrappers(*args, **kwargs):
            with rollback_and_close(self.registry) as cr:
                return getattr(self.obj, fname)(cr, self.uid, *args, **kwargs)
        return wrappers


class OpenERPRegistry(object):

    registries = {}  # {db: cls}

    def __init__(self, database, maxcursor):
        self.registry = RegistryManager.get(database)
        self.maxcursor = maxcursor

    @classmethod
    def add(cls, database, maxcursor):
        r = cls(database, maxcursor)
        cls.registries[database] = r
        return r

    @classmethod
    def get(cls, database):
        return cls.registries[database]

    def get_openerpobject(self, uid, model):
        return OpenERPObject(self, uid, model)


# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
