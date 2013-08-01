# -*- coding: utf-8 -*-

from openerp.addons.web_longpolling.longpolling import longpolling

POLL_SLEEP = 0.5


@longpolling.route('/notification')
def get_notifications(request, **kwargs):
    from gevent import sleep
    cr, uid = request.cr, request.uid
    model = request.pool.get('mail.notification')
    mail = request.pool.get('mail.message')
    context = request.context
    user = request.pool.get('res.users').read(
        cr, uid, [uid], ['partner_id', 'notification_sticky'],
        context=context, load="_classic_write")[0]
    domain = [
        ('partner_id', '=', user['partner_id']),
        ('mode', 'in', ('notify', 'warn', False, '')),
    ]
    ids = []
    while not ids:
        sleep(POLL_SLEEP)
        ids = model.search(cr, uid, domain, context=context)
        # we are on longpolling if they are no response then the time out cut
        # the connection and restart it

    res = []
    for this in model.read(cr, uid, ids,
                           ['message_id', 'mode', 'force_notification'],
                           context=context,
                           load="_classic_write"):
        message = mail.read(cr, uid, [this['message_id']],
                            ['subject', 'body', 'author_id'],
                            load="_classic_write",
                            context=context)[0]
        condition = message['author_id'] != user['partner_id']
        condition = condition or this['force_notification']
        if condition:
            res.append({
                'title': message['subject'] or '',
                'msg': message['body'],
                'type': this['mode'] or 'notify',
                'sticky': user['notification_sticky'],
            })
    model.write(cr, uid, ids, {'mode': 'delivery'}, context=context)
    return res

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
