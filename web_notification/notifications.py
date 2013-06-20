# -*- coding: utf-8 -*-

from openerp.osv import osv, fields


class MailNotification(osv.Model):
    _inherit = 'mail.notification'
    _description = ''

    _columns = {
        'mode': fields.selection(
            [('notify', 'Notification'), ('warn', 'Warning'),
             ('delivery', 'Delivery')], 'Mode'),
        'force_notification': fields.boolean('Force notification'),
    }

    _defaults = {
        'mode': 'notify',
        'force_notification': False,
    }

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
