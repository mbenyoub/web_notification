# -*- coding: utf-8 -*-

from openerp.addons.web_longpolling.namespace import LongPollingNameSpace
from openerp.addons.web_socketio.session import AbstractAdapter


class NotificationAdapter(AbstractAdapter):
    channel = 'notification'

    def get(self, message, uid):
        if message['values']['to_id'] == uid:
            return True
        return False


@LongPollingNameSpace.on(
    'notification', adapterClass=NotificationAdapter, eventtype='connect')
def get_notifications(session):
    while True:
        notification = session.listen(session.uid)
        session.validate(True)
        session.emit('get notification', notification)

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
