# -*- coding: utf-8 -*-

from openerp.tools import config
from multiprocessing import Process


LONGPOOLTIMEOUT = 5


#def getMessage(response, path_info):
    #from gevent import sleep
    #while True:
        #current = datetime.datetime.now()
        #response.put('%s\n' % current.strftime("%Y-%m-%d %I:%M:%S"))
        #sleep(2)
    #response.put(StopIteration)


def application(request, start_response):
    import simplejson
    from gevent import sleep
    status = '200 OK'
    headers = [
        ('Content-Type', 'application/json'),
    ]
    start_response(status, headers)
    r = 'titi'
    #simplejson.encoder(r)
    print r
    return r
    #yield simplejson.dumps(['titi'])
    #while True:
        #print "*" * 80
        #yield simplejson.dumps('titi')
        #sleep(5)

    #from gevent import spawn, queue
    #import simplejson
    #response = queue.Queue()
    #response.put(' ' * 998)
    #response.put("Current Time:\n\n")
    #spawn(getMessage, response, request.get('PATH_INFO', '/')[1:])
    #body = simplejson.dumps(response)
    #start_response('200 OK', [
        #('Content-Type', 'application/json'),
        #('Content-Length', str(len(body))),
    #])
    #return body


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
