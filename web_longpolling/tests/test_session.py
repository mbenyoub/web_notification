# -*- coding: utf-8 -*-

from openerp.tests.common import TransactionCase
from ..session import OpenERPRegistry
from ..notify import get_channel
from simplejson import dumps


class TestOpenERPRegistry(TransactionCase):

    def tearDown(self):
        OpenERPRegistry.registries = {}

    def test_add(self):
        r = OpenERPRegistry.add(self.cr.dbname, 2)
        assert r.registries[self.cr.dbname] == r
        assert r.registry.db_name == self.cr.dbname
        assert r.maxcursor == 2

    def test_get(self):
        OpenERPRegistry.add(self.cr.dbname, 2)
        r = OpenERPRegistry.get(self.cr.dbname)
        assert r.registries[self.cr.dbname] == r
        assert r.registry.db_name == self.cr.dbname
        assert r.maxcursor == 2

    def test_get_openerpobject(self):
        r = OpenERPRegistry.add(self.cr.dbname, 2)
        user = r.get_openerpobject(self.uid, 'res.users')
        assert user.search([])
        assert r.maxcursor == 2

    def test_listen(self):
        r = OpenERPRegistry.add(self.cr.dbname, 2)
        r.listen()
        from gevent import sleep
        sleep(1)
        message = dumps({
            'channel': 'test1',
            'uid': self.uid,
            'values': {},
        })
        self.cr.execute('NOTIFY ' + get_channel() + ', %s;', (message,))
        self.cr.commit()
        sleep(0.1)
        message = dumps({
            'channel': 'test2',
            'uid': self.uid,
            'values': {},
        })
        self.cr.execute('NOTIFY ' + get_channel() + ', %s;', (message,))
        self.cr.commit()
        sleep(0.1)
        self.cr.execute('NOTIFY ' + get_channel() + ', %s;', (message,))
        self.cr.commit()
        sleep(0.1)
        assert r.received_message['test1']
        assert r.received_message['test2']
        assert len(r.received_message['test2']) == 2


# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
