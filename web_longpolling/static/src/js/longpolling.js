openerp.web_longpolling = function(instance) {
    var ERROR_DELAY = 5000;
    instance.web.LongPolling = instance.web.Controller.extend({
        init_longpolling: function(parent, service, success, error){
            var self = this;
            this.longpolling_service = false;
            this.rpc('/web/longpolling/get_url', {}).then(function(url){
                if (url) {
                    self.parent = parent;
                    self.longpolling_service = url + '/longpolling' + service;
                    self.longpolling_success = success || function(collection){
                        console.log('success')
                        console.log(yeah)
                        debugger;
                    };
                    self.longpolling_error = error || function(collection){};
                    self.longpolling();
                }
            });
        },
        longpolling: function(){
            //var self = this;
            //this.rpc(this.longpolling_service, {}, {shadow: true})
                //.then(this.longpolling_success, function(unused, e) {                                                   
                    //e.preventDefault();
                    //setTimeout(_.bind(self.longpolling, self), ERROR_DELAY);
                //})
            $.ajax({
                url: this.longpolling_service,
                type: 'GET',
                data: {},
                cache: false,
                success: this.longpolling_success,
                error: this.longpolling_error,
                dataType: 'json',
                complete: longpolling, 
                complete: function (xhr, status) {
                    if (status === 'error' || !xhr.responseText) {
                        console.log('ko')
                    } else {
                        var data = xhr.responseText;
                        consolo.log('YEAKKKKKKKKK');
                    }
                },
                timeout: 30000 })
        },
    });
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
