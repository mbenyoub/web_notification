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
                        var deferred = $.Deferred();
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
                        var notif_ids = _.pluck(notifications, 'id');
                        notif.call('write', [notif_ids, {mode: 'delivery'}])
                            .then(function () {
                                deferred.resolve();
                            });
                        return deferred;
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
