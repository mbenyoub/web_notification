# -*- coding: utf-8 -*-

from openerp.osv import osv, fields


class MailNotification(osv.Model):
    _name = 'mail.notification'
    _inherit = [
        'mail.notification',
        'longpolling.notification',
    ]
    _longpolling_channel = 'notification'

    _columns = {
        'mode': fields.selection(
            [('notify', 'Notification'), ('warn', 'Warning')], 'Mode'),
        'force_notification': fields.boolean('Force notification'),
    }

    _defaults = {
        'mode': 'notify',
        'force_notification': False,
    }

    def create(self, cr, uid, values, context=None):
        id = super(MailNotification, self).create(
            cr, uid, values, context=context)
        message = {
            'to_id': uid,
            'title': 'Un titre',
            'msg': 'Un message',
            'sticky': False,
        }
        self.notify(cr, uid, **message)
        return id

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
