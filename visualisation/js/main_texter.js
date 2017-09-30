var video = $("#interlude")[0];
var canvas = document.getElementById('canvas');
var context = canvas.getContext('2d');

// var bufferCanvas = document.getElementById('buffer');
// var buffer = bufferCanvas.getContext('2d');





var texters = []
var nb_texters = 30;
var lastIndex = 0;

for (i = 0; i < nb_texters; i++) {
	var t = new Texter(i);
	t.initialize();
	texters.push(t);
}


// https://github.com/joewalnes/reconnecting-websocket
var tracker = new ReconnectingWebSocket("ws://127.0.0.1:8888/tracker");
// WebSocket

tracker.onopen = function(e){
	console.log("WebSocketClient connected:",e);
}

var width = 1920, height = 1080;
var height_ratio = (height / 424.);
var width_ratio = height_ratio;
var dx = (width - height) / 2.;
// var width_ratio = (width / 512.);



tracker.onmessage = function (event) {
	// activer et desactiver les texters en fonction du tracking en cours 
	if (typeof event.data === 'string' || event.data instanceof String) {
		var data = $.parseJSON(event.data);

		if("walkers" in data){
			$.each(data.walkers, function (index, value) {
				var i = parseInt(index) % nb_texters;
				texters[i].tracked_point = [width_ratio * value[0] + dx, height_ratio * value[1]];
			});
		} else if ("control" in data) {
			set_data(data.control);
		}
	}
};


function write_transparent_video() {
	buffer.drawImage(video, 0, 0, width, height);
	// this can be done without alphaData, except in Firefox which doesn't like it when image is bigger than the canvas
	var image = buffer.getImageData(0, 0, width, height),
		imageData = image.data,
		alphaData = buffer.getImageData(0, height, width, height).data;
	for (var i = 3, len = imageData.length; i < len; i = i + 4) {
		imageData[i] = alphaData[i - 1];
	}
	context.putImageData(image, 0, 0, 0, 0, width, height);
}


var frame = 0;
function clear() {
	if (frame == 0) {
		context.save();
		context.fillStyle = 'rgba(0,0,0,0.1)';
		context.fillRect(0, 0, canvas.width, canvas.height);
		context.fillStyle = 'rgba(255,255,255,1)';
		context.restore();
	}
	frame++;
	frame %= 20;
}

function init() {
	clear();
	raf = window.requestAnimationFrame(init);
}

// video.addEventListener("play", draw_video, false);
function draw_video() {
	if (video.paused || video.ended) {
		return;
	}
	// processFrame();
	context.drawImage(video, 0, 0, width, height);
	requestAnimationFrame(draw_video);
}

init();

Maptastic("canvas");

// draw_video();

// var gui = new dat.GUI();
// gui.add(texters[0], 'text').name('Text').onChange(function () { texters[0].onTextChange() });
// gui.add(texters[0], 'minFontSize', 3, 100).name('Minimum Size');
// gui.add(texters[0], 'maxFontSize', 3, 400).name('Maximum Size');
// gui.add(texters[0], 'angleDistortion', 0, 2).step(0.1).name('Random Angle');
// // gui.addColosr(texter, 'textColor').name( 'Text Color' ).onChange( function(value) { texter.applyNewColor( value ) } );
// // gui.addColosr(texter, 'bgColor').name( 'Background Color' ).onChange( function(value) { texter.setBackground( value ) } );
// gui.add(texters[0], 'clear').name('Clear');
// gui.add(texters[0], 'save').name('Save');

