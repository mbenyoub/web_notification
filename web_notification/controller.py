# -*- coding: utf-8 -*-

import openerp.addons.web.http as openerpweb


class WebNotification(openerpweb.Controller):
    _cp_path = "/web/notification"

    @openerpweb.jsonrequest
    def get_notifications(self, request):
        model = request.session.model('mail.notification')
        mail = request.session.model('mail.message')
        context = request.session.context
        user = request.session.model('res.users').read(
            [request.session._uid], ['partner_id', 'notification_sticky'],
            context=context, load="_classic_write")[0]
        domain = [
            ('partner_id', '=', user['partner_id']),
            ('mode', 'in', ('notify', 'warn', False)),
        ]
        ids = model.search(domain, context=context)
        res = []
        for this in model.read(ids,
                               ['message_id', 'mode', 'force_notification'],
                               context=context,
                               load="_classic_write"):
            message = mail.read([this['message_id']],
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
        model.write(ids, {'mode': 'delivery'}, context=context)
        return res

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
