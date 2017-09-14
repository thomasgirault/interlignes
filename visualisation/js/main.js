
// var textWidth = function (string, size) {
//   context.font = size + "px Time new roman";

//   if (context.fillText) {
//     return context.measureText(string).width;

//   } else if (context.mozDrawText) {
//     return context.mozMeasureText(string);

//   }
// };


var ws = new WebSocket("ws://127.0.0.1:8888/");

// mapping
// Wrapping angular/typescript : https://codepen.io/osublake/pen/gLGYxx
// 3D CSS Quad wrapping

// CSS transform
// https://github.com/glowbox/maptasticjs
// https://codepen.io/dudleystorey/pen/EyPbQp



// var ws_params = new WebSocket("ws://127.0.0.1:8888/params");

var ligne = new Ligne("Exigez le Roquefort Société le vrai dans son ovale vert");
// var ligne2 = new Ligne("Un camion livre de la bière en tonneaux de métal ( Kanterbraü , la bière de Maître Kanter)");
// var ligne3 = new Ligne("Sur le terre-plein un enfant fait courir son chien (genre Milou )");
// var ligne4 = new Ligne("Une jeune fille mange la moitié d'un palmier . Un homme à pipe et sacoche noire. ");


var gui = new dat.GUI();
gui.add(ligne, 'texte').name( 'Texte' ); //.onChange( function() { ligne.onTextChange() } );
gui.add(ligne, 'minFontSize', 3, 100).name( 'Minimum Size' );
gui.add(ligne, 'maxFontSize', 30, 150).name( 'Maximum Size' );
gui.add(ligne, 'maxLen', 20, 400).name( 'Maximum len' );
gui.add(ligne, 'segLength', 15, 100).name( 'Seg len' );


// gui.add(ligne, 'angleDistortion', 0, 2).step(0.1).name( 'Random Angle' );
// gui.addColor(texter, 'textColor').name( 'Text Color' ).onChange( function(value) { texter.applyNewColor( value ) } );
// gui.addColor(texter, 'bgColor').name( 'Background Color' ).onChange( function(value) { texter.setBackground( value ) } );
//gui.add(ligne, 'clear').name( 'Clear' );
//gui.add(ligne, 'save').name( 'Save' );



ws.onmessage = function (event) {
  if (typeof event.data === 'string' || event.data instanceof String) {
    doc = event.data + "  ";
    // console.log(doc);
    ligne.setTexte(doc);
    // ligne2.setTexte(doc);
    // ligne3.setTexte(doc);
    // ligne4.setTexte(doc);
    }
};



// var myFont;
// function preload() {
//   myFont = loadFont('assets/AvenirNextLTPro-Demi.otf');
// }

function setup() {
  // textFont(myFont);
  textFont("Times new roman");
  //background(0);
  var canvas = createCanvas(1920, 1200);
  canvas.parent('main');
  //Maptastic("defaultCanvas0");

  // Move the canvas so it's inside our <div id="sketch-holder">.
   
  // var sketch = function(p) {
  //   p.setup = function(){
  //     p.createCanvas(1920, 1200);
  //     p.background(0);
  //   }
  // };
  // new p5(sketch, 'canvas');
  
  // fill(255);

}

function draw() {          
  background(0);
  ligne.draw(mouseX, mouseY);
  // ligne2.draw(1920 - mouseX, mouseY);
  // ligne3.draw(1920 - mouseX, 1080 - mouseY);
  // ligne4.draw(mouseX, 1080 - mouseY);

}
