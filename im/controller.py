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
    cr, uid, context = request.cr, request.uid, request.context
    im_user_obj = request.pool.get('im.user')
    im_message_obj = request.pool.get('im.message')
    my_id = im_user_obj.get_by_user_id(cr, uid, uid, context=context)
    message_received = []
    now = dt.now()
    while (now - start).seconds < POLL_TIMEOUT and not message_received:
        sleep(POLL_SLEEP)
        message_received = im_message_obj.get_messages(cr, uid, context=context)
        now = dt.now()

    users_status = im_user_obj.get_users_status(cr, uid, context=context)
    im_user_obj.im_connect(cr, uid, my_id['id'], context=context)

    return {
        'user_id': my_id,
        'status': users_status,
        'messages': message_received,
    }

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
