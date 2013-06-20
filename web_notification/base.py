# -*- coding: utf-8 -*-

from openerp.osv import osv, fields
from openerp.addons.base.res.res_users import res_users


res_users.SELF_WRITEABLE_FIELDS.append('notification_sticky')
res_users.SELF_READABLE_FIELDS.append('notification_sticky')


class ResUsers(osv.Model):
    _inherit = 'res.users'

    _columns = {
        'notification_sticky': fields.boolean('Notification sticky'),
    }

    _defaults = {
        'notification_sticky': False,
    }

    def post_notification(self, cr, uid, to_user_id, title='', message='',
                          mode='notify', context=None):
        partner_id = self.pool.get('res.users').read(
            cr, uid, [to_user_id], ['partner_id'], context=context,
            load="_classic_write")[0]['partner_id']
        vals = {
            'subject': title,
            'body': message,
            'type': 'notification',
            'partner_ids': [(6, 0, [partner_id])],
            'notification_ids': [(0, 0, {
                'partner_id': partner_id,
                'mode': mode,
                'force_notification': True,
            })],
        }
        self.pool.get('mail.message').create(cr, uid, vals, context=context)

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
