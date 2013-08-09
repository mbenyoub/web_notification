# -*- coding: utf-8 -*-

from openerp.tools import config


def get_channel():
    return config.get('longpolling_channel', 'longpolling_channel')

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
