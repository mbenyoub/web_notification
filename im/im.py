# -*- coding: utf-8 -*-
##############################################################################
#
#    OpenERP, Open Source Management Solution
#    Copyright (C) 2004-2010 Tiny SPRL (<http://tiny.be>).
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU Affero General Public License as
#    published by the Free Software Foundation, either version 3 of the
#    License, or (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU Affero General Public License for more details.
#
#    You should have received a copy of the GNU Affero General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
##############################################################################

import openerp
from openerp.tools.misc import DEFAULT_SERVER_DATETIME_FORMAT
import datetime
from datetime import datetime as dt
from openerp.osv import osv, fields
import logging
from openerp.addons.web_longpolling.longpolling import longpolling

_logger = logging.getLogger(__name__)

POLL_TIMER = 30  # TODO use longpolling timeout
DISCONNECTION_TIMER = POLL_TIMER + 5


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
    while ((now - start).seconds < POLL_TIMER - 5) and not message_received:
        sleep(0.1)
        message_received = im_message_obj.get_messages(cr, uid, context=context)
        now = dt.now()

    users_status = im_user_obj.get_users_status(cr, uid, context=context)
    im_user_obj.im_connect(cr, uid, my_id['id'], context=context)

    return {
        'user_id': my_id,
        'status': users_status,
        'messages': message_received,
    }


class im_message(osv.Model):
    _name = 'im.message'

    _order = "date"

    _columns = {
        'message': fields.char(string="Message", size=200, required=True),
        'from_id': fields.many2one(
            "im.user", "From", required=True, ondelete='cascade'),
        'to_id': fields.many2one(
            "im.user", "To", required=True, select=True, ondelete='cascade'),
        'date': fields.datetime("Date", required=True, select=True),
        'read_by_from': fields.boolean('Read by from user'),
        'read_by_to': fields.boolean('Read by to user'),
    }

    _defaults = {
        'date': lambda *args: datetime.datetime.now().strftime(
            DEFAULT_SERVER_DATETIME_FORMAT),
        'read_by_from': False,
        'read_by_to': False,
    }

    def get_messages(self, cr, uid, last=None, context=None):
        users = self.pool.get("im.user")
        my_id = users.get_by_user_id(cr, uid, uid, context=context)["id"]
        domain = [
            '|',
            '&', ('from_id', '=', my_id), ('read_by_from', '=', False),
            '&', ('to_id', '=', my_id), ('read_by_to', '=', False),
        ]
        mess_ids = self.search(
            cr, openerp.SUPERUSER_ID, domain, context=context)
        mess = self.read(cr, openerp.SUPERUSER_ID, mess_ids,
                         ["id", "message", "from_id", 'to_id', "date"],
                         load='_classic_write', context=context)
        for m in mess:
            vals = {}
            if m['from_id'] == my_id:
                vals['read_by_from'] = True
            else:
                vals['read_by_to'] = True
            self.write(
                cr, openerp.SUPERUSER_ID, [m['id']], vals, context=context)

        return mess

    def post(self, cr, uid, message, to_user_id, context=None):
        my_id = self.pool.get('im.user').get_by_user_id(cr, uid, uid)["id"]
        val = {"message": message, 'from_id': my_id, 'to_id': to_user_id}
        self.create(cr, openerp.SUPERUSER_ID, val, context=context)
        return True


class im_user(osv.Model):
    _name = "im.user"

    def get_users_status(self, cr, uid, context=None):
        ids = self.search(cr, openerp.SUPERUSER_ID, [('user', '!=', uid)],
                          context=context)
        return self.read(cr, openerp.SUPERUSER_ID, ids, ['im_status'],
                         context=context)

    def _im_status(self, cr, uid, ids, something, something_else, context=None):
        res = {}
        current = datetime.datetime.now()
        delta = datetime.timedelta(0, DISCONNECTION_TIMER)
        data = self.read(cr, openerp.SUPERUSER_ID, ids, ["im_last_status_update"], context=context)
        for obj in data:
            last_update = datetime.datetime.strptime(
                obj["im_last_status_update"], DEFAULT_SERVER_DATETIME_FORMAT)
            res[obj["id"]] = (last_update + delta) > current

        return res

    def search_users(self, cr, uid, domain, fields, limit, context=None):
        # do not user openerp.SUPERUSER_ID, reserved to normal users
        found = self.pool.get('res.users').search(cr, uid, domain, limit=limit, context=context)
        found = self.get_by_user_ids(cr, uid, found, context=context)
        return self.read(cr, uid, found, fields, context=context)

    def im_connect(self, cr, uid, id, context=None):
        vals = {
            "im_last_status_update": datetime.datetime.now().strftime(
                DEFAULT_SERVER_DATETIME_FORMAT),
        }
        self.write(cr, openerp.SUPERUSER_ID, id, vals, context=context)

    def get_by_user_id(self, cr, uid, user_id, context=None):
        ids = self.get_by_user_ids(cr, uid, [user_id], context=context)
        return ids[0]

    def get_by_user_ids(self, cr, uid, user_ids, context=None):
        users = self.search(
            cr, openerp.SUPERUSER_ID, [('user', 'in', user_ids)], context=None)
        records = self.read(
            cr, openerp.SUPERUSER_ID, users, ['user'], context=None)
        inside = [x['user'][0] for x in records]
        for to_create in user_ids:
            if to_create in inside:
                continue

            created = self.create(
                cr, openerp.SUPERUSER_ID, {"user": to_create}, context=context)
            records.append({"id": created, "user": [to_create, ""]})
        return records

    def assign_name(self, cr, uid, name, context=None):
        id = self.get_by_user_id(cr, uid, context=context)["id"]
        self.write(cr, openerp.SUPERUSER_ID, id, {"assigned_name": name}, context=context)
        return True

    def _get_name(self, cr, uid, ids, name, arg, context=None):
        res = {}
        for record in self.browse(cr, uid, ids, context=context):
            res[record.id] = record.assigned_name
            if record.user:
                res[record.id] = record.user.name
                continue
        return res

    _columns = {
        'name': fields.function(_get_name, type='char', size=200,
                                string="Name", store=True, readonly=True),
        'assigned_name': fields.char(
            string="Assigned Name", size=200, required=False),
        'image': fields.related('user', 'image_small', type='binary',
                                string="Image", readonly=True),
        'user': fields.many2one(
            "res.users", string="User", select=True, ondelete='cascade'),
        'im_last_status_update': fields.datetime(
            string="Instant Messaging Last Status Update"),
        'im_status': fields.function(
            _im_status, string="Instant Messaging Status", type='boolean'),
    }

    _defaults = {
        'im_last_status_update': lambda *args: datetime.datetime.now(
        ).strftime(DEFAULT_SERVER_DATETIME_FORMAT),
    }
