# -*- coding: utf-8 -*-

from gevent import pywsgi, monkey
monkey.patch_all()
import gevent_psycopg2
gevent_psycopg2.monkey_patch()
from openerp.tools import config
from openerp.netsvc import init_logger
from openerp.addons.web_longpolling.longpolling import longpolling
from openerp.modules.registry import RegistryManager
from logging import getLogger
from argparse import ArgumentParser


logger = getLogger("Gevent WSGI server")


def start_longpolling_server(host, port, dbnames):
    for db in dbnames:
        RegistryManager.get(db)
    server = pywsgi.WSGIServer((host, port), longpolling.application)
    logger.info("Start long polling server %r:%s", host, port)
    server.serve_forever()

if __name__ == '__main__':
    parser = ArgumentParser(description='Gevent WSGI server')
    parser.add_argument('-d', dest='db', default='',
                        help="'list of db names, separated by ','")

    args = parser.parse_args()
    #TODO enleve la config par openerp, on l'ajoute dans argparse
    #TODO si bas de dbname alors on prend celuid du config
    if config.get('longpolling_server', True):
        host = config.get('longpolling_server_host', '127.0.0.1')
        if host.lower() != 'none':
            port = int(config.get('longpolling_server_port', '8068'))
            init_logger()
            dbs = args.db.split(',')
            start_longpolling_server(host, port, dbs)

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
