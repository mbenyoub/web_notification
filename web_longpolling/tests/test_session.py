# -*- coding: utf-8 -*-

from openerp.tests.common import TransactionCase
from ..session import OpenERPRegistry


class TestOpenERPRegistry(TransactionCase):

    def test_add(self):
        r = OpenERPRegistry.add(self.cr.dbname, 2)
        assert r.registries[self.cr.dbname] == r
        assert r.registry.db_name == self.cr.dbname
        assert r.maxcursor == 2

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
