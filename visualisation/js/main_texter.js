
var canvas = document.getElementById('interlignes');
var context = canvas.getContext('2d');

var native_width = 512, native_height = 424;
var width = 1920, height = 1080;
var height_ratio = (height / native_height);
var width_ratio = height_ratio;
var dx = (width - native_width*height_ratio) / 2



// var configObject = {
// 	autoSave: false,
// 	autoLoad: false,
// 	labels: true,
// 	layers: ["interlignes"],
// 	// onchange: _.debounce(myChangeHandler, 500),
// 	};
// var mapper = Maptastic(configObject);
var mapper = Maptastic("interlignes");


console.log(mapper.getLayout());

var interlude1 = $("#interlude1")[0];
var interlude2 = $("#interlude2")[0];

// var bufferCanvas = document.getElementById('buffer');
// var buffer = bufferCanvas.getContext('2d');

var texters = [];
var nb_texters = 1;
var lastIndex = 0;

var texters = {}

// for (i = 0; i < nb_texters; i++) {
// 	var t = new Texter(i);
// 	t.initialize();
// 	texters[i] = t;
// }


// for (i = 0; i < nb_texters; i++) {
// 	var t = new Texter(i);
// 	t.initialize();
// 	texters.push(t);
// }


// https://github.com/joewalnes/reconnecting-websocket
var tracker = new ReconnectingWebSocket("ws://127.0.0.1:8888/tracker");
// WebSocket

tracker.onopen = function (e) {
	console.log("WebSocketClient connected:", e);
}


tracker.onmessage = function (event) {
	// activer et desactiver les texters en fonction du tracking en cours 
	if (typeof event.data === 'string' || event.data instanceof String) {
		var data = $.parseJSON(event.data);

		if ("walkers" in data) {
			$.each(data.walkers, function (index, value) {
				// var i = parseInt(index) % nb_texters;
				var i = parseInt(index);
				var point = [width_ratio * value[0] + dx, height_ratio * value[1]];
				if(!(i in texters)){
					var t = new Texter(i);
					t.initialize(point);
					texters[i] = t;
					console.log("create new texter", i);					
				}
				else
					texters[i].tracked_point = point;
			});
		} else if ("control" in data) {
			set_data(data.control);
			if ("interlude1" in data.control) {
				interlude1.play();
				draw_video1();
			} else if ("interlude2" in data.control) {
				interlude2.play();
				draw_video2();
			}
		} else if ("mapping" in data) {
			console.log(data.mapping);
			// mapper = Maptastic(configObject);
			mapper.setLayout([data.mapping]);

		}
	}
};


// function write_transparent_video() {
// 	buffer.drawImage(video, 0, 0, width, height);
// 	// this can be done without alphaData, except in Firefox which doesn't like it when image is bigger than the canvas
// 	var image = buffer.getImageData(0, 0, width, height),
// 		imageData = image.data,
// 		alphaData = buffer.getImageData(0, height, width, height).data;
// 	for (var i = 3, len = imageData.length; i < len; i = i + 4) {
// 		imageData[i] = alphaData[i - 1];
// 	}
// 	context.putImageData(image, 0, 0, 0, 0, width, height);
// }


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
	// frame %= 20;
	frame %= params["clearPeriod"];
}

function init() {
	clear();
	raf = window.requestAnimationFrame(init);
}

// video.addEventListener("play", draw_video, false);
function draw_video1() {
	if (interlude1.paused || interlude1.ended) {
		return;
	}
	// processFrame();
	context.drawImage(interlude1, 0, 0, width, height);
	requestAnimationFrame(draw_video1);
}

function draw_video2() {
	if (interlude2.paused || interlude2.ended) {
		return;
	}
	// processFrame();
	context.drawImage(interlude2, 0, 0, width, height);
	requestAnimationFrame(draw_video2);
}



init();


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

