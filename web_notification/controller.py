# -*- coding: utf-8 -*-

#from openerp.addons.web_longpolling.namespace import LongPollingNameSpace
#from openerp.addons.web_socketio.session import AbstractAdapter
#
#
#class NotificationAdapter(AbstractAdapter):
#    channel = 'notification'
#
#    def get(self, messages, uid):
#        res = []
#        for m in messages:
#            if m['values']['to_id'] == uid:
#                res.append(m)
#        return res
#
#
#@LongPollingNameSpace.on(
#    'notification', adapterClass=NotificationAdapter, eventtype='connect')
#def get_notifications(session):
#    while True:
#        notifications = session.listen(session.uid)
#        session.validate(True)
#        session.emit('get notification', notifications)

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
