var ws = new WebSocket("ws://127.0.0.1:5678/");



var doc = "Une vieille femme met sa main en visière pour voir quel est le numéro de l'autobus qui arrive (je peux déduire de son air décu qu'elle voudrait prendre le 70)";
var segLength = 100;                                 // **change** float to var
var x = new Array(segLength);  // **change** float[] x = new float[20] to new Array(20)
var y = new Array(segLength);  // **change** float[] y = new float[20] to new Array(20)
// var letterSize = new Array(segLength);  // **change** float[] y = new float[20] to new Array(20)
var ligne = doc.substr(0, segLength);;

var j = 0;


ws.onmessage = function (event) {
  // if (event.data != undefined){
  if (typeof event.data === 'string' || event.data instanceof String) {

    doc = event.data + "  ";
    console.log(doc);

    segLength = Math.min(40, doc.length);                                 // **change** float to var
    console.log("segLength", segLength);
    //x = new Array(segLength);  // **change** float[] x = new float[20] to new Array(20)
    // y = new Array(segLength);  // **change** float[] y = new float[20] to new Array(20)
    ligne = doc.substr(0, segLength);;
    j = 0;
    // ligne = ligne.split('').reverse().join('');
    // segLength = doc.length; 
  }

  // textIndex = 0;
};

var textWidth = function (string, size) {
  context.font = size + "px Time new roman";

  if (context.fillText) {
    return context.measureText(string).width;

  } else if (context.mozDrawText) {
    return context.mozMeasureText(string);

  }
};



function setup() {                          // **change** void setup() to function setup()
  background(0);                            // background() is the same
  fill(255);

  textFont("Time new roman");

  createCanvas(1920, 1080);                   // **change** size() to createCanvas()
  // strokeWeight(30);                          // strokeWeight() is the same
  // stroke(255, 255,255);                         // stroke() is the same
  fill(255, 255, 255, 255);

  for (var i = 0; i < x.length; i++) {         // initialize the array
    x[i] = 0;
    y[i] = 0;
  }
}

function draw() {                           // **change** void draw() to function draw()
  //if(j == 0)
  background(0); //,0,0,10);                            // background() is the same
  if (j + 0.2 < segLength) {
    ligne = doc.substr(int(j), segLength);
    //ligne = doc;
    ligne = ligne.split('').reverse().join('');

    // console.log(ligne);
  }
  fill(255);
  drawSegment(0, mouseX, mouseY);           // functions calls, mouseX and mouseY are the same
  for (var n = 0; n < ligne.length - 1; n++) {         // **change** int i to var i
    drawSegment(n + 1, x[n], y[n]);          // function calls are the same
  }
  j = (j + 0.1) % segLength;
}

function drawSegment(i, xin, yin) {         // **change** void drawSegment() to function drawSegment(), remove type declarations
  var dx = xin - x[i];                      // **change** float to var
  var dy = yin - y[i];                      // **change** float to var
  var angle = atan2(dy / 5, dx / 5);
  var letter = ligne[i];
  var fontSize = Math.min(70, Math.sqrt(dx * dx + dy * dy));
  var stepSize = textWidth(letter, 170);

  fill(int(255. / Math.sqrt(0.1 * i + 1)));

  // **change** float to var, atan2() is the same
  x[i] = xin - cos(angle) * segLength;      // cos() is the same
  y[i] = yin - sin(angle) * segLength;      // sin() is the same
  // console.log(ligne[i], x[i], y[i], ts, angle);
  segmentText(x[i], y[i], fontSize, angle, letter);               // function calls are the same
}
function segmentText(x, y, ts, a, t) {                 // **change** void segment() to function segment(), remove type declarations
  push();                            		// pushMatrix() becomes push()
  translate(x, y);                          // translate() is the same
  rotate(a);                               // rotate() is the same
  try {
    textSize(ts);
    text(String(t), 0, 0);
  }
  catch (err) {

    console.log(err.message);
  }
  pop();                              		// popMatrix() becomes pop()
}


function segment(x, y, a) {                 // **change** void segment() to function segment(), remove type declarations
  push();                            		// pushMatrix() becomes push()
  translate(x, y);                          // translate() is the same
  rotate(a);                               // rotate() is the same
  line(0, 0, segLength, 0);                 // line() is the same
  pop();                              		// popMatrix() becomes pop()
}

function windowResized() {
	resizeCanvas(windowWidth, windowHeight);
}