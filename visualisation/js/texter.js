var defaultText = 'Texter ';

var params = {

    "minFontSize": 8,
    "maxFontSize": 400
};


set_data = function (dico) {
    for (i in dico) {
        params[i] = parseInt(dico[i]);
        console.log(i, dico[i]);
    }
};


function Texter(id) {

    var _this = this;

    // Application variables
    this.textIndex = 0;
    this.id = id;
    this.textColor = "#ffffff";
    this.bgColor = "#000000";
    this.curFontSize = 12;
    this.varFontSize = 0.4;

    this.minFontSize = 8;
    this.maxFontSize = 400;

    this.angle = 0;
    this.angleDelta = 0;
    this.angleDistortion = 0.01;
    this.completeWords = true;
    this.tracked_point = [0, 0];
    this.last_tracked_point = [0, 0];

    this.text = "";

    // Drawing Variables
    canvas = null;
    context = null;

    this.initialize = function () {

        canvas = document.getElementById('canvas');
        context = canvas.getContext('2d');
        canvas.width = 1920;
        canvas.height = 1080;
        _this.setBackground(_this.bgColor);
        context.fillStyle = _this.textColor;
        update();
        askNewText();
    };



    function update() {
        requestAnimationFrame(update);
        draw();
    }

    function draw() {
        if (_this.tracked_point != _this.last_tracked_point) {
            var newDistance = dist(_this.tracked_point, _this.last_tracked_point);
            var fontSize = calcFontSize(newDistance);
            var letter = _this.text[_this.textIndex];
            var stepSize = textWidth(letter, fontSize);

            if (newDistance > stepSize) {
                var angle = Math.atan2(_this.tracked_point[1] - _this.last_tracked_point[1], _this.tracked_point[0] - _this.last_tracked_point[0]);
                _this.angleDelta = _this.angle - angle;
                if (_this.angleDelta > 3.14) {
                    _this.angleDelta = _this.angle + angle;
                }
                _this.angle = angle;

                context.font = fontSize + "px Georgia";

                letter_to_context(letter);

                _this.textIndex++;
                if (_this.textIndex > _this.text.length - 1) {
                    _this.textIndex = 0;
                    askNewText();
                }

                _this.last_tracked_point[0] += Math.cos(angle) * stepSize;
                _this.last_tracked_point[1] += Math.sin(angle) * stepSize;

            }
        }
    };



    function finishWord() {
        var newDistance = dist(_this.tracked_point, _this.last_tracked_point);
        var fontSize = calcFontSize(newDistance);
        var letter = _this.text[_this.textIndex];
        context.font = fontSize + "px Georgia";
        while (letter != ' ') {

            console.log("Finish word");
            letter_to_context(letter);

            _this.textIndex++;
            if (_this.textIndex > _this.text.length - 1) {
                _this.textIndex = 0;
                // askNewText();
                return;
            }
            else {
                var stepSize = textWidth(letter, fontSize);
                _this.last_tracked_point[0] += Math.cos(angle) * stepSize;
                _this.last_tracked_point[1] += Math.sin(angle) * stepSize;
                letter = _this.text[_this.textIndex];
                _this.angle -= _this.angleDelta;
                _this.angleDelta -= _this.angleDelta / 6;
            }
        }
    }

    function dist(pt, pt2) {
        var xs = pt2[0] - pt[0];
        var ys = pt2[1] - pt[1];
        return Math.sqrt(xs * xs + ys * ys);
    };


    function calcFontSize(d) {
        var fontSize = params["minFontSize"] + d / 2;
        if (fontSize > params["maxFontSize"])
            fontSize = params["maxFontSize"];
        return fontSize;
    }
    // var fontSize = _this.minFontSize + d / 2;
    // if (fontSize > _this.maxFontSize)
    //     fontSize = _this.maxFontSize;

    // var fontSize = _this.curFontSize + d * _this.varFontSize;

    function letter_to_context(letter) {
        context.save();
        context.translate(_this.last_tracked_point[0], _this.last_tracked_point[1]);
        context.rotate(_this.angle + (Math.random() * (_this.angleDistortion * 2) - _this.angleDistortion));
        context.fillText(letter, 0, 0);
        context.restore();
    }




    function textWidth(string, size) {
        context.font = size + "px Georgia";

        if (context.fillText) {
            return context.measureText(string).width;

        } else if (context.mozDrawText) {
            return context.mozMeasureText(string);

        }
    };

    this.clear = function () {
        canvas.width = canvas.width;
        textIndex = 0;
        context.fillStyle = _this.textColor;
    }

    this.applyNewColor = function (value) {
        _this.textColor = value;
        context.fillStyle = _this.textColor;
    }

    this.setBackground = function (value) {
        _this.bgColor = value;
        canvas.style.backgroundColor = value;

    };

    this.setText = function (text) {
        if (text == '') {
            text = defaultText;
        }
        this.text = text;
        textIndex = 0;
    }



    function askNewText() {
        console.log(_this.id, "asks new text");
        $.ajax({
            type: "POST",
            url: "http://localhost:8888/paragraphe/" + id,
            data: JSON.stringify({ 'id': _this.id }),
            contentType: "application/json; charset=utf-8",
            dataType: "json",
            success: function (data) {
                console.log(data);
                _this.text = data.texte;
            },
            failure: function (errMsg) { alert(errMsg); }
        });
    }

};




// this.save = function () {

//     // Prepare the background canvas's color
//     bgContext.rect(0, 0, bgCanvas.width, bgCanvas.height);
//     bgContext.fillStyle = _this.bgColor;
//     bgContext.fill();

//     // Draw the front canvas onto the bg canvas
//     bgContext.drawImage(canvas, 0, 0);

//     // Open in a new window
//     window.open(bgCanvas.toDataURL('image/png'), 'mywindow');

// }


    // var mouseUp = function (event) {
    //     if (mouse.down == false) {
    //         return;
    //     }
    //     mouse.down = false;
    //     if (_this.completeWords == false) {
    //         return;
    //     }

    //     // Finish word following the same angle
    //     var newDistance = distance(position, mouse);
    //     var fontSize = calcFontSize(newDistance);
    //     var letter = _this.text[textIndex];
    //     context.font = fontSize + "px Gabriela";
    //     while (letter != ' ') {

    //         letter_to_context(letter);

    //         textIndex++;
    //         if (textIndex > _this.text.length - 1) {
    //             textIndex = 0;
    //             return;
    //         }
    //         else {
    //             var stepSize = textWidth(letter, fontSize);
    //             position.x = position.x + Math.cos(_this.angle) * stepSize;
    //             position.y = position.y + Math.sin(_this.angle) * stepSize;
    //             letter = _this.text[textIndex];
    //             _this.angle -= _this.angleDelta;
    //             _this.angleDelta -= _this.angleDelta / 6;
    //         }
    //     }
    // }



            // mouse = { x: 0, y: 0, down: false };

        // bgCanvas = null;
        // bgContext = null;

        // bgCanvas = document.createElement('canvas');
        // bgContext = bgCanvas.getContext('2d');
        // bgCanvas.width = canvas.width;
        // bgCanvas.height = canvas.height;
    //position = {x: 0, y: window.innerHeight/2};
