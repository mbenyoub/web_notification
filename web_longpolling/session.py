# -*- coding: utf-8 -*-

from openerp.modules.registry import RegistryManager
from openerp.addons.web_longpolling.notify import get_channel
from openerp.addons.web.session import AuthenticationError
from .postgresql import openerpCursor, get_conn_and_cr
from .postgresql import gevent_wait_callback
from gevent import spawn, sleep
from simplejson import loads, dumps


class AbstractAdapter(object):

    channel = None

    def __init__(self, registry):
        self.registry = registry
        assert self.channel

    def get(self, messages, *args, **kwargs):
        """ Return the messageto get """
        res = []
        for m in messages:
            res.append(m)
        return res

    def format(self, message, *args, **kwargs):
        return message['values']

    def listen(self, *args, **kwargs):
        while True:
            sleep(0)  # switch to other coroutine
            received_messages = self.registry.received_message.get(self.channel, [])
            if not received_messages:
                continue
            messages = self.get(received_messages, *args, **kwargs)
            if not messages:
                continue
            result = []
            for message in messages:
                self.registry.received_message[self.channel].remove(message)
                result.append(self.format(message, *args, **kwargs))

            return result


class OpenERPObject(object):

    def __init__(self, registry, uid, model, autocommit):
        self.registry = registry
        self.uid = uid
        self.obj = registry.registry.get(model)
        self.autocommit = autocommit

    def __getattr__(self, fname):
        def wrappers(*args, **kwargs):
            with openerpCursor(self.registry, self.autocommit) as cr:
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

    def get_openerpobject(self, uid, model, autocommit=False):
        return OpenERPObject(self, uid, model, autocommit)

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

                sleep(0)  # switch yo other coroutine

        spawn(get_listen)

    def cursor(self):
        return self.registry.db.cursor(serialized=False)

    def notify(self, channel, uid, **kwargs):
        with openerpCursor(self, True) as cr:
            message = dumps({
                'channel': channel,
                'uid': uid,
                'values': kwargs,
            })
            cr.execute('NOTIFY ' + get_channel() + ', %s;', (message,))
        return True

    def renotify(self):
        model_obj = self.get_openerpobject(1, 'ir.model')
        m_ids = model_obj.search([])
        for m in model_obj.read(m_ids, ['model']):
            obj = self.get_openerpobject(1, m['model'], autocommit=True)
            if hasattr(obj.obj, 'renotify'):
                obj.renotify()


class OpenERPSession(object):

    def __init__(self, request, session_store, mustbeauthenticated, adapter):
        self.adapter = adapter
        sid = request.cookies.get('sid')
        session = None
        if sid:
            session = session_store.get(sid)
        session_id = request.args.get('session_id')
        if session and session_id:
            session = session.get(session_id)
        else:
            session = None

        self.authenticate = False
        if session:
            try:
                session.assert_valid()
                self.authenticate = True
            except AuthenticationError:
                if mustbeauthenticated:
                    raise

            self.context = session.context
            self.uid = session._uid
            self.registry = OpenERPRegistry.get(session._db)
        elif mustbeauthenticated:
            raise AuthenticationError('No session found')
        else:
            self.context = {}
            self.uid = None
            self.registry = None

    def model(self, openerpmodel):
        if not self.authenticate:
            raise AuthenticationError('Controler must be authenticate')
        return self.registry.get_openerpobject(self.uid, openerpmodel)

    def listen(self, *args, **kwargs):
        if not self.adapter:
            raise Exception("No Adapter defined for this listen action")
        if not self.authenticate:
            raise AuthenticationError('Controler must be authenticate')
        return self.adapter(self.registry).listen(*args, **kwargs)

    def notify(self, channel, **kwargs):
        if not self.authenticate:
            raise AuthenticationError('Controler must be authenticate')
        return self.registry.notify(channel, self.uid, **kwargs)


class OpenERPService(object):

    def __init__(self, registry, adapter):
        self.registry = registry
        self.adapter = adapter

    def model(self, openerpmodel):
        return self.registry.get_openerpobject(self.uid, openerpmodel,
                                               autocommit=True)

    def listen(self, *args, **kwargs):
        if not self.adapter:
            raise Exception("No Adapter defined for this listen action")
        return self.adapter(self.registry).listen(*args, **kwargs)

    def notify(self, channel, uid, **kwargs):
        return self.registry.notify(channel, uid, **kwargs)

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
