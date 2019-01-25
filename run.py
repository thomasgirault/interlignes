import numpy as np
import cv2
import bgs
import sys
from datetime import datetime
import traceback

import asyncio
from signal import signal, SIGINT
import json as js

from video import Kinect, DepthVideo, VideoRecorder, Webcam
from Tracker import *
from sort import Sort

from sanic import Sanic, response
from sanic_cors import CORS, cross_origin
from sanic.response import text, json, stream
from sanic.config import Config
from sanic.exceptions import RequestTimeout

from conf import VARS


Config.REQUEST_TIMEOUT = 100000
Config.KEEP_ALIVE = True


# MAX_DIST = 18750. / 255.
# with open("params.json", "r") as f:
#     VARS = js.load(f)
#     VARS["learnBG"] = 0

font = cv2.FONT_HERSHEY_SIMPLEX
video_out = None
displayed_frame = None
tracked_points = {}


try:
    kinect = Kinect()
except Exception as e:
    print("KINECT NOT FOUND")

    # video_path = "/home/thomas/Vidéos/interlignes/2017-09-30\ 21:36:10.avi"
    # video_path = "/home/thomas/Vidéos/interlignes/2017-09-30 21:20:04.avi"
    video_path = "/home/thomas/Vidéos/interlignes/2017-09-25 19:37:59.avi"
    kinect = DepthVideo(video_path)
    # kinect = Webcam(1)
    VARS["depth_ir"] = 1

sort_tracker = Sort(max_age=5, min_hits=10)


def blob_detection(frame, min_blob_size=VARS["min_blob_size"],  max_blob_size=VARS["max_blob_size"]):
    global tracked_points

    # http://opencv-python-tutroals.readthedocs.io/en/latest/py_tutorials/py_imgproc/py_contours/py_contour_features/py_contour_features.html
    # https://stackoverflow.com/questions/32414559/opencv-contour-minimum-dimension-location-in-python

    out = frame.copy()
    out = cv2.cvtColor(out, cv2.COLOR_GRAY2BGR)

    # out2 = np.zeros((512, 424,3), np.uint8)
    # cv2.add(out, out2)

    im2, contours, hier = cv2.findContours(
        frame, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

    # frame, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)
    # cv2.RETR_CCOMP,cv2.CHAIN_APPROX_SIMPLE

    rects = []
    detections = []
    for i, cnt in enumerate(contours):
        # compute the bounding box for the contour
        (x, y, w, h) = cv2.boundingRect(cnt)
        # reject contours outside size range
        if w > max_blob_size or w < min_blob_size or h > max_blob_size or h < min_blob_size:
            continue
        rects.append((x, y, w, h))
        detections.append((x, y, x + w, y + h, 1))
        cv2.rectangle(out, (x, y), (x + w, y + h), (255, 0, 0), 2)
    try:
        detections = sort_tracker.update(np.array(detections))

        new_tracked_points = {}

        for x1, y1, x2, y2, walker_id in detections:
            w_id = str(int(walker_id))
            x = int((x2 + x1) / 2)
            y = int((y2 + y1) / 2)
            new_tracked_points[w_id] = [x, y2]
            cv2.circle(out, (x, int(y2)), 5, (0, 0, 255), -1)
            cv2.putText(out, w_id, (x, y), font, 1,
                        (255, 255, 0), 1, cv2.LINE_AA)

        tracked_points = new_tracked_points

    except Exception as e:
        print(e)
        print(traceback.format_exc())
    return out


async def kinect_loop():
    global displayed_frame

    bgs_depth = BGSubstractor('depth_mask')
    bgs_ir = BGSubstractor('depth_ir')
    # bgs_depth = BGSWrapper()
    # bgs_ir = BGSWrapper()

    vr = VideoRecorder()
    # initialisation avec 100x l'image sauvegardée précédement

    while True:
        if VARS['save'] and not VARS['last_save']:
            vr.start_recording()
        elif not VARS['save'] and VARS['last_save']:
            vr.stop_recording()

        depth, ir = kinect.get_frame(get_depth=True, get_ir=True)
        shapes = []

        if VARS["learnBG"] == 1 or not bgs_depth.init or not bgs_ir.init:
            VARS["learnBG"] = 0
            bgs_depth.save(depth)
            bgs_ir.save(ir)

        if (VARS["depth_ir"] % 2) == 0:  # 0,2
            frame_depth = Frame(depth)
            frame_depth.threshold()
            depth_masked = bgs_depth.apply(frame_depth.frame)
            ir_cleaned = frame_depth.clean(depth_masked)
            shapes.append(depth_masked)

        if VARS["depth_ir"] > 0:  # 1,2
            frame_ir = Frame(ir)
            frame_ir.blur()
            ir_masked = bgs_ir.apply(frame_ir.frame)
            ir_cleaned = frame_ir.clean(ir_masked)
            shapes.append(ir_cleaned)

        if VARS["depth_ir"] == 2:
            shapes = cv2.bitwise_or(shapes[0], shapes[1])

        blobs = blob_detection(shapes[0])

        if VARS["display_mode"] == 0:
            displayed_frame = blobs
        elif VARS["display_mode"] == 1:
            displayed_frame = depth
            if vr.recording:
                vr.record(depth)
        elif VARS["display_mode"] == 2:
            displayed_frame = ir
            if vr.recording:
                vr.record(ir)

        # displayed_frame = np.hstack((depth_flip, blobs))

        await asyncio.sleep(0)


async def get_jpeg_bytes():
    while True:
        ret, jpeg = cv2.imencode('.jpg', displayed_frame)
        f = jpeg.tobytes()  # bytearray
        if ret:
            return b'--frame\r\nContent-Type: image/jpeg\r\n\r\n' + f + b'\r\n'


async def frame_streamer(response):
    while True:
        jpeg_frame = await get_jpeg_bytes()
        await response.write(jpeg_frame)
        await asyncio.sleep(0.05)  # 0.0 1/FPS


def create_corpus(path):
    lines = []
    with open(path, "r") as f:
        for l in f:
            l = l.strip()
            if len(l) > 0:
                lines.append(l)
    return lines


app = Sanic(__name__)
CORS(app)


@app.route('/video_feed', stream=True)
async def video_feed(request):
    """Video streaming route. Put this in the src attribute of an img tag."""
    return stream(frame_streamer, content_type='multipart/x-mixed-replace; boundary=frame')


@app.route("/param/<name>/<value>", methods=['POST', 'OPTIONS'])
def post_params(request, name, value):
    VARS[name] = int(value)
    if name == "MAX_DIST":
        kinect.max_dist = VARS[name]
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



# TODO : générer le texte XML directement dans l'appli Web ?
current_paragraph = 0
current_ponctuation_paragraph = 0
tentative = create_corpus("/home/thomas/dev/Interlignes/tentative.txt")
merci = create_corpus("/home/thomas/dev/Interlignes/MERCI2.txt")
ponctuation = create_corpus("/home/thomas/dev/Interlignes/ponctuation.txt")
corpus = tentative + ponctuation + merci  # + ponctuation


@app.route('corpus/<name>', methods=['GET'])
def send_corpus(request, name):

    data = create_corpus(f"/home/thomas/dev/Interlignes/{name}.txt")

    return json({"corpus": name, "data": data})


# Réimplémenter les fonctions liées au corpus dans le JAVASCRIPT
@app.route("/paragraphe/<walker_id>", methods=['POST', 'OPTIONS'])
def paragraphe(request, walker_id):
    global current_paragraph, current_ponctuation_paragraph, new_params, VARS

    if VARS["init_texte"] == 1:
        VARS["init_texte"] = 0
        current_paragraph = 0
        current_ponctuation_paragraph = 0

    # if VARS["anniversaire"] > 0:
    #     texte = "Joyeux anniversaire Laurence !        Joyeux anniversaire Laurence !        Joyeux anniversaire Laurence !"
    #     VARS["anniversaire"] -= 1

    elif VARS["ponctuation_proba"] > np.random.random() * 100:
        texte = ponctuation[current_ponctuation_paragraph]
        current_ponctuation_paragraph += 1
        current_ponctuation_paragraph %= len(ponctuation)
    else:
        texte = corpus[current_paragraph] + VARS['extra_spaces'] * " "
        current_paragraph += 1
        if current_paragraph > len(corpus) - 1:
            current_paragraph = 0
            if VARS["video_ok"] in [1, True]:
                new_params["interlude_play"] = 1

    print("/paragraphe", current_paragraph)
    return json({"received": True, "walker_id": walker_id, "texte": texte, "paragraphe": current_paragraph})

    # if corpus[current_paragraph] in ["I", "II", "III"]:
    #     corpus = ponctuation
    #     current_main_paragraph = current_paragraph
    #     current_paragraph = 0

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

        await asyncio.sleep(0)


app.static('/', './visualisation')
app.static('/params.json', './params.json')
app.static('/text_params.json', './text_params.json')


if __name__ == '__main__':
    server = app.create_server(host="0.0.0.0", port=8888)  # , debug=True)
    loop = asyncio.get_event_loop()
    task = asyncio.ensure_future(server)
    kinect_task = asyncio.ensure_future(kinect_loop())

    try:
        loop.run_forever()
    except:
        loop.stop()
        kinect.close()
        sys.exit(0)
