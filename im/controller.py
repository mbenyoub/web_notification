# -*- coding: utf-8 -*-

from openerp.addons.web_longpolling.longpolling import longpolling
from openerp.addons.web_longpolling.session import AbstractAdapter


class MessageAdapter(AbstractAdapter):
    channel = 'im_message'

    def get(self, messages, uid):
        res = []
        for m in messages:
            if m['values']['forid'] == uid:
                res.append(m)
        return res


class UserAdapter(AbstractAdapter):
    channel = 'im_user'

    def get(self, messages, uid):
        res = []
        for m in messages:
            if not m['values']['forservice'] and m['values']['forid'] == uid:
                res.append(m)
        return res


@longpolling.route('/im/message', adapter=MessageAdapter)
def receive_message(session, **kwargs):
    context = session.context
    im_user_obj = session.model('im.user')
    my_id = im_user_obj.get_by_user_id(session.uid, context=context)
    message_received = session.listen(my_id['id'])
    return {
        'user_id': my_id,
        'messages': message_received,
    }


@longpolling.route('/im/user', adapter=UserAdapter)
def update_status_user(session, **kwargs):
    context = session.context
    im_user_obj = session.model('im.user')
    my_id = im_user_obj.get_by_user_id(session.uid, context=context)
    #FIXME the longpolling are not stop after deconnection
    #session.notify('im_user', im_status=True, user_id=my_id, forservice=True)
    return session.listen(my_id['id'])

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
