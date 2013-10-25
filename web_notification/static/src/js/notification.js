openerp.web_notification = function (instance) {
    instance.web.WebClient.include({ 
        show_application: function() {
            var self = this;
            this._super();
            instance.web.longpolling_socket.on('get notification', function (notification) {
                console.log(notification)
                if (notification.mode == 'warn'){
                    self.do_warn(notification.subject, 
                                 notification.body,
                                 notification.sticky);
                }else{
                    if (notification.mode == 'notify'){
                        self.do_notify(notification.subject, 
                                       notification.body,
                                       notification.sticky);
                    }
                }
            });
        },
    });
};
