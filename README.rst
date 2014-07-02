Web notification for OpenERP v7
===============================

.. warning::
    Odoo has is own internal bus service in v8, the sockectio won't be supported.
    The branch v8 implement notification with the odoo bus

How Install the module ``web_notification``
-------------------------------------------

Make your Nginx/Apache conf
~~~~~~~~~~~~~~~~~~~~~~~~~~~

example conf for nginx::

    worker_processes  1;

    events {
        worker_connections  1024;
    }

    http {
        server {
            listen  80;
            server_name www.myopenerp.fr;
            location /socket.io {
                proxy_pass   http://127.0.0.1:8068;
                proxy_http_version 1.1;

                proxy_set_header Upgrade $http_upgrade;
                proxy_set_header Connection "upgrade";
                proxy_set_header Host $host;

                proxy_set_header X-Real-IP $remote_addr;
                proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
                proxy_set_header X-Forwarded-Proto https;

                proxy_redirect off;
            }
            location / {
                proxy_pass   http://127.0.0.1:8069;
            }
        }
    }


/etc/hosts::

    127.0.0.1       www.myopenerp.fr


the port::

    8069: the OpenERP server
    8068: the SocketIO server


/socketio is the default path to dispatch the poll


With buildout
~~~~~~~~~~~~~

Example of buildout configuration::

    [buildout]
    parts = openerp
    versions = versions
    extensions = gp.vcsdevelop
    vcs-extend-develop = git+http://github.com/buildout/buildout.git#egg=zc.buildout
    vcs-update = true
    develop = web_socketio/oe_web_socketio
    
    [openerp]
    recipe = anybox.recipe.openerp[bzr]:server
    version = bzr lp:openobject-server/7.0 openerp-server last:1
    addons = bzr lp:openobject-addons/7.0 openerp-addons last:1
             bzr lp:openerp-web/7.0 openerp-web last:1 subdir=addons
             hg http://bitbucket.org/anybox/web_socketio web_socketio default
             hg http://bitbucket.org/anybox/web_notification web_notification socketio
    
    eggs = oe.web.socketio
    
    openerp_scripts = nosetests=nosetests command-line-options=-d
                      oe_web_socketio=oe_web_socketio 
    
    [versions]
    lxml = 2.3.3
    docutils = 0.9
    collective.recipe.sphinxbuilder = 0.7.3
    pyparsing = 1.5.6
    Werkzeug = 0.8.3

Build the buildout::

    bin/buildout -c buildout.cfg

Run the OpenERP server in the first shell::

    bin/start_openerp -d mydb -i web_notification

Run the Gevent SocketIO server in the second shell::

    ./bin/oe_web_socketio -d mydb

Without buildout
~~~~~~~~~~~~~~~~

You must get the modules web_socketio, web_longpolling and web_im::

    hg clone http://bitbucket.org/anybox/web_socketio
    hg clone http://bitbucket.org/anybox/web_notification

Install the python eggs needed for gevent_socketio::

    pip install gevent
    pip install gevent_psycopg2
    pip install gevent_socketio

Run the OpenERP server in the first shell::

    oe -d mydb -i web_notification

Run the Gevent SocketIO server in the second shell::

    python web_socketio/web_socketio/server.py -d mydb
