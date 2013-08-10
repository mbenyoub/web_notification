# -*- coding: utf-8 -*-

from openerp.modules.registry import RegistryManager
from openerp.addons.web_longpolling.notify import get_channel
from .postgresql import rollback_and_close, get_conn_and_cr
from .postgresql import gevent_wait_callback
from gevent import spawn, sleep
from simplejson import loads


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
        self.received_message = {}

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

    def listen(self):
        self.maxcursor -= 1
        conn, cr = get_conn_and_cr(self.registry.db_name)
        cr.execute('Listen ' + get_channel() + ';')

        def get_listen():
            while True:
                gevent_wait_callback(cr.connection)
                while conn.notifies:
                    notify = conn.notifies.pop()
                    payload = loads(notify.payload)
                    channel = payload['channel']
                    del payload['channel']
                    if self.received_message.get(channel) is None:
                        self.received_message[channel] = []
                    self.received_message[channel] += [payload]

                sleep(0.1)

        spawn(get_listen)

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
