(function() {
    var web_notification = openerp.web_notification = {};

    web_notification.Notification = openerp.Widget.extend({
        init: function(parent, user_id) {
            var self = this;
            this._super(parent);
            this.bus = openerp.bus.bus;
            this.channel = 'notify_res_user_' + user_id;
            this.bus.add_channel(this.channel)
            this.bus.on("notification", this, this.on_notification);
            this.bus.start_polling();
        },
        on_notification: function(notification) {
            var self = this;
            var channel = notification[0];
            var message = notification[1];
            if (channel == this.channel) {
                if (message.mode == 'warn'){
                    self.do_warn(message.subject,
                                 message.body,
                                 message.sticky);
                }else{
                    if (message.mode == 'notify'){
                        self.do_notify(message.subject,
                                       message.body,
                                       message.sticky);
                    }
                }
            }
        },
    });
    openerp.web.WebClient.include({
        show_application: function() {
            this._super();
            this.web_notification = new web_notification.Notification(this, this.session.uid);
        },
    });
})();
