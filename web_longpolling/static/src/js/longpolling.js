openerp.web_longpolling = function(instance) {
    var ERROR_DELAY = 30000;
    instance.web.LongPolling = instance.web.Controller.extend({
        start_longpolling: function(parent, service, data, success, error){
            var self = this;
            this.longpolling_service = false;
            this.rpc('/web/longpolling/get_url', {}).then(function(url){
                if (url) {
                    self.parent = parent;
                    self.longpolling_service = '/openerplongpolling';
                    self.longpolling_data = data || {};
                    if (service.indexOf('/') === 0) 
                        self.longpolling_service += service;
                    else
                        self.longpolling_service += '/' + service
                    self.longpolling_success = success || function(collection){};
                    //TODO call crashmanager
                    self.longpolling_error = error || function(xhr, status, errorThrown){};
                    self.longpolling_run= true;
                    self.longpolling();
                }
            });
        },
        stop_longpolling= function(){
            this.longpolling_run = false;
        },
        longpolling: function(){
            var self = this;
            console.log(this);
            $.ajax({
                url: this.longpolling_service,
                type: 'GET',
                data: {
                    db: self.parent.session.db,
                    uid: self.parent.session.uid,
                    data: JSON.stringify(self.longpolling_data)
                },
                cache: false,
                dataType: 'json',
                timeout: ERROR_DELAY,
                complete: function(xhr, status, errorThrown){
                    if (status === 'error' || !xhr.responseText) {
                        self.longpolling_error(xhr, status, errorThrown);
                        if (xhr.status !== 404) self.longpolling_run = false;
                    } else {
                        var data = xhr.responseText;
                        self.longpolling_success(data);
                    }
                    if (self.longpolling_run) self.longpolling();
                }
            })
        },
    });
    // just for test 
    instance.web.WebClient.include({ 
        show_common: function() {
            this._super();
            self.longpolling = new instance.web.LongPolling();
            self.longpolling.start_longpolling(
                this, '/42', 
                {toto: 'tata'},
                function(yeah) {
                console.log('success')
                console.log(yeah)
            });
        },
    });
};
