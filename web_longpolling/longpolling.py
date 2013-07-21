# -*- coding: utf-8 -*-

from openerp.tools import config
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
        path = session_path()
        self.session_store = FilesystemSessionStore(path)

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

    def dispatch_request(self, request):
        adapter = self.path_map.bind_to_environ(request.environ)
        try:
            endpoint, values = adapter.match()
            sid = request.cookies.get('sid')
            session = None
            if sid:
                session = self.session_store.get(sid)
            session_id = request.args.get('session_id')
            self.session = None
            if session and session_id:
                self.session = session.get(session_id)

            if self.view_function[endpoint]['mustbeauthenticate']:
                if not self.session:
                    raise AuthenticationError('No session found')
                self.session.assert_valid()
            values.update(loads(request.args.get('data')))
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


def process_longpolling(host, port):
    from gevent import pywsgi
    server = pywsgi.WSGIServer((host, port), longpolling.application)
    print "Start long polling server %r:%r" % (host, port)
    server.serve_forever()


def start_server():
    if config.get('longpolling_server', True):
        host = config.get('longpolling_server_host', '127.0.0.1')
        if host.lower() != 'none':
            port = int(config.get('longpolling_server_port', '8068'))
            p = Process(target=process_longpolling, args=(host, port))
            p.deamon = True
            p.start()


@longpolling.route('/notification/')
def foo(request, **kwargs):
    r = {
        'title': 'toto',
        'msg': 'toto',
        'sticky': True,
        'type': 'notify',
    }
    from gevent import sleep
    sleep(5)
    return [r]

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
