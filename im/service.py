# -*- coding: utf-8 -*-

from openerp.addons.web_longpolling.longpolling import longpolling
from openerp.addons.web_longpolling.session import AbstractAdapter
from openerp import SUPERUSER_ID
from openerp.tools.misc import DEFAULT_SERVER_DATETIME_FORMAT
from datetime import datetime


class UsersAdapter(AbstractAdapter):
    channel = 'im_user'

    def get(self, messages):
        res = []
        for m in messages:
            if m['values']['forservice']:
                res.append(m)
        return res


@longpolling.service('im', adapter=UsersAdapter)
def update_connection(service):
    status = service.listen()
    user = service.model(SUPERUSER_ID, 'im.user')
    states = {}
    for s in status:
        im_status = user.read(s['user_id']['id'], ['im_status'])['im_status']
        if im_status == s['im_status']:
            continue
        else:
            states[s['user_id']['id']] = s['im_status']
    users_ids = user.search([('im_status', '=', True)])
    # define the connected user
    for u_id, state in states.items():
        if u_id in users_ids and not state:
            users_ids.remove(u_id)
        elif u_id not in users_ids and state:
            users_ids.append(u_id)
    for user_id, state in states.items():
        vals = {
            'im_status': state,
            'im_last_status_update': datetime.now().strftime(
                DEFAULT_SERVER_DATETIME_FORMAT),
        }
        user.write([user_id], vals)
        # make one notification for each connected user
        for u_id in users_ids:
            if u_id == user_id:
                # notify himself for know if we are connected or not
                continue
            service.notify(
                'im_user', SUPERUSER_ID, forid=u_id, id=user_id,
                forservice=False, im_status=state)

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
