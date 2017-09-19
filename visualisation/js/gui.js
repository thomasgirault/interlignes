class Controls{    
    constructor(params) {        
        this.gui = new dat.GUI();
        var stp = 1;
        for(var name in params){
            var p = params[name];
            this.add_param(name, p["val"], p["min"], p["max"], stp);
        }
    }
    
    add_param(n, val, min_, max_, stp){
        var o = {};
        o[n] = val;       
        this.gui.add(o, n, min_, max_).onChange( function(value) {
            $.ajax({
                type: "POST",
                url: "http://localhost:8888/param/" + n + "/" + Math.round(value),
                data: JSON.stringify({n: Math.round(value)}),
                contentType: "application/json; charset=utf-8",
                dataType: "json",
                success: function(data){console.log(data);},
                failure: function(errMsg) {
                    alert(errMsg);
                }
            });
        });
    }
}

params = {"min_depth":{"val":0, "min":0, "max":255},
         "max_depth":{"val":255, "min":0, "max":255},
         "theta":{"val":0, "min":0, "max":255}, 
         "MAX_DIST":{"val":40, "min":1, "max":70}, 
         "save":{"val":false, "min":false, "max":true}};

window.onload = function(){          
    var c = new Controls(params);
};
