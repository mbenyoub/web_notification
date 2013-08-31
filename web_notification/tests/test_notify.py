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
        assert messages[0]['body'] == 'test body'
        assert messages[0]['mode'] == 'notify'

    def test_notify(self):
        vals = {
            'subject': 'test',
            'body': 'test body',
            'user_ids': [self.uid],
            'mode': 'notify',
        }
        self.registry('ir.notification').create(self.cr, self.uid, vals)
        sleep(0)
        messages = NotificationAdapter(self.r).listen(self.uid)
        self.assert_result(messages)

    def test_user_post_notification(self):
        self.registry('res.users').post_notification(
            self.cr, self.uid, self.uid, title='test', message='test body')
        sleep(0)
        messages = NotificationAdapter(self.r).listen(self.uid)
        self.assert_result(messages)

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
