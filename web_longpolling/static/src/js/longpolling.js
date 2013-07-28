openerp.web_longpolling = function(instance) {
    instance.web.LongPolling = instance.web.Controller.extend({
        init: function(){
            this._super.apply(this, arguments);
            this.longpolling_run = false;
            this.crashmanager = new instance.web.CrashManager();
        },
        start_longpolling: function(session, service, data, success, error){
            var self = this;
            this.longpolling_service = false;
            self.session = session;
            self.longpolling_service = '/openerplongpolling';
            self.longpolling_data = data || {};
            if (service.indexOf('/') === 0) 
                self.longpolling_service += service;
            else
                self.longpolling_service += '/' + service
            self.longpolling_success = success || function(collection){};
            self.longpolling_error = error || function(xhr, status){
                if (xhr.status !== 502 && xhr.status !== 408) {
                    var error = {
                        code: xhr.status,
                        message: "XmlHttpRequestError ",
                        data: {
                            type: "xhr" + status, 
                            debug: xhr.responseText, 
                            objects: [xhr] 
                        }
                    };
                    self.crashmanager.rpc_error(error);
                }
            };
            self.longpolling_run= true;
            self.longpolling();
        },
        stop_longpolling: function(){
            this.longpolling_run = false;
        },
        longpolling: function(){
            var self = this;
            $.ajax({
                url: this.longpolling_service,
                type: 'GET',
                data: {
                    session_id: self.session.session_id,
                    data: JSON.stringify(self.longpolling_data)
                },
                cache: false,
                dataType: 'json',
                complete: function(xhr, status, errorThrown){
                    if (status === 'error' || !xhr.responseText) {
                        self.longpolling_error(xhr, status, errorThrown);
                        if (xhr.status === 404) self.longpolling_run = false;
                    } else {
                        var data = JSON.parse(xhr.responseText);
                        self.longpolling_success(data);
                    }
                    if (self.longpolling_run) self.longpolling();
                }
            })
        },
    });
};
