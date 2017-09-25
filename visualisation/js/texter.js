/*
 *  Texter - Drawing with Text.
 *  - Ported from demo in Generative Design book - http://www.generative-gestaltung.de
 *  - generative-gestalung.de original licence: http://www.apache.org/licenses/LICENSE-2.0
 *
 *  - Modified and maintained by Tim Holman - tholman.com - @twholman
 */

function Texter(id) {

  var _this = this;

  // Application variables
  position = { x: 0, y: window.innerHeight / 2 };
  this.id = id;
  this.textIndex = 0;
  this.textColor = "#ffffff";
  this.bgColor = "#000000";
  this.minFontSize = 30;
  this.maxFontSize = 300;
  this.angleDistortion = 0.00;
  this.tracked_point = [0, 0];
  this.last_tracked_point = [0, 0];


  this.text = "Un flic à vélo gare son vélo et entre dans le tabac ; il en ressort presque aussitôt, on ne sait pas ce qu'il a acheté (des cigarettes ? un stylo à bille , un timbre , des cachous , un paquet de mouchoirs en papier ?)";

  // Drawing Variables
  canvas = null;
  context = null;

  bgCanvas = null;
  bgContext = null;

  this.initialize = function () {

    canvas = document.getElementById('canvas');
    context = canvas.getContext('2d');
    canvas.width = window.innerWidth;
    canvas.height = window.innerHeight;


    bgCanvas = document.createElement('canvas');
    bgContext = bgCanvas.getContext('2d');
    bgCanvas.width = canvas.width;
    bgCanvas.height = canvas.height;
    _this.setBackground(_this.bgColor);
    context.fillStyle = _this.textColor;


    window.onresize = function (event) {
      canvas.width = window.innerWidth;
      canvas.height = window.innerHeight;
      bgCanvas.width = window.innerWidth;
      bgCanvas.height = window.innerHeight;
      _this.setBackground(_this.bgColor);
      _this.clear();
    }

    update();
    askNewText();
  };



  var update = function () {
    requestAnimationFrame(update);
    draw();
  }

  var draw = function () {
    if (_this.tracked_point != _this.last_tracked_point) {
      position.x = _this.last_tracked_point[0];
      position.y = _this.last_tracked_point[1];
      _this.last_tracked_point = _this.tracked_point;


      var newDistance = distance(position, { x: _this.tracked_point[0], y: _this.tracked_point[1] });

      var fontSize = _this.minFontSize + newDistance / 2;

      if (fontSize > _this.maxFontSize) {
        fontSize = _this.maxFontSize;
      }

      var letter = _this.text[_this.textIndex];
      var stepSize = textWidth(letter, fontSize);

      if (newDistance > stepSize) {
        var angle = Math.atan2(_this.tracked_point[1] - position.y, _this.tracked_point[0] - position.x);

        context.font = fontSize + "px Georgia";

        context.save();
        context.translate(position.x, position.y);
        context.rotate(angle + (Math.random() * (_this.angleDistortion * 2) - _this.angleDistortion));
        context.fillText(letter, 0, 0);
        context.restore();



        _this.textIndex++;
        if (_this.textIndex > _this.text.length - 1) {
          _this.textIndex = 0;
          askNewText()
        }

        position.x = position.x + Math.cos(angle) * stepSize;
        position.y = position.y + Math.sin(angle) * stepSize;

      }
    }
  };

  var distance = function (pt, pt2) {
    var xs = 0;
    var ys = 0;
    xs = pt2.x - pt.x;
    ys = pt2.y - pt.y;
    return Math.sqrt(xs * xs + ys * ys);
  };


  var textWidth = function (string, size) {
    context.font = size + "px Georgia";
    // "24pt 'Times New Roman'"

    if (context.fillText) {
      return context.measureText(string).width;

    } else if (context.mozDrawText) {
      return context.mozMeasureText(string);

    }
  };

  this.clear = function () {
    canvas.width = canvas.width;
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

  this.onTextChange = function () {
    _this.textIndex = 0;
  }

  this.save = function () {
    // Prepare the background canvas's color
    bgContext.rect(0, 0, bgCanvas.width, bgCanvas.height);
    bgContext.fillStyle = _this.bgColor;
    bgContext.fill();

    // Draw the front canvas onto the bg canvas
    bgContext.drawImage(canvas, 0, 0);
    // Open in a new window
    window.open(bgCanvas.toDataURL('image/png'), 'mywindow');
  }


  function askNewText() {
    console.log(_this.id, "asks new text");
    $.ajax({
      type: "POST",
      url: "http://localhost:8888/paragraphe/" + id,
      data: JSON.stringify({ 'id': _this.id}),
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