openerp.web_notification = function (instance) {

    var _cp_path = '/web/notification/';
    // set interval between 2 event for get notifications in ms
    var notification_timeout_interval = 10000; // 10 second
    // We get the notification only during the user work
    // for that we have a counter when the counter = 0 we don't get
    // notification
    var notification_timeout_number = 0; 
    // when we use some rpc method we fill the timeout number by timeout
    // number max here 30 = 5 * 6, because the interval = 10 s
    // so the timeout number max is 5 mn
    var notification_timeout_number_max = 30;

    // inherit method to change the timeout number
    instance.web.Query.include({
        _execute: function () {
            notification_timeout_number = notification_timeout_number_max;
            return this._super();
        },
    });

    instance.web.Model.include({
        call: function (method, args, kwargs, options) {
            notification_timeout_number = notification_timeout_number_max;
            return this._super(method, args, kwargs, options);
        },
        exec_workflow: function (id, signal) {
            notification_timeout_number = notification_timeout_number_max;
            return this._super(id, signal);
        },
        call_button: function (method, args) {
            notification_timeout_number = notification_timeout_number_max;
            return this._super(method, args);
        },
    });

    // launch timeout for notification
    instance.web.WebClient.include({ 
        show_common: function() {
            this._super();
            this.get_notifications();
        },
        get_notifications: function(){
            var self = this;
            setTimeout( function(){
                if (self.isDestroyed())
                    return
                if (notification_timeout_number) {
                    notification_timeout_number =  notification_timeout_number -1;
                    self.rpc_get_connection()
                        .done( function(notifications) {
                        _(notifications).each( function(notification) {
                            if (notification.type == 'warn'){
                                self.do_warn(notification.title, 
                                             notification.msg,
                                             notification.sticky);
                            }else{
                                if (notification.type == 'notify'){
                                    self.do_notify(notification.title, 
                                                   notification.msg,
                                                   notification.sticky);
                                }
                            }
                        });
                    });
                }
                self.get_notifications()
            }, notification_timeout_interval);
        },
        rpc_get_connection: function () {
            var ret = new $.Deferred();
            var self = this;
            // unactive the crashmanager because we dont want an error here
            // if the serveur is down 
            this.crashmanager.active = false;
            this.rpc(_cp_path + 'get_notifications', {})
                .done( function (notifications) {
                    ret.resolve(notifications);
                    // no error so we reactive the crashmanager
                    self.crashmanager.active = true;
                }).fail( function (error) {
                    notification_timeout_number = 0;
                    ret.resolve([{
                        'title': 'Error',
                        'msg': 'The client has been deconnected',
                        'sticky': false,
                        'type': 'warn',
                    }])
                    ret.reject(error);
                    setTimeout( function (){
                        // we reactive after little time because we let 
                        // the carsmanger the time to consum the events 
                        // before reactive crashmanager
                        self.crashmanager.active = true;
                    }, 100);
                });
            return ret;
        },
    });
};
