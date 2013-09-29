# -*- coding: utf-8 -*-

from openerp.osv import osv, fields


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
    }

    _defaults = {
        'mode': 'notify',
    }

    def button_check_notification(self, cr, uid, ids, context=None):
        r = self.read(cr, uid, ids[0], ['title', 'message', 'mode'],
                      context=context)
        del r['id']
        self.pool.get('res.users').post_notification(
            cr, uid, [uid], context=context, **r)
        return True

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
