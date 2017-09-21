
var tracker = new WebSocket("ws://127.0.0.1:8888/tracker");
// var corpus = new WebSocket("ws://127.0.0.1:8888/corpus");


var texters = []
var nb_texters = 30;
var lastIndex = 0;


for (i = 0; i < nb_texters; i++) {
	var t = new Texter(i);
	t.initialize();
	texters.push(t);
}


// corpus.onmessage = function (event) {
// 	// il suffit maintenant que texter notifie qu'il arrive en textIndex == newText.length;
// 	// on fera alors une requete ajax au serveur pour avoir un nouveau texte
// 	console.log(event.data);
// 	texters[lastIndex].text = event.data;
// 	texters[lastIndex].textIndex = 0;
// 	lastIndex++;
// 	lastIndex %= nb_texters;
// };

canvas = document.getElementById('canvas');
context = canvas.getContext('2d');
Maptastic("canvas");


tracker.onmessage = function (event) {
	if (typeof event.data === 'string' || event.data instanceof String) {
		// console.log(event.data)
		var points = $.parseJSON(event.data);
		$.each(points, function (index, value) {
			var i = parseInt(index);
			texters[i].tracked_point = [(1920. / 512.) * value[0], (1080 / 424.) * value[1]];
		});
	}
	// for (i = 0; i < nb_texters; i++) {
	// 	texters[i].tracked_point = [points[i][0], points[i][1]];
	// }
	// context.save();
	// context.fillStyle = 'rgba(0,255,0,0.1)';
	// context.fillRect(texters[i].tracked_point[0], texters[i].tracked_point[0], 10, 10);
	// context.restore();

};

var frame = 0;

function clear() {
	if (frame == 0) {
		context.fillStyle = 'rgba(0,0,0,0.1)';
		context.fillRect(0, 0, canvas.width, canvas.height);
		context.fillStyle = 'rgba(255,255,255,1)';
	}
	frame++;
	frame %= 20;
}


function init() {
	clear();
	raf = window.requestAnimationFrame(init);
}


var gui = new dat.GUI();
gui.add(texters[0], 'text').name('Text').onChange(function () { texters[0].onTextChange() });
gui.add(texters[0], 'minFontSize', 3, 100).name('Minimum Size');
gui.add(texters[0], 'maxFontSize', 3, 400).name('Maximum Size');
gui.add(texters[0], 'angleDistortion', 0, 2).step(0.1).name('Random Angle');
// gui.addColosr(texter, 'textColor').name( 'Text Color' ).onChange( function(value) { texter.applyNewColor( value ) } );
// gui.addColosr(texter, 'bgColor').name( 'Background Color' ).onChange( function(value) { texter.setBackground( value ) } );
gui.add(texters[0], 'clear').name('Clear');
gui.add(texters[0], 'save').name('Save');
init();

