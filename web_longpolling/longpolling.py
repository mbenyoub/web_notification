# -*- coding: utf-8 -*-

from simplejson import dumps, loads
from werkzeug.wrappers import Request, Response
from werkzeug.routing import Map, Rule
from werkzeug.exceptions import HTTPException, Unauthorized, RequestTimeout
from werkzeug.exceptions import InternalServerError
from werkzeug.contrib.sessions import FilesystemSessionStore
from openerp.addons.web.http import session_path
from openerp.addons.web.session import AuthenticationError
from openerp.modules.registry import RegistryManager


LONGPOOLTIMEOUT = 30


class LongPolling(object):

    def __init__(self):
        self.path_map = Map()
        self.view_function = {}
        path = session_path()
        self.session_store = FilesystemSessionStore(path)

    def route(self, path='/', mode='json', mustbeauthenticate=True):
        assert path not in (False, None), "Bad route path: " + str(path)
        assert isinstance(path, str), "Path must be a string: " + str(path)
        assert mode in ('json', 'http'), "Mode must be json or http: " + str(path)
        assert isinstance(mustbeauthenticate, bool)

        def wrapper(function):
            if path[0] == '/':
                realpath = '/openerplongpolling' + path
            else:
                realpath = '/openerplongpolling' + '/' + path
            endpoint = '%s:%s' % (function.__name__, realpath)
            rule = Rule(realpath, endpoint=endpoint)
            self.path_map.add(rule)
            old_func = self.view_function.get(endpoint)
            if old_func is not None and old_func != function:
                raise AssertionError('View function mapping is overwriting an '
                                     'existing endpoint function: %s' % endpoint)
            self.view_function[endpoint] = {
                'function': function,
                'mode': mode,
                'mustbeauthenticate': mustbeauthenticate,
            }
            return function
        return wrapper

    def application(self, environ, start_response):
        request = Request(environ)
        response = self.dispatch_request(request)
        return response(environ, start_response)

    def dispatch_request(self, request):
        from gevent import Timeout
        timeout = Timeout(LONGPOOLTIMEOUT)
        timeout.start()
        adapter = self.path_map.bind_to_environ(request.environ)
        try:
            endpoint, values = adapter.match()
            sid = request.cookies.get('sid')
            session = None
            if sid:
                session = self.session_store.get(sid)
            session_id = request.args.get('session_id')
            if session and session_id:
                session = session.get(session_id)

            if session:
                if self.view_function[endpoint]['mustbeauthenticate']:
                    session.assert_valid()

                request.authenticate = True
                request.context = session.context
                request.uid = session._uid
                request.pool = RegistryManager.get(session._db)
                # serialized = False => put the the isolation level
                # READ_COMMITED, without it option, the other commit can not be
                # used and we have always got the same result for each read
                request.cr = request.pool.db.cursor(serialized=False)
            elif self.view_function[endpoint]['mustbeauthenticate']:
                raise AuthenticationError('No session found')
            else:
                request.authenticate = False
                request.context = {}

            values.update(loads(request.args.get('data')))
            result = self.view_function[endpoint]['function'](
                request, **values)
            if request.cr is not None:
                request.cr.commit()
                request.cr.close()

            if self.view_function[endpoint]['mode'] == 'json':
                result = dumps(result)
                mimetype = 'application/json'
            else:
                mimetype = 'text/html'

            return Response(result, mimetype=mimetype)
        except HTTPException, e:
            if request.cr is not None:
                request.cr.close()
            return e
        except AuthenticationError, e:
            # No session = No cursor to close
            return Unauthorized()
        except Timeout, e:
            if request.cr is not None:
                request.cr.close()
            return RequestTimeout()
        except Exception, e:
            if request.cr is not None:
                request.cr.close()
            return InternalServerError(str(e))

longpolling = LongPolling()

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
