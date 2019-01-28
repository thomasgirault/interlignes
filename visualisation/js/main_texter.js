
var mapper = Maptastic("interlignes");
var canvas = document.getElementById('interlignes');
var context = canvas.getContext('2d');
var video = $("#interlude2")[0];
var video_play = false;

var corpus = new Corpus()

canvas.width = 1920, canvas.height = 1200;

var native_width = 640, native_height = 480;
var width = 1920, height = 1200;

var height_ratio = (height / native_height);
var width_ratio = height_ratio;
// var dx = (width - native_width * height_ratio) / 2


var texters = {}

// https://github.com/joewalnes/reconnecting-websocket
// WebSocket
// var tracker = new ReconnectingWebSocket("ws://127.0.0.1:8888/tracker");

var loc = window.location, new_uri;
var new_uri = "ws://" + loc.host;

// var new_uri = "ws://127.0.0.1:8888";
var tracker = new ReconnectingWebSocket(new_uri + "/tracker");



tracker.onopen = function (e) {
	console.log("WebSocketClient connected:", e);
}


tracker.onmessage = function (event) {
	// activer et desactiver les texters en fonction du tracking en cours 
	if (typeof event.data === 'string' || event.data instanceof String) {
		var data = $.parseJSON(event.data);

		if (!video_play && "walkers" in data) {
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
			console.log(data.control);
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
var animation_id;

function play_video() {
	params["interlude_play"] = 0;
	var video_name = '#interlude' + String(params["interlude"]);
	video = $(video_name)[0];
	console.log("interlude_play", video);
	params["textColor"] = "#000000";
	context.clearRect(0, 0, canvas.width, canvas.height);
	// cancelAnimationFrame(animation_id);
	// video.pause();
	video_play = true;
	// context.style.display = "none";
	video.play();

	var playPromise = video.play();

	if (playPromise !== undefined) {
		playPromise.then(_ => {
			video.style.display = "inline";

			// Automatic playback started!
			// Show playing UI.
			// We can now safely pause video...
			// video.pause();
			// video_play = false;
			// params["textColor"] = "#FFFFFF";
			// video.style.display = "none";
		})
			.catch(error => {

			});
	}
	params["interlude"] += 1;
	params["interlude"] %= params["max_interludes"];
	params["interlude_play"] = 0;
}

function draw() {
	if (params["interlude_play"]) {
		play_video();
	}
	if (video_play) {
		if (video.paused || video.ended) {
			video.pause();
			video_play = false;
			params["textColor"] = "#FFFFFF";
			// context.style.display = "inline";
			video.style.display = "none";
			// animation_id = requestAnimationFrame(draw);
		}
		// context.clearRect(0, 0, canvas.width, canvas.height);
		// // context.drawImage(video, 0, 0, width * 0.8, height * 0.8);
		// context.drawImage(video, 0, 0, width, height);
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
	animation_id = requestAnimationFrame(draw);
}

requestAnimationFrame(draw);




