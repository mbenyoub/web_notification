# -*- coding: utf-8 -*-

import openerp.addons.web.http as openerpweb
from .longpolling import get_path


class WebNotification(openerpweb.Controller):
    _cp_path = "/web/longpolling"

    @openerpweb.jsonrequest
    def get_path(self, request):
        return get_path()

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
