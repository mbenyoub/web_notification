# -*- coding: utf-8 -*-

from openerp.tools import config
from multiprocessing import Process
from simplejson import dumps


LONGPOOLTIMEOUT = 5


class Json(object):

    def __call__(self, function):
        def wrap(*args, **kwargs):
            result = function(*args, **kwargs)
            print result
            return dumps(result)
        return wrap


@Json()
def application(request, start_response):
    from gevent import sleep
    status = '200 OK'
    headers = [
        ('Content-Type', 'application/json'),
    ]
    start_response(status, headers)
    r = 'titi'
    sleep(5)
    return r


def process_longpolling(host, port):
    from gevent import pywsgi
    server = pywsgi.WSGIServer((host, port), application)
    server.serve_forever()


def start_server():
    if config.get('longpolling_server', True):
        host = config.get('longpolling_server_host', '127.0.0.1')
        if host.lower() != 'none':
            port = int(config.get('longpolling_server_port', '8068'))
            p = Process(target=process_longpolling, args=(host, port))
            p.deamon = True
            p.start()


# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
