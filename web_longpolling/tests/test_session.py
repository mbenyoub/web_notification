# -*- coding: utf-8 -*-

from openerp.tests.common import TransactionCase
from ..session import OpenERPRegistry, AbstractAdapter
from ..notify import get_channel
from ..longpolling import longpolling
from simplejson import dumps
from gevent import sleep


longpolling.patch_all()


class Adapter(AbstractAdapter):
    channel = 'test'


class TestOpenERPRegistry(TransactionCase):

    def tearDown(self):
        super(TestOpenERPRegistry, self).tearDown()
        OpenERPRegistry.registries = {}

    def setUp(self):
        super(TestOpenERPRegistry, self).setUp()
        self.r = OpenERPRegistry.add(self.cr.dbname, 2)

    def test_add(self):
        assert self.r.registries[self.cr.dbname] == self.r
        assert self.r.registry.db_name == self.cr.dbname
        assert self.r.maxcursor == 2

    def test_get(self):
        r = OpenERPRegistry.get(self.cr.dbname)
        assert r.registries[self.cr.dbname] == r
        assert r.registry.db_name == self.cr.dbname
        assert r.maxcursor == 2

    def test_get_openerpobject(self):
        user = self.r.get_openerpobject(self.uid, 'res.users')
        assert user.search([])
        assert self.r.maxcursor == 2

    def test_listen(self):
        # use sleep to switch to other coroutine
        self.r.listen()
        message = dumps({
            'channel': 'test1',
            'uid': self.uid,
            'values': {},
        })
        self.cr.execute('NOTIFY ' + get_channel() + ', %s;', (message,))
        self.cr.commit()
        sleep(0)
        message = dumps({
            'channel': 'test2',
            'uid': self.uid,
            'values': {},
        })
        self.cr.execute('NOTIFY ' + get_channel() + ', %s;', (message,))
        self.cr.commit()
        sleep(0)
        self.cr.execute('NOTIFY ' + get_channel() + ', %s;', (message,))
        self.cr.commit()
        sleep(0.1)
        assert self.r.received_message['test1']
        assert self.r.received_message['test2']
        assert len(self.r.received_message['test2']) == 2

    def test_cursor(self):
        cr = self.r.cursor()
        cr.execute('select * from res_users where id=%s', (self.uid,))
        assert cr.fetchone()
        cr.close()

    def test_adapter(self):
        self.r.listen()
        message = dumps({
            'channel': 'test',
            'uid': self.uid,
            'values': {
                'uid': self.uid,
            },
        })
        sleep(.1)
        self.cr.execute('NOTIFY ' + get_channel() + ', %s;', (message,))
        self.cr.commit()
        sleep(0)
        messages = Adapter(self.r).listen()
        assert messages
        assert messages[0]['uid'] == self.uid
        assert not self.r.received_message['test']

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
