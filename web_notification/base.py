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

    def post_notification(self, cr, uid, to_user_ids, title='', message='',
                          mode='notify', context=None):
        if not isinstance(to_user_ids, (list, tuple)):
            to_user_ids = [to_user_ids]
        vals = {
            'subject': title,
            'body': message,
            'user_ids': [(4, x) for x in to_user_ids],
            'mode': mode,
        }
        return self.pool.get('ir.notification').create(cr, uid, vals)

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
