# -*- coding: utf-8 -*-

from openerp.tools import config
from multiprocessing import Process
from simplejson import dumps, loads
from werkzeug.wrappers import Request, Response
from werkzeug.routing import Map, Rule
from werkzeug.exceptions import HTTPException


LONGPOOLTIMEOUT = 5


class LongPolling(object):

    path_map = Map()
    view_function = {}

    def route(self, path='/', mode='json', mustbeauthenticate=True):
        assert path not in (False, None), "Bad route path: " + str(path)
        assert isinstance(path, str), "Path must be a string: " + str(path)
        assert mode in ('json', 'http'), "Mode must be json or http: " + str(path)
        assert isinstance(mustbeauthenticate, bool)

        #TODO make authenticate
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
            values.update(loads(request.args.get('data')))
            request.db = request.args.get('db')
            request.uid = request.args.get('uid')
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

longpolling = LongPolling()


def process_longpolling(host, port):
    from gevent import pywsgi
    server = pywsgi.WSGIServer((host, port), longpolling.application)
    server.serve_forever()


def start_server():
    if config.get('longpolling_server', True):
        host = config.get('longpolling_server_host', '127.0.0.1')
        if host.lower() != 'none':
            port = int(config.get('longpolling_server_port', '8068'))
            p = Process(target=process_longpolling, args=(host, port))
            p.deamon = True
            p.start()


@longpolling.route('/<int>')
def foo(request, **kwargs):
    print kwargs
    r = 'titi'
    from gevent import sleep
    sleep(5)
    return r

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
