class Controls{    
    constructor(gui, folder_name, params, url) {
        
        // this.gui = gui; 
        this.folder = gui.addFolder(folder_name);        
        this.url = url;


        var stp = 1;
        for(var name in params){
            var p = params[name];
            if (!p.hasOwnProperty('val')) 
                this.add_button(name);     
            else
                this.add_param(name, p["val"], p["min"], p["max"], stp);
        }
    }
    
    add_button(name){
        var self = this;
        
        var obj = {learnBG:
            function(){
                $.ajax({
                    type: "POST",
                    url: self.url + "/" + name + "/" + Math.round(1),
                    data: JSON.stringify({name: Math.round(0)}),
                    contentType: "application/json; charset=utf-8",
                    dataType: "json",
                    success: function(data){console.log(data);},
                    failure: function(errMsg) {alert(errMsg);}
                });
            }   
        };
        this.folder.add(obj,"learnBG");
    }

    add_param(n, val, min_, max_, stp){
        var o = {};
        o[n] = val;
        var self = this;
        
        this.folder.add(o, n, min_, max_).onChange( function(value) {
            $.ajax({
                type: "POST",
                url: self.url + "/" + n + "/" + Math.round(value),
                data: JSON.stringify({n: Math.round(value)}),
                contentType: "application/json; charset=utf-8",
                dataType: "json",
                success: function(data){console.log(data);},
                failure: function(errMsg) {alert(errMsg);}
            });
        });
    }
}

params = {"min_depth":{"val":0, "min":0, "max":255},
         "max_depth":{"val":255, "min":0, "max":255},
         "theta":{"val":0, "min":0, "max":255}, 
         "MAX_DIST":{"val":40, "min":1, "max":70},
         "min_blob_size":{"val":30, "min":1, "max":300},
         "max_blob_size":{"val":500, "min":100, "max":500},
         "min_norm":{"val":1, "min":0, "max":10},
         "erode_kernel_size":{"val":10, "min":2, "max":20},
         "erode_iterations":{"val":1, "min":1, "max":10},
         "smooth":{"val":0, "min":0, "max":10},
         "extra_spaces":{"val":1, "min":0, "max":20},
         "save":{"val":false, "min":false, "max":true},
         "learnBG":{"min":null, "max":null}
        };

var web_params = {
 "minFontSize":{"val":20, "min":3, "max":100},
 "maxFontSize":{"val":100, "min":30, "max":300},
 "clearPeriod":{"val":20, "min":1, "max":100}
}



window.onload = function(){

    gui = new dat.GUI();
    // gui.remember(params);

    var url_server_params = "http://localhost:8888/param";
    var c = new Controls(gui, "image", params, url_server_params);

    var url_web_params = "http://localhost:8888/web_param";
    var c2 = new Controls(gui, "texte", web_params, url_web_params);

};
