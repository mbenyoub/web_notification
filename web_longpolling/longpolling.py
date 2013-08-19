# -*- coding: utf-8 -*-

from simplejson import dumps, loads
from werkzeug.wrappers import Request, Response
from werkzeug.routing import Map, Rule
from werkzeug.exceptions import HTTPException, Unauthorized, RequestTimeout
from werkzeug.exceptions import InternalServerError
from werkzeug.contrib.sessions import FilesystemSessionStore
from openerp.addons.web.http import session_path
from openerp.addons.web.session import AuthenticationError
from openerp.tools import config
from logging import getLogger
from .session import OpenERPRegistry, OpenERPSession, OpenERPService


logger = getLogger(__name__)


def get_path():
    path = config.get('longpolling_path', '/openerplongpolling')
    assert path[0] == '/'
    return path


def get_timeout():
    return int(config.get('longpolling_timeout', '60'))


class LongPolling(object):

    def __init__(self):
        self.path_map = Map()
        self.view_function = {}
        path = session_path()
        self.session_store = FilesystemSessionStore(path)
        self.current_database = False
        self.services = {}

    def patch_all(self):
        from gevent import monkey
        monkey.patch_all()
        from .postgresql import patch
        patch()

    def load_database(self, database, maxcursor=2):
        self.current_database = database
        r = OpenERPRegistry.add(database, maxcursor)
        r.listen()
        r.renotify()
        self.current_database = None

    def load_databases(self, databases, maxcursor=2):
        for db in databases:
            self.load_database(db, maxcursor=maxcursor)

    def serve_forever(self, host, port):
        """Load dbs and run gevent wsgi server"""
        from gevent.pywsgi import WSGIServer
        server = WSGIServer((host, port), self.application)
        logger.info("Start long polling server %r:%s", host, port)
        server.serve_forever()

    def route(self, path='/', mode='json', mustbeauthenticated=True,
              adapter=None):
        assert path not in (False, None), "Bad route path: " + str(path)
        assert isinstance(path, str), "Path must be a string: " + str(path)
        assert path[0] == '/', "Path must begin by '/'"
        assert mode in ('json', 'http'), "Mode must be json or http: " + str(path)
        assert isinstance(mustbeauthenticated, bool)
        if adapter:
            assert adapter.format
            assert adapter.get

        def wrapper(function):
            if self.current_database:
                realpath = get_path() + path
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
                    'adapter': adapter,
                }
                logger.info('Add the rule: %r' % endpoint)
            return function
        return wrapper

    def service(self, module, adapter=None):
        assert isinstance(module, str)
        assert module
        if adapter:
            assert adapter.format
            assert adapter.get

        def wrapper(function):
            if self.current_database:
                if not self.services.get(self.current_database):
                    self.services[self.current_database] = {
                        module: [(function, adapter)]}
                elif not self.services[self.current_database].get(module):
                    self.services[self.current_database][module] = [
                        (function, adapter)]
                else:
                    self.services[self.current_database][module].append(
                        (function, adapter))
            return function
        return wrapper

    def run_services(self):
        from gevent import spawn, sleep

        def run(service, function):
            while 1:
                function(service)
                sleep(0)

        for dbname, modules in self.services.items():
            db = OpenERPRegistry.get(dbname)
            module_obj = db.get_openerpobject(1, 'ir.module.module')
            for module, functions in modules.items():
                domain = [
                    ('name', '=', module),
                    ('state', '=', 'installed'),
                ]
                if module_obj.search(domain):
                    for function, adapter in functions:
                        service = OpenERPService(db, adapter)
                        spawn(run, service, function)
                        logger.info('Add the service %r:%r' % (
                            module, function.__name__))

    def application(self, environ, start_response):
        request = Request(environ)
        response = self.dispatch_request(request)
        return response(environ, start_response)

    def dispatch_request(self, request):
        #FIXME Timeout traceback
        from gevent import Timeout
        Timeout(get_timeout()).start()
        adapter = self.path_map.bind_to_environ(request.environ)
        try:
            endpoint, values = adapter.match()
            route = self.view_function[endpoint]
            session = OpenERPSession(
                request, self.session_store, route['mustbeauthenticated'],
                route['adapter'])

            values.update(loads(request.args.get('data')))
            result = route['function'](session, **values)

            if route['mode'] == 'json':
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
