openerp.web_notification = function (instance) {

    instance.web.WebClient.include({ 
        init:function (parent){
            this.lg_notification = new instance.web.LongPolling();
            this._super(parent);
        },
        show_application: function() {
            var self = this;
            this._super();
            var notif = new instance.web.Model('mail.notification');
            if (!this.lg_notification.longpolling_run){
                this.lg_notification.start_longpolling(
                    this.session, '/notification', {},
                    function (notifications) {
                        _(notifications).each( function(notification) {
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
                    }
                );
            }
        },
        on_logout: function() { 
            this.lg_notification.stop_longpolling();
            this._super();
        },
    });
};
