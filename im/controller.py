# -*- coding: utf-8 -*-

from openerp.addons.web_longpolling.longpolling import longpolling, get_timeout
from datetime import datetime as dt

POLL_SLEEP = 0.25
POLL_TIMEOUT = get_timeout() - 5
assert POLL_TIMEOUT > 0


@longpolling.route('/im')
def receive(request, **kwargs):
    from gevent import sleep
    start = dt.now()
    context = request.context
    im_user_obj = request.model('im.user')
    im_message_obj = request.model('im.message')
    message_received = []
    now = dt.now()
    while True:
        message_received = im_message_obj.get_messages(context=context)
        now = dt.now()
        if (now - start).seconds > POLL_TIMEOUT or message_received:
            break
        sleep(POLL_SLEEP)

    users_status = im_user_obj.get_users_status(context=context)
    my_id = im_user_obj.get_by_user_id(request.uid, context=context)
    return {
        'user_id': my_id,
        'status': users_status,
        'messages': message_received,
    }

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
