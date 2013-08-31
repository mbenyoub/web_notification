# -*- coding: utf-8 -*-

from openerp.osv import osv, fields


class IrNotification(osv.Model):
    _name = 'ir.notification'
    _description = 'OpenERP Notification'
    _inherit = [
        'postgres.notification',
    ]
    _postgres_channel = 'notification'

    _columns = {
        'mode': fields.selection([
            ('notify', 'Notification'), ('warn', 'Warning')], 'Mode',
            required=True),
        'subject': fields.char('Subject', size=64, required=True),
        'body': fields.html('Body', required=True),
        'user_ids': fields.many2many('res.users', 'user_notified_rel',
                                     'notify_id', 'user_id', 'Users'),
    }

    _defaults = {
        'mode': 'notify',
    }

    def create(self, cr, uid, values, context=None):
        id = super(IrNotification, self).create(
            cr, uid, values, context=context)
        self.notify(cr, uid, **values)
        return id

    def notify(self, cr, uid, user_ids, **values):
        for user in self.pool.get('res.users').read(cr, uid, user_ids,
                                                    ['notification_sticky']):
            message = values.copy()
            message.update({
                'to_id': user['id'],
                'sticky': user['notification_sticky'],
            })
            super(IrNotification, self).notify(cr, uid, **message)

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
