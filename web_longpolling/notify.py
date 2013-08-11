# -*- coding: utf-8 -*-

from openerp.osv import osv
from openerp.tools import config
from openerp.modules.registry import RegistryManager
from simplejson import dumps


def get_channel():
    return config.get('longpolling_channel', 'longpolling_channel')


class LongPollingNotification(osv.AbstractModel):
    _name = 'longpolling.notification'
    _description = 'AbstractClass to notify'
    _longpolling_channel = None

    def notify(self, cr, uid, **kwargs):
        assert self._longpolling_channel
        cursor = RegistryManager.get(cr.dbname).db.cursor()
        message = dumps({
            'channel': self._longpolling_channel,
            'uid': uid,
            'values': kwargs,
        })
        cursor.execute('NOTIFY ' + get_channel() + ', %s;', message)
        cursor.commit()
        cursor.close()

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
