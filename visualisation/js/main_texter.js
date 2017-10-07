
var mapper = Maptastic("interlignes");
var canvas = document.getElementById('interlignes');
var context = canvas.getContext('2d');
var video = $("#interlude2")[0];
var video_play = false;

canvas.width = 1920, canvas.height = 1200;

var native_width = 512, native_height = 424;
var width = 1920, height = 1200;

var height_ratio = (height / native_height);
var width_ratio = height_ratio;
// var dx = (width - native_width * height_ratio) / 2


var texters = {}

// https://github.com/joewalnes/reconnecting-websocket
// WebSocket
var tracker = new ReconnectingWebSocket("ws://127.0.0.1:8888/tracker");

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
				if (!(i in texters)) {
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
			if ("interlude" in data.control) {
				params["interlude"] = data.control["interlude"];				
			} else if ("interlude_play" in data.control) {
				console.log("interlude_play");
				var video_name = '#interlude' + String(params["interlude"]);
				video = $(video_name)[0];
				params["textColor"] = "#000000";
				video.pause();
				video_play = true;
				video.play();
				params["interlude"] += 1;
				params["interlude"] %= params["max_interludes"];
			}

		}
	}
};

$(window).bind('storage', function (e) {
	// console.log(e.originalEvent.key, e.originalEvent.newValue);
	var mapping = mapper.getLayout();
	var new_value = $.parseJSON(e.originalEvent.newValue);
	mapper.setLayout(new_value);
});


// https://stackoverflow.com/questions/45549418/subtract-opacity-instead-of-multiplying
var frame = 0;

function draw() {
	if (video_play) {
		if (video.paused || video.ended) {
			video.pause();
			video_play = false;
			params["textColor"] = "#FFFFFF";
		}
		context.clearRect(0, 0, canvas.width, canvas.height);
		context.drawImage(video, 0, 0, width * 0.8, height * 0.8);
	} else if (frame == 0) {
		var img = context.getImageData(0, 0, canvas.width, canvas.height);
		context.clearRect(0, 0, canvas.width, canvas.height);
		var px = img.data;
		for (var i = 0; i < px.length; i += 4) {
			px[i] -= 10;
			px[i + 1] = px[i];
			px[i + 2] = px[i];
		}
		context.putImageData(img, 0, 0);
	}
	frame++;
	frame %= params["clearPeriod"];
	requestAnimationFrame(draw);
}

draw();

// function clear_() {
	// 	if (frame == 0) {
	// 		context.save();
	// 		// context.globalCompositeOperation = "darker";

	// 		context.globalAlpha = 0.8;
	// 		context.fillStyle = 'rgba(0,0,0,0.1)';
	// 		context.fillRect(0, 0, canvas.width, canvas.height);
	// 		context.fillStyle = 'rgba(255,255,255,1)';
	// 		context.restore();
	// 	}
	// 	// frame++;
	// 	// frame %= params["clearPeriod"];
	// }


// function init() {
// 	draw();
// 	raf = window.requestAnimationFrame(init);
// }
// init();

// video.addEventListener("play", draw_video, false);
// function draw_video() {
// 	if (video.paused || video.ended) {
// 		return;
// 	}
// 	context.drawImage(video, 0, 0, width, height);
// 	requestAnimationFrame(draw_video);
// }


// function draw_video2() {
// 	if (interlude2.paused || interlude2.ended) {
// 		return;
// 	}
// 	// processFrame();
// 	context.drawImage(interlude2, 0, 0, width, height);
// 	requestAnimationFrame(draw_video2);
// }



