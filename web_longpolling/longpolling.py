# -*- coding: utf-8 -*-

from simplejson import dumps, loads
from werkzeug.wrappers import Request, Response
from werkzeug.routing import Map, Rule
from werkzeug.exceptions import HTTPException, Unauthorized, RequestTimeout
from werkzeug.exceptions import InternalServerError
from werkzeug.contrib.sessions import FilesystemSessionStore
from openerp.addons.web.http import session_path
from openerp.addons.web.session import AuthenticationError
from openerp.modules.registry import RegistryManager
from openerp.tools import config
from psycopg2 import extensions, OperationalError
from logging import getLogger
from .postgresql import rollback_and_close


logger = getLogger(__name__)


CURSORLIMIT = {}


def get_path():
    path = config.get('longpolling_path', '/openerplongpolling')
    assert path[0] == '/'
    return path


def get_timeout():
    return int(config.get('longpolling_timeout', '60'))


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
            with rollback_and_close(self.registry, CURSORLIMIT) as cr:
                return getattr(self.obj, fname)(cr, self.uid, *args, **kwargs)
        return wrappers


class LongPolling(object):

    def __init__(self):
        self.path_map = Map()
        self.view_function = {}
        path = session_path()
        self.session_store = FilesystemSessionStore(path)
        self.longpolling_timeout = get_timeout()
        self._longpolling_serve = False
        self.longpolling_path = get_path()
        self.uid = None
        self.registry = None
        self.registries = {}

    def get_openerp_object(self, model):
        return OpenERPObject(self.registry, self.uid, model)

    def serve_forever(self, host, port, dbnames, maxcursor=2):
        """Load dbs and run gevent wsgi server"""
        from gevent import monkey
        monkey.patch_all()
        import gevent_psycopg2
        gevent_psycopg2.monkey_patch()
        from gevent.pywsgi import WSGIServer
        from gevent.socket import wait_read, wait_write

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

        extensions.set_wait_callback(gevent_wait_callback)
        self._longpolling_serve = True
        for db in dbnames:
            self.registries[db] = RegistryManager.get(db)
            CURSORLIMIT[db] = maxcursor

        server = WSGIServer((host, port), self.application)
        logger.info("Start long polling server %r:%s", host, port)
        server.serve_forever()

    def route(self, path='/', mode='json', mustbeauthenticated=True):
        assert path not in (False, None), "Bad route path: " + str(path)
        assert isinstance(path, str), "Path must be a string: " + str(path)
        assert path[0] == '/', "Path must begin by '/'"
        assert mode in ('json', 'http'), "Mode must be json or http: " + str(path)
        assert isinstance(mustbeauthenticated, bool)

        def wrapper(function):
            if self._longpolling_serve:
                realpath = self.longpolling_path + path
                endpoint = '%s:%s' % (function.__name__, realpath)
                rule = Rule(realpath, endpoint=endpoint)
                self.path_map.add(rule)
                old_func = self.view_function.get(endpoint)
                if old_func is not None and old_func != function:
                    raise AssertionError('View function mapping is overwriting an '
                                         'existing endpoint function: %s' % endpoint)
                self.view_function[endpoint] = {
                    'function': function,
                    'mode': mode,
                    'mustbeauthenticated': mustbeauthenticated,
                }
                logger.info('Add the rule: %r' % endpoint)
            return function
        return wrapper

    def application(self, environ, start_response):
        request = Request(environ)
        response = self.dispatch_request(request)
        return response(environ, start_response)

    def dispatch_request(self, request):
        from gevent import Timeout
        timeout = Timeout(self.longpolling_timeout)
        timeout.start()
        adapter = self.path_map.bind_to_environ(request.environ)
        try:
            endpoint, values = adapter.match()
            sid = request.cookies.get('sid')
            session = None
            if sid:
                session = self.session_store.get(sid)
            session_id = request.args.get('session_id')
            if session and session_id:
                session = session.get(session_id)

            if session:
                if self.view_function[endpoint]['mustbeauthenticated']:
                    session.assert_valid()

                request.authenticate = True
                request.context = session.context
                request.uid = self.uid = session._uid
                self.registry = self.registries.get(session._db)
            elif self.view_function[endpoint]['mustbeauthenticated']:
                raise AuthenticationError('No session found')
            else:
                request.authenticate = False
                request.context = {}

            def model(m):
                return self.get_openerp_object(m)
            request.model = model

            values.update(loads(request.args.get('data')))
            result = self.view_function[endpoint]['function'](
                request, **values)

            if self.view_function[endpoint]['mode'] == 'json':
                result = dumps(result)
                mimetype = 'application/json'
            else:
                mimetype = 'text/html'

            return Response(result, mimetype=mimetype)
        except HTTPException, e:
            return e
        except AuthenticationError, e:
            return Unauthorized()
        except Timeout, e:
            return RequestTimeout()
        except Exception, e:
            return InternalServerError(str(e))

longpolling = LongPolling()

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
