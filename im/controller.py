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


@longpolling.route('/im', adapter=MessageAdapter)
def receive_message(session, **kwargs):
    context = session.context
    im_user_obj = session.model('im.user')
    my_id = im_user_obj.get_by_user_id(session.uid, context=context)
    session.notify('im_user', state='connected', user_id=my_id, forservice=True)
    message_received = session.listen(my_id['id'])
    return {
        'user_id': my_id,
        'messages': message_received,
    }

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
