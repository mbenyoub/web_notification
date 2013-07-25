# -*- coding: utf-8 -*-

from openerp.tools import config
from openerp.modules.registry import RegistryManager
from multiprocessing import Process
from simplejson import dumps, loads
from werkzeug.wrappers import Request, Response
from werkzeug.routing import Map, Rule
from werkzeug.exceptions import HTTPException
from werkzeug.contrib.sessions import FilesystemSessionStore
from openerp.addons.web.http import session_path
from openerp.addons.web.session import AuthenticationError


LONGPOOLTIMEOUT = 5


class LongPolling(object):

    def __init__(self):
        self.path_map = Map()
        self.view_function = {}
        self.loaded_bases = []
        path = session_path()
        self.session_store = FilesystemSessionStore(path)
        self.registry = None

    def route(self, path='/', mode='json', mustbeauthenticate=True):
        assert path not in (False, None), "Bad route path: " + str(path)
        assert isinstance(path, str), "Path must be a string: " + str(path)
        assert mode in ('json', 'http'), "Mode must be json or http: " + str(path)
        assert isinstance(mustbeauthenticate, bool)

        def wrapper(function):
            if path[0] == '/':
                realpath = '/openerplongpolling' + path
            else:
                realpath = '/openerplongpolling' + '/' + path
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
                'mustbeauthenticate': mustbeauthenticate,
            }
            return function
        return wrapper

    def application(self, environ, start_response):
        request = Request(environ)
        response = self.dispatch_request(request)
        return response(environ, start_response)

    def load_db(self, db):
        #reload the Registry because it was not finish before multiprocess call
        #FIXME, no restart postload
        RegistryManager.new(db, update_module=False)
        self.loaded_bases.append(db)

    def dispatch_request(self, request):
        adapter = self.path_map.bind_to_environ(request.environ)
        try:
            endpoint, values = adapter.match()
            sid = request.cookies.get('sid')
            session = None
            if sid:
                session = self.session_store.get(sid)
            session_id = request.args.get('session_id')
            request.session = None
            if session and session_id:
                request.session = session.get(session_id)

            if self.view_function[endpoint]['mustbeauthenticate']:
                if not request.session:
                    raise AuthenticationError('No session found')
                request.session.assert_valid()
                db = request.session._db
                if db not in self.loaded_bases:
                    self.load_db(db)
            values.update(loads(request.args.get('data')))
            values = {}
            result = self.view_function[endpoint]['function'](
                request, **values)
            if self.view_function[endpoint]['mode'] == 'json':
                result = dumps(result)
                mimetype = 'application/json'
            else:
                mimetype = 'text/html'

            return Response(result, mimetype=mimetype)
        except (HTTPException, AuthenticationError), e:
            return e

longpolling = LongPolling()


def process_longpolling(host, port, longpolling):
    from gevent import pywsgi
    server = pywsgi.WSGIServer((host, port), longpolling.application)
    print "Start long polling server %r:%r" % (host, port)
    server.serve_forever()


def start_server():
    if config.get('longpolling_server', True):
        host = config.get('longpolling_server_host', '127.0.0.1')
        if host.lower() != 'none':
            port = int(config.get('longpolling_server_port', '8068'))
            p = Process(target=process_longpolling, args=(host, port,
                                                          longpolling))
            p.deamon = True
            p.start()

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
