# -*- coding: utf-8 -*-

from openerp.osv import osv, fields
import thread
from openerp.modules.registry import RegistryManager
from time import sleep
from openerp import SUPERUSER_ID


class Setting(osv.TransientModel):
    _name = 'web.notification.setting'
    _description = 'Setting for Notification'
    _inherit = 'res.config.settings'

    _columns = {
        'title': fields.char('Title', size=64),
        'message': fields.text('Message'),
        'mode': fields.selection(
            [('notify', "Notification"), ('warn', 'Warning')], 'Mode',
            required=True),
        'makecheck': fields.selection(
            [('none', "None"), ('simple', "Only a simple notification"),
             ('withdelay', "Notification after a delay in second"),
             ('cron', "Notification by cron")], "Make a ckeck", required=True),
        'delay': fields.integer('Delay'),
        'dt': fields.datetime('Date time'),
    }

    _defaults = {
        'mode': 'notify',
        'makecheck': 'none',
        'delay': 0,
    }

    def button_check_notification(self, cr, uid, ids, context=None):
        r = self.read(cr, uid, ids[0], ['title', 'message', 'mode'],
                      context=context)
        del r['id']
        self.pool.get('res.users').post_notification(
            cr, uid, [uid], context=context, **r)
        return True

    def button_check_notification_delay(self, cr, uid, ids, context=None):
        r = self.read(cr, uid, ids[0], ['title', 'message', 'mode', 'delay'],
                      context=context)
        del r['id']
        delay = r['delay']
        del r['delay']

        def thread_method(dbname, delay, kwargs):
            sleep(delay)
            registry = RegistryManager.get(dbname)
            cursor = registry._db.cursor()
            registry.get('res.users').post_notification(
                cursor, uid, [uid], **kwargs)
            cursor.commit()
            cursor.close()
            return True

        thread.start_new_thread(thread_method, (cr.dbname, delay, r))
        return True

    def button_check_notification_cron(self, cr, uid, ids, context=None):
        r = self.read(cr, uid, ids[0], ['title', 'message', 'mode', 'dt'],
                      context=context)
        vals = {
            'name': "Check notification",
            'user_id': uid,
            'priority': 100,
            'numbercall': 1,
            'doall': True,
            'model': 'res.users',
            'function': 'post_notification',
            'args': str(([uid], r['title'], r['message'], r['mode'], context)),
        }
        if r['dt']:
            vals.update({
                'nextcall': r['dt'],
            })

        self.pool.get('ir.cron').create(cr, SUPERUSER_ID, vals, context=context)

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
