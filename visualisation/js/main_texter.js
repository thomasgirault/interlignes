
var mapper = Maptastic("interlignes");
var canvas = document.getElementById('interlignes');
var context = canvas.getContext('2d');
//canvas.width = screen.width, canvas.height = screen.width;
canvas.width = 1920, canvas.height = 1080;



var native_width = 512, native_height = 424;
// var width = canvas.width, height = canvas.width;
var width = 1920, height = 1080;

var height_ratio = (height / native_height);
var width_ratio = height_ratio;
var dx = (width - native_width*height_ratio) / 2


var interlude1 = $("#interlude1")[0];
var interlude2 = $("#interlude2")[0];


var texters = {}

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
				var i = parseInt(index);
				var point = [width_ratio * value[0], height_ratio * value[1]];
				if(!(i in texters)){
					var t = new Texter(i);
					t.initialize(point);
					texters[i] = t;
					console.log("create new walker", i);					
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
		} 
	}
};

$(window).bind('storage', function (e) {
	// console.log(e.originalEvent.key, e.originalEvent.newValue);
	var mapping = mapper.getLayout();
	var new_value =  $.parseJSON(e.originalEvent.newValue);
	mapper.setLayout(new_value); 
});


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
