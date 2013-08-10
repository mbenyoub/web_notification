# -*- coding: utf-8 -*-

from openerp.netsvc import init_logger
from openerp.addons.web_longpolling.longpolling import longpolling
from openerp.tools import config
from argparse import ArgumentParser


if __name__ == '__main__':
    parser = ArgumentParser(description='Gevent WSGI server')
    parser.add_argument('-d', dest='db', default='',
                        help="'list of db names, separated by ','")
    parser.add_argument('-i', dest='interface', default='127.0.0.1',
                        help="Define the interface to listen")
    parser.add_argument('-p', dest='port', default=8068,
                        help="Define the port to listen")
    parser.add_argument('--max-cursor', dest='maxcursor', default=2,
                        help="Max declaration of cursor by data base")

    args = parser.parse_args()
    init_logger()
    dbs = args.db.split(',')
    if not dbs:
        dbs = [config.get('db_name')]
    longpolling.patch_all()
    longpolling.load_databases(dbs, int(args.maxcursor))
    longpolling.serve_forever(args.interface, int(args.port))

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
