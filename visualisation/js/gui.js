class Controls {
    constructor(gui, folder_name, params, url) {

        // this.gui = gui; 
        this.folder = gui.addFolder(folder_name);
        this.url = url;


        var stp = 1;
        for (var name in params) {
            var p = params[name];
            if (!p.hasOwnProperty('val'))
                this.add_button(name);
            else
                this.add_param(name, p["val"], p["min"], p["max"], stp);
        }
    }

    add_button(name) {
        var self = this;

        var obj = {
            learnBG:
            function () {
                $.ajax({
                    type: "POST",
                    url: self.url + "/" + name + "/" + Math.round(1),
                    data: JSON.stringify({ name: Math.round(0) }),
                    contentType: "application/json; charset=utf-8",
                    dataType: "json",
                    success: function (data) { console.log(data); },
                    failure: function (errMsg) { alert(errMsg); }
                });
            }
        };
        this.folder.add(obj, "learnBG");
    }

    add_param(n, val, min_, max_, stp) {
        var o = {};
        o[n] = val;
        var self = this;

        this.folder.add(o, n, min_, max_).onChange(function (value) {
            $.ajax({
                type: "POST",
                url: self.url + "/" + n + "/" + Math.round(value),
                data: JSON.stringify({ n: Math.round(value) }),
                contentType: "application/json; charset=utf-8",
                dataType: "json",
                success: function (data) { console.log(data); },
                failure: function (errMsg) { alert(errMsg); }
            });
        });
    }
}

params = {
    "display_mode":{ "val": 0, "min": 0, "max": 2 },
    "depth_ir":{ "val": 0, "min": 0, "max": 1 },
    "min_depth": { "val": 0, "min": 0, "max": 255 },
    "max_depth": { "val": 255, "min": 0, "max": 255 },
    "theta": { "val": 0, "min": 0, "max": 255 },
    "blur":{ "val": 5, "min": 0, "max": 20 },
    "MAX_DIST": { "val": 40, "min": 1, "max": 70 },
    "min_blob_size": { "val": 30, "min": 1, "max": 300 },
    "max_blob_size": { "val": 500, "min": 100, "max": 500 },
    "min_norm": { "val": 1, "min": 0, "max": 10 },
    "erode_kernel_size": { "val": 10, "min": 2, "max": 20 },
    "erode_iterations": { "val": 1, "min": 1, "max": 10 },
    "smooth_path": { "val": 0, "min": 0, "max": 10 },
    "init_texte":{ "val": false, "min": false, "max": true },
    "extra_spaces": { "val": 1, "min": 0, "max": 20 },
    "save": { "val": false, "min": false, "max": true },
    "learnBG": { "min": null, "max": null }
};

var web_params = {
    //  "width_ratio":{"val":800, "min":1920, "max":1920},
    //  "heigth_ratio":{"val":2.55, "min":1, "max":5},

    "minFontSize": { "val": 20, "min": 3, "max": 100 },
    "maxFontSize": { "val": 100, "min": 30, "max": 300 },
    "clearPeriod": { "val": 20, "min": 1, "max": 100 },
    "max_word_ts_interval": { "val": 2, "min": 0, "max": 10 },
    "letter_spaces": { "val": 0, "min": 0, "max": 5 },
    "interlude1": { "val": false, "min": false, "max": true },
    "interlude2": { "val": false, "min": false, "max": true }
};


var mapping_params = {
    "x0": { "val": 0, "min": -1000, "max": 3000 },
    "y0": { "val": 0, "min": -1000, "max": 3000 },
    "x1": { "val": 1920, "min": -1000, "max": 3000 },
    "y1": { "val": 0, "min": -1000, "max": 3000 },
    "x2": { "val": 1920, "min": -1000, "max": 3000 },
    "y2": { "val": 1080, "min": -1000, "max": 3000 },
    "x3": { "val": 0, "min": -1000, "max": 3000 },
    "y3": { "val": 1080, "min": -1000, "max": 3000 }
};


window.onload = function () {

    gui = new dat.GUI();
    // gui.remember(params);

    var url_server_params = "/param";
    var c = new Controls(gui, "image", params, url_server_params);

    var url_web_params = "/web_param";
    var c2 = new Controls(gui, "texte", web_params, url_web_params);

    var url_mapping = "/mapping";
    var c3 = new Controls(gui, "mapping", mapping_params, url_mapping);
};
