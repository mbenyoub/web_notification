# -*- coding: utf-8 -*-

import openerp.addons.web.http as openerpweb
from openerp.tools import config


class WebNotification(openerpweb.Controller):
    _cp_path = "/web/longpolling"

    @openerpweb.jsonrequest
    def get_url(self, request):
        host = config.get('longpolling_server_host', '127.0.0.1')
        if host.lower() == 'none':
            return False
        port = config.get('longpolling_server_port', '8068')
        return "http://%s:%s" % (host, port)

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
