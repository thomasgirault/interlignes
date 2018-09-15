class Controls {
    constructor(gui, folder_name, params, url) {

        // this.gui = gui; 
        this.folder = gui.addFolder(folder_name);
        this.url = url;


        var stp = 1;
        for (var name in params) {
            var p = params[name];
            // if (!p.hasOwnProperty('val'))
            if (p['val'] == null)

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


var params = {

    "display_mode": { "val": 0, "min": 0, "max": 2 },
    "depth_ir": { "val": 0, "min": 0, "max": 2 },
    "min_depth": { "val": 0, "min": 0, "max": 255 },
    "max_depth": { "val": 255, "min": 0, "max": 255 },
    "theta": { "val": 0, "min": 0, "max": 255 },
    "blur": { "val": 5, "min": 0, "max": 20 },
    "MAX_DIST": { "val": 73, "min": 1, "max": 73 },
    "min_blob_size": { "val": 20, "min": 1, "max": 300 },
    "max_blob_size": { "val": 500, "min": 100, "max": 500 },
    "min_norm": { "val": 1, "min": 0, "max": 10 },
    "erode_kernel_size": { "val": 10, "min": 2, "max": 20 },
    "erode_iterations": { "val": 1, "min": 1, "max": 10 },
    "max_age": { "val": 5, "min": 1, "max": 30 },
    "min_hits": { "val": 10, "min": 1, "max": 30 },
    "smooth": { "val": 0, "min": 0, "max": 10 },
    "learnBG": { "val": false, "min": false, "max": true },
    "save": { "val": false, "min": false, "max": true }
};


var web_params = {
    //  "width_ratio":{"val":800, "min":1920, "max":1920},
    //  "heigth_ratio":{"val":2.55, "min":1, "max":5},
    "minFontSize": { "val": 10, "min": 3, "max": 100 },
    "maxFontSize": { "val": 40, "min": 15, "max": 300 },
    "clearPeriod": { "val": 5, "min": 0, "max": 100 },
    "max_word_ts_interval": { "val": 2, "min": 0, "max": 10 },
    "kerning": { "val": 0, "min": 0, "max": 100 },
    "word_interspaces": { "val": 2, "min": 0, "max": 10 },
    "ponctuation_proba": { "val": 0, "min": 0, "max": 100 },
    "sentence_interspaces": { "val": 10, "min": 0, "max": 40 },
    "min_distance": { "val": 10, "min": 0, "max": 50 },
    "init_texte": { "val": false, "min": false, "max": true },
    // "anniversaire": { "val": 0, "min": 0, "max": 43 },
    "extra_spaces": { "val": 1, "min": 0, "max": 20 },
    "interlude": { "val": 0, "min": 0, "max": 8 },
    "interlude_play": { "val": false, "min": false, "max": true },
    "video_ok": { "val": true, "min": false, "max": true }
};



// SAVE PARAMS

$.ajax({
    type: "GET",
    async: false,
    url: "http://localhost:8888/params.json",
    contentType: "application/json; charset=utf-8",
    dataType: "json",
    success: function (data) {
        $.each(data, function (key, value) {
            if (key in params) {
                console.log(key, params[key]);
                params[key]["val"] = value;
            }
        });
    },
    failure: function (errMsg) { alert(errMsg); }
});



$.ajax({
    type: "GET",
    async: false,
    url: "http://localhost:8888/text_params.json",
    contentType: "application/json; charset=utf-8",
    dataType: "json",
    success: function (data) {
        $.each(data, function (key, value) {
            if (key in params) {
                console.log(key, params[key]);
                web_params[key]["val"] = value;
            }
        });
    },
    failure: function (errMsg) { alert(errMsg); }
});




function save_all(gui) {
    var obj = {
        save_params:
            function () {
                $.ajax({
                    type: "GET",
                    url: "/save_params",
                    contentType: "application/json; charset=utf-8",
                    dataType: "json",
                    success: function (data) { console.log(data); },
                    failure: function (errMsg) { alert(errMsg); }
                });
            }
    };
    gui.add(obj, "save_params");

}








window.onload = function () {

    gui = new dat.GUI();
    // gui.remember(params);
    console.log(params);

    var url_server_params = "/param";
    var c = new Controls(gui, "image", params, url_server_params);

    var url_web_params = "/web_param";
    var c2 = new Controls(gui, "texte", web_params, url_web_params);

    save_all(gui);
};




    // if(typeof(Storage) !== "undefined") {
    //     // Code for localStorage/sessionStorage.
    //     console.log( Storage );
    // } 

//     {

// var gui = new dat.GUI({load:
    //       "preset": "Default",
//       "closed": false,
//       "remembered": {
//         "Default": {
//           "0": {"x": 8}
//         }
//       },
//       "folders": {}
//     }
//     });