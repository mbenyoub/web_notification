# -*- coding: utf-8 -*-

from openerp.addons.web_longpolling.longpolling import longpolling
from openerp.addons.web_longpolling.session import AbstractAdapter

#POLL_SLEEP = 0.5


class NotificationAdapteur(AbstractAdapter):
    channel = 'notification'

    def get(self, messages, uid):
        res = []
        for m in messages:
            if m['values']['to_id'] == uid:
                res.append(m)
        return res


@longpolling.route('/notification', adapter=NotificationAdapteur)
def get_notifications(session, **kwargs):
    return session.listen(session.uid)

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
