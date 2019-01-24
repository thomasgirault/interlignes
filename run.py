import numpy as np
import cv2
import sys
from datetime import datetime

import asyncio
from signal import signal, SIGINT
import json as js

from video import DepthVideo, VideoRecorder, Webcam, VideoCaptureTreading
from Tracker import *

from sanic import Sanic, response
from sanic_cors import CORS, cross_origin
from sanic.response import text, json, stream
from sanic.config import Config
from sanic.exceptions import RequestTimeout

from conf import VARS


Config.REQUEST_TIMEOUT = 100000
Config.KEEP_ALIVE = True

video_out = None
jpeg_frame = None
tracked_points = {}

VARS["depth_ir"] = 1

# video_path = "/home/thomas/Vidéos/interlignes/2017-09-30\ 21:36:10.avi"
# video_path = "/home/thomas/Vidéos/interlignes/2017-09-30 21:20:04.avi"
video_path = "/home/thomas/Vidéos/interlignes/2017-09-25 19:37:59.avi"
# ip = '192.168.0.25'
ip = '169.254.72.191'
ip = '10.3.141.1'
video_path = f"http://{ip}:8080/stream/video.mjpeg"
# video_path = "/home/thomas/Vidéos/interlignes/2019-01-24_10:55:49.avi"
# cam = DepthVideo(video_path)
cam = VideoCaptureTreading(video_path).start()

fp = FrameProcessor()

# bgs_depth = BGSubstractor('depth_mask')
# bgs_ir = BGSubstractor('depth_ir')
# bgs_depth = BGSWrapper()


# bgs_depth = BGStrategy('depth_mask')
# bgs_ir = BGSubstractor('depth_ir')


async def cam_loop():
    global jpeg_frame, tracked_points
    vr = VideoRecorder()
    # initialisation avec 100x l'image sauvegardée précédement
    while True:
        ir = cam.get_frame()

        if VARS['save'] and not VARS['last_save']:
            vr.start_recording()
        elif not VARS['save'] and VARS['last_save']:
            vr.stop_recording()
        if vr.recording:
            vr.record(ir)

        fp.update(ir)
        if VARS["learnBG"] == 1 or not fp.bgs.init:
            VARS["learnBG"] = 0
            fp.save_background()

        tracked_points = fp.process()

        await asyncio.sleep(0.05)


async def frame_streamer(response):
    while True:
        jpeg_frame = await fp.get_jpeg_bytes(VARS["display_mode"])
        await response.write(jpeg_frame)
        await asyncio.sleep(0.05)  # 0.0 1/FPS


app = Sanic(__name__)
CORS(app)


@app.route('/video_feed', stream=True)
async def video_feed(request):
    """Video streaming route. Put this in the src attribute of an img tag."""
    return stream(frame_streamer, content_type='multipart/x-mixed-replace; boundary=frame')


@app.route("/param/<name>/<value>", methods=['POST', 'OPTIONS'])
def post_params(request, name, value):
    VARS[name] = int(value)
    return json({"received": True, "name": name, "value": value})


new_params = {}


@app.route("/web_param/<name>/<value>", methods=['POST', 'OPTIONS'])
def post_webparams(request, name, value):
    new_params[name] = value
    return json({"received": True, "name": name, "value": value})


@app.route("/save_params", methods=['GET'])
def save_params(request):
    now = datetime.now().strftime('%Y-%m-%d_%H:%M:%S')
    with open(f"params/params_{now}.json", "w") as f:
        js.dump(VARS, f, indent=4)
    with open("params.json", "w") as f:
        js.dump(VARS, f, indent=4)

    # lien symbolique
    return json({"received": True})


@app.route('corpus/<name>', methods=['GET'])
def send_corpus(request, name):
    path = f"/home/thomas/dev/Interlignes/{name}.txt"
    lines = []
    with open(path, "r") as f:
        for l in f:
            l = l.strip()
            if len(l) > 0:
                lines.append(l)
    return json({"corpus": name, "data": lines})

# exponential moving avg : http://damienclarke.me/code/posts/writing-a-better-noise-reducing-analogread


@app.websocket('/tracker')
async def tracker(request, ws):
    global new_params

    old_mapping = {}
    # global mapping
    while True:
        if tracked_points != {}:
            await ws.send(js.dumps({"walkers": tracked_points}))

        if new_params != {}:
            await ws.send(js.dumps({"control": new_params}))
            new_params = {}

        await asyncio.sleep(0.005)


app.static('/', './visualisation')
app.static('/params.json', './params.json')
app.static('/text_params.json', './text_params.json')


if __name__ == '__main__':
    server = app.create_server(host="0.0.0.0", port=8888)  # , debug=True)
    loop = asyncio.get_event_loop()
    task = asyncio.ensure_future(server)
    cam_task = asyncio.ensure_future(cam_loop())

    try:
        loop.run_forever()
    except:
        loop.stop()
        cam.stop()
        # cam.close()
        sys.exit(0)


# TODO : générer le texte XML directement dans l'appli Web ?
# current_paragraph = 0
# current_ponctuation_paragraph = 0
# tentative = create_corpus("/home/thomas/dev/Interlignes/tentative.txt")
# merci = create_corpus("/home/thomas/dev/Interlignes/MERCI2.txt")
# ponctuation = create_corpus("/home/thomas/dev/Interlignes/ponctuation.txt")
# corpus = tentative + ponctuation + merci  # + ponctuation

# # Réimplémenter les fonctions liées au corpus dans le JAVASCRIPT
# @app.route("/paragraphe/<walker_id>", methods=['POST', 'OPTIONS'])
# def paragraphe(request, walker_id):
#     global current_paragraph, current_ponctuation_paragraph, new_params, VARS

#     if VARS["init_texte"] == 1:
#         VARS["init_texte"] = 0
#         current_paragraph = 0
#         current_ponctuation_paragraph = 0

#     # if VARS["anniversaire"] > 0:
#     #     texte = "Joyeux anniversaire Laurence !        Joyeux anniversaire Laurence !        Joyeux anniversaire Laurence !"
#     #     VARS["anniversaire"] -= 1

#     elif VARS["ponctuation_proba"] > np.random.random() * 100:
#         texte = ponctuation[current_ponctuation_paragraph]
#         current_ponctuation_paragraph += 1
#         current_ponctuation_paragraph %= len(ponctuation)
#     else:
#         texte = corpus[current_paragraph] + VARS['extra_spaces'] * " "
#         current_paragraph += 1
#         if current_paragraph > len(corpus) - 1:
#             current_paragraph = 0
#             if VARS["video_ok"] in [1, True]:
#                 new_params["interlude_play"] = 1

#     print("/paragraphe", current_paragraph)
#     return json({"received": True, "walker_id": walker_id, "texte": texte, "paragraphe": current_paragraph})

    # if corpus[current_paragraph] in ["I", "II", "III"]:
    #     corpus = ponctuation
    #     current_main_paragraph = current_paragraph
    #     current_paragraph = 0
