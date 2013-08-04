openerp.web_longpolling = function(instance) {
    instance.web.LongPolling = instance.web.Controller.extend({
        init: function(){
            this._super.apply(this, arguments);
            this.longpolling_run = false;
        },
        start_longpolling: function(session, service, data, success, error){
            var self = this;
            self.session = session;
            this.rpc('/web/longpolling/get_path', {}).then(function (path){
                self.longpolling_service = path;
                self.longpolling_data = data || {};
                if (service.indexOf('/') === 0) 
                    self.longpolling_service += service;
                else
                    self.longpolling_service += '/' + service
                self.longpolling_success = success || function(collection){};
                self.longpolling_error = error || function(xhr, status){};
                self.longpolling_run= true;
                self.longpolling();
            });
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
                    var x;
                    if (status === 'error' || !xhr.responseText) {
                        x = self.longpolling_error(xhr, status, errorThrown);
                        if (xhr.status === 404) self.longpolling_run = false;
                    } else {
                        var data = JSON.parse(xhr.responseText);
                        x = self.longpolling_success(data);
                    }
                    $.when(x).then(function (){
                        if (self.longpolling_run) self.longpolling();
                    });
                }
            })
        },
    });
};
