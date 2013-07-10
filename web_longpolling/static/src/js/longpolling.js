openerp.web_longpolling = function(instance) {
    var ERROR_DELAY = 30000;
    instance.web.LongPolling = instance.web.Controller.extend({
        init_longpolling: function(parent, service, success, error){
            var self = this;
            this.longpolling_service = false;
            this.rpc('/web/longpolling/get_url', {}).then(function(url){
                if (url) {
                    self.parent = parent;
                    self.longpolling_service = '/openerplongpolling' + service;
                    self.longpolling_success = success || function(collection){};
                    self.longpolling_error = error || function(collection){};
                    self.longpolling();
                }
            });
        },
        longpolling: function(){
            var self = this;
            $.ajax({
                url: this.longpolling_service,
                type: 'GET',
                data: {},
                cache: false,
                //success: this.longpolling_success,
                //error: this.longpolling_error,
                dataType: 'json',
                //complete: longpolling, 
                timeout: ERROR_DELAY
            }).then(this.longpolling_success)
              .fail(this.longpolling_error)
              .done(function(unused, e) {self.longpolling();});
        },
    });
    // just for test 
    instance.web.WebClient.include({ 
        show_common: function() {
            this._super();
            self.longpolling = new instance.web.LongPolling();
            self.longpolling.init_longpolling(this, 'toto/tata/titi', function(yeah) {
                console.log('success')
                console.log(yeah)
            }, function(jqXHR, textStatus) {
                console.log('error')
                console.debug(jqXHR)
                console.debug(textStatus)
            });
        },
    });
};
