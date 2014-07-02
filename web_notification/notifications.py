from openerp.osv import osv, fields


class IrNotification(osv.Model):
    _name = 'ir.notification'
    _description = 'OpenERP Notification'

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
        read = self.read(cr, uid, id, [], context=context)
        del read['id']
        self.notify(cr, uid, **read)
        return id

    def notify(self, cr, uid, user_ids, **values):
        bus = self.pool.get('bus.bus')
        for user in self.pool.get('res.users').read(cr, uid, user_ids,
                                                    ['notification_sticky']):
            message = values.copy()
            message['sticky'] = user['notification_sticky']
            print 'notify_res_user_%d' % user['id']
            bus.sendone(cr, uid, 'notify_res_user_%d' % user['id'], message)
