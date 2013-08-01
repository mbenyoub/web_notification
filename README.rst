Long polling
============

With long polling, the client requests information from the server in a way 
similar to a normal polling; however, if the server does not have any 
information available for the client, then instead of sending an empty 
response, the server holds the request and waits for information to become 
available (or for a suitable timeout event), after which a complete response 
is finally sent to the client.

In OpenERP v7 it is dangeourous to do long polling, because for each poll 
connection open a thread for some second. If all the thread are open, the 
OpenERP server will be inacessible

The solution is to start a server with greenlet event. All the poll have got 
the same thread. 

.. warning:: One poll can block all the polls

We can not and we don't replace the wsgi OpenERP server. But we can start 
another server in paralell whith greenlet just for the long polling. the other
use the OpenERP server.

What is the requirement
-----------------------

We need to get 2 python egg:

* gevent: supply a wsgi client based on greenlet, and patch the python eggs
  to remove blocking loop.
* gevent_psycopg2: Patch psycopg2 egg for gevent


Appach or Nginx to make a dispatcher.

How use long polling with OpenERP
---------------------------------

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

Install the ``web_longpolling`` module or module who depend of 
``web_longpolling``::

    oe -d mydb -i web_longpolling

The configuration file can define the timeout(default: 60 second) and the 
path(default: /openerplongpolling) of dispatch. etc/openerp.cfg::

    longpolling_path = /otherpath
    longpolling_timeout = 30


Start long polling server
~~~~~~~~~~~~~~~~~~~~~~~~~

start the server::

    python web_longpolling/server.py -d mydb


the server has 3 options:

* -d: Data bases names (Default: the conf file db_name)
* -i: Interface(Default: 127.0.0.1)
* -p: Port(Default: 8068)

