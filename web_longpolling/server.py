# -*- coding: utf-8 -*-

from gevent import pywsgi, monkey
monkey.patch_all()
import gevent_psycopg2
gevent_psycopg2.monkey_patch()
from openerp.netsvc import init_logger
from openerp.addons.web_longpolling.longpolling import longpolling
from openerp.modules.registry import RegistryManager
from openerp.tools import config
from argparse import ArgumentParser
from logging import getLogger


logger = getLogger("Gevent WSGI server")


def start_longpolling_server(host, port, dbnames):
    longpolling.serve()
    for db in dbnames:
        RegistryManager.get(db)
    server = pywsgi.WSGIServer((host, port), longpolling.application)
    logger.info("Start long polling server %r:%s", host, port)
    server.serve_forever()

if __name__ == '__main__':
    parser = ArgumentParser(description='Gevent WSGI server')
    parser.add_argument('-d', dest='db', default='',
                        help="'list of db names, separated by ','")
    parser.add_argument('-i', dest='interface', default='127.0.0.1',
                        help="Define the interface to listen")
    parser.add_argument('-p', dest='port', default=8068,
                        help="Define the port to listen")

    args = parser.parse_args()
    init_logger()
    dbs = args.db.split(',')
    if not dbs:
        dbs = [config.get('db_name')]
    start_longpolling_server(args.interface, int(args.port), dbs)

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
