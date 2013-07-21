openerp.web_notification = function (instance) {

    instance.web.WebClient.include({ 
        init:function (parent){
            this._super(parent);
            this.longpolling = new instance.web.LongPolling();
        },
        show_application: function() {
            var self = this;
            this._super();
            console.log('yop')
            if (!this.longpolling.longpolling_run){
                this.longpolling.start_longpolling(
                    this.session, '/notification', {},
                    function (notifications) {
                        console.log(notifications);
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
                    },
                    function (xhr, status) {
                        console.log(xhr);
                        console.log(status);
                    }
                );
            }
        },
        on_logout: function() { 
            this.longpolling.stop_longpolling();
            this._super();
        },
    });
};
