# -*- coding: utf-8 -*-

from openerp.addons.web_longpolling.longpolling import longpolling


@longpolling.service('im')
def check_connection(registry):
    pass

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
