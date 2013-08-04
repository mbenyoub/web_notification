# -*- coding: utf-8 -*-

from openerp.addons.web_longpolling.longpolling import longpolling

POLL_SLEEP = 0.5


@longpolling.route('/notification')
def get_notifications(request, **kwargs):
    from gevent import sleep
    model = request.model('mail.notification')
    mail = request.model('mail.message')
    context = request.context
    user = request.model('res.users').read(
        [request.uid], ['partner_id', 'notification_sticky'],
        context=context, load="_classic_write")[0]
    domain = [
        ('partner_id', '=', user['partner_id']),
        ('mode', 'in', ('notify', 'warn', False, '')),
        '|',
        ('force_notification', '=', True),
        ('message_id.author_id', '=', user['partner_id']),
    ]
    while True:
        ids = model.search(domain, context=context)
        # we are on longpolling if they are no response then the time out cut
        # the connection and restart it
        if ids:
            break
        sleep(POLL_SLEEP)

    res = []
    for this in model.read(ids, ['message_id', 'mode'],
                           context=context, load="_classic_write"):
        message = mail.read([this['message_id']], ['subject', 'body'],
                            load="_classic_write", context=context)[0]
        res.append({
            'id': this['id'],
            'title': message['subject'] or '',
            'msg': message['body'],
            'type': this['mode'] or 'notify',
            'sticky': user['notification_sticky'],
        })
    return res

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
