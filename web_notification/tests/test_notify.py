# -*- coding: utf-8 -*-

from openerp.tests.common import TransactionCase
from openerp.addons.web_socketio.session import OpenERPRegistry
from ..controller import NotificationAdapter
from gevent import sleep


class TestIrNotification(TransactionCase):

    def tearDown(self):
        super(TestIrNotification, self).tearDown()
        OpenERPRegistry.registries = {}

    def setUp(self):
        super(TestIrNotification, self).setUp()
        self.r = OpenERPRegistry.add(self.cr.dbname, 2)
        self.r.listen()

    def assert_result(self, messages):
        assert messages
        assert messages[0]['to_id'] == self.uid
        assert messages[0]['subject'] == 'test'
        assert messages[0]['body'] == '<p>test body</p>'
        assert messages[0]['mode'] == 'notify'

    def test_notify(self):
        vals = {
            'subject': 'test',
            'body': 'test body',
            'user_ids': [(4, self.uid)],
            'mode': 'notify',
        }
        self.registry('ir.notification').create(self.cr, self.uid, vals)
        sleep(0)
        messages = NotificationAdapter(self.r, 'socket').listen(self.uid)
        self.assert_result(messages)

    def test_user_post_notification(self):
        notification_id = self.registry('res.users').post_notification(
            self.cr, self.uid, self.uid, title='test', message='test body')
        sleep(0)
        messages = NotificationAdapter(self.r, 'socket').listen(self.uid)
        self.assert_result(messages)
        r = self.registry('ir.notification').read(
            self.cr, self.uid, notification_id, ['user_ids'])
        self.assertEqual(r['user_ids'], [self.uid])


# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
