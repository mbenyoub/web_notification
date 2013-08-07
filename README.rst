Long polling
============

With the long polling technique, the client requests information from the server in a way 
similar to a normal polling; however, if the server does not have any 
information available for the client, then instead of sending an empty 
response, the server holds the request and waits for information to become 
available (or for a suitable timeout event), after which a complete response 
is finally sent to the client.

In OpenERP it is a bad idea to use long polling, because each long polling 
connection opens a thread for many seconds. If all the threads are open, the 
OpenERP server will be unavailable

One solution is to start a server using greenlets. All the poll have got 
the same thread. 

.. warning:: One polling can block all other ones

We don't replace the wsgi OpenERP server. But we can start 
another server in parallel whith greenlet just for the long polling. the other
use the OpenERP server.

What is the requirement
-----------------------

We need to get 2 python eggs:

* gevent: supply a wsgi client based on greenlet, and patch the python eggs
  to remove blocking loop.
* gevent_psycopg2: Patch psycopg2 egg for gevent


Appach or Nginx to make a dispatcher.

How to use long polling with OpenERP
------------------------------------

Make your Nginx/Appach conf
~~~~~~~~~~~~~~~~~~~~~~~~~~~

exemple a conf for nginx::

    worker_processes  1;

    events {
        worker_connections  1024;
    }

    http {
        server {
            listen  80;
            server_name www.myopenerp.fr;
            location / {
              proxy_pass   http://127.0.0.1:8069;
            }
            location /openerplongpolling {
              proxy_pass   http://127.0.0.1:8068;
            }
        }
    }

/etc/hosts::

    127.0.0.1       www.myopenerp.fr


the port:

* 8069: the OpenERP server
* 8068: the long polling server

``/openerplongpolling`` is the default path to dispatch the poll

Start the OpenERP server
~~~~~~~~~~~~~~~~~~~~~~~~

Install the ``web_longpolling`` module or module which depend of 
``web_longpolling``::

    oe -d mydb -i web_longpolling

The configuration file can define the timeout(default: 60 second) and the 
path(default: /openerplongpolling) of dispatch. etc/openerp.cfg::

    longpolling_path = /otherpath
    longpolling_timeout = 30


Start the long polling server
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

start the server::

    python web_longpolling/server.py -d mydb


the server has 3 options:

* -d: Data bases names (Default: the conf file db_name)
* -i: Interface(Default: 127.0.0.1)
* -p: Port(Default: 8068)
* --max-cursor: The max number of the simultaneous cursor open by databases


How to use long polling in OpenERP module
-----------------------------------------

Module
~~~~~~

You have to add ``web_longpolling`` on the dependencies of your module. The 
module add Javascript class to call longpolling and Python class to declare the
route

Python
~~~~~~

The controller is call by the server gevent to get data on long polling mode.
You must declare the route(s) for each controller with a decorator::

    from openerp.addons.web_longpolling.longpolling import longpolling


    @longpolling.route('/mainroute')
    @longpolling.route('/otherroute')
    @longpolling.route('/varroute/<var1>/<var2>')
    def myfunction(request, **kwargs):
        var1 = kwargs.get('var1')
        var2 = kwargs.get('var2')

        ...

        return ...

The decorator route has got thre arguments

* path: by default is '/'
* mode: (json/http) by default is 'json'
* mustbeauthenticated: (True/False) by default is 'True'

.. warning:: A assert wille be raised if you fill bad arguments
.. warning:: Dont put the long polling path in path, because it is added automaticly by the decorator


The route are only declared on the gevent server not in the OpenERP server::

    2013-08-07 07:15:02,386 64916 INFO longpolling openerp.addons.web_longpolling.longpolling: Add the rule: 'myfunction:/openerplongpolling/varroute/<var1>/<var2>'
    2013-08-07 07:15:02,386 64916 INFO longpolling openerp.addons.web_longpolling.longpolling: Add the rule: 'myfunction:/openerplongpolling/otherroute'
    2013-08-07 07:15:02,386 64916 INFO longpolling openerp.addons.web_longpolling.longpolling: Add the rule: 'myfunction:/openerplongpolling/mainroute'
    2013-08-07 07:15:02,703 64916 INFO longpolling openerp.modules.loading: Modules loaded.
    2013-08-07 07:15:02,705 64916 INFO longpolling openerp.addons.web_longpolling.longpolling: Start long polling server '127.0.0.1':8068

We want that the longpolling controller look like at the OpenERP controller.
So we use orm to get data::

    user = request.model('res.users')
    user.read([request.uid], ['partner_id], context=request.context)


.. warning:: The request.uid exist only if the user is authenticated
.. warning:: A ``AuthenticationError`` will be raised if you use OpenERP Model whithout be authenticate
.. warning:: The long polling controller doesn't allow the write in database, the cursor are rollbacked before to close the connection


the timeout of the longpolling can be got by the get_timeout function::

    from openerp.addons.web_longpolling.longpolling import get_timeout

    timeout = get_timeout()


Javascript
~~~~~~~~~~~

In javascript you have to create a new instance of ``LongPolling`` and call the 
``start_longpolling`` function::

    this.lp = new instance.web.LongPolling();
    session = this.session; // it is the OpenERP session, in function of the location
                            // the session might have not be in DOM.
    path = '/mainpath';
    param = {}; // all param are on the controller kwargs
    successcallback = function(result){
    };
    errorcallback = function(xhr, status){
    };
    this.lp.start_longpolling(session, path, param, sucesscallback, errorcallback)

.. warning:: The session is used to get the session in the controller.

After call of the success or error callback if you want write on the database, 
you must use a simple poll in the callback::

    var self = this;
    successcallback = function (result) {
        self.rpc(' ... ', {'write': result});
    }

If the long polling and the polling are linked, you should use deferred. the 
recall of the controller wait while the deferred are not resolved::

    var self = this;
    successcallback = function (result) {
        var deferred = $.Deferred();
        self.rpc(' ... ', {'write': result}).then (function () {
            deferred.resolve();
        });
        return deferred;
    }

