import numpy as np
import cv2
import sys
from datetime import datetime
import traceback

import asyncio
from signal import signal, SIGINT
import json as js

from Kinect import Kinect, DepthVideo
from sort import Sort

from sanic import Sanic, response
from sanic_cors import CORS, cross_origin
from sanic.response import text, json, stream
from sanic.config import Config
from sanic.exceptions import RequestTimeout

Config.REQUEST_TIMEOUT = 100000
Config.KEEP_ALIVE = True


# MAX_DIST = 18750. / 255.
with open("params.json", "r") as f:
    VARS = js.load(f)
    VARS["learnBG"] = 0

font = cv2.FONT_HERSHEY_SIMPLEX
video_out = None
displayed_frame = None
tracked_points = {}

try:
    kinect = Kinect()
except Exception as e:
    # video_path = "/home/thomas/Vidéos/interlignes/2017-09-25 19:37:59.avi"
    video_path = "/home/thomas/Vidéos/interlignes/2017-09-30 21:36:10.avi"
    kinect = DepthVideo(video_path)
    VARS["depth_ir"] = 1

sort_tracker = Sort(max_age=5, min_hits=10)


def video_export(depth):
    global video_out

    try:
        if VARS['save'] == 1 and VARS['last_save'] == 0:
            print("saving video")
            now = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            fps = 25
            w, h = 512, 424
            codec = cv2.VideoWriter_fourcc(*'MJPG')
            filename = f"/home/thomas/Vidéos/interlignes/{now}.avi"
            video_out = cv2.VideoWriter(filename, codec, fps, (w, h))
            VARS['last_save'] = 1

        if VARS['save'] == 1 and VARS['last_save'] == 1:
            color = cv2.cvtColor(depth, cv2.COLOR_GRAY2BGR)
            video_out.write(color)
        elif video_out != None and VARS['save'] == 0 and VARS['last_save'] == 1:
            VARS['last_save'] = 0
            video_out.release()
            video_out = None

    except Exception as e:
        print(e)
        print(traceback.format_exc())


def blob_detection(frame):
    global tracked_points

    # http://opencv-python-tutroals.readthedocs.io/en/latest/py_tutorials/py_imgproc/py_contours/py_contour_features/py_contour_features.html
    # https://stackoverflow.com/questions/32414559/opencv-contour-minimum-dimension-location-in-python

    out = frame.copy()
    out = cv2.cvtColor(out, cv2.COLOR_GRAY2BGR)

    # out2 = np.zeros((512, 424,3), np.uint8)
    # cv2.add(out, out2)

    im2, contours, hier = cv2.findContours(
        frame, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)
    # cv2.RETR_CCOMP,cv2.CHAIN_APPROX_SIMPLE

    rects = []
    detections = []
    for i, cnt in enumerate(contours):
        # compute the bounding box for the contour
        (x, y, w, h) = cv2.boundingRect(cnt)
        # reject contours outside size range
        if w > VARS["max_blob_size"] or w < VARS["min_blob_size"] or h > VARS["max_blob_size"] or h < VARS["min_blob_size"]:
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
        # if w_id in tracked_points:
        # vérifier les distances entre les précédents et les nouveaux
        # pour n'envoyer que les points qui ont bougé
        # x0 = tracked_points[w_id][0]
        # y0 = tracked_points[w_id][1]
        # d =  np.sqrt((x-x0)**2 + (y-y0)**2)
        # if d < VARS['min_norm']:
        #     continue

        # x += (x - x0) * VARS['smooth'] / 10
        # y += (y - y0) * VARS['smooth'] / 10
        # new_tracked_points[w_id] = {"x":x, "y":y}
        # new_tracked_points.append({"tracker":w_id, "x":x, "y":y})

        # TODO : vérifier si 'il y a des marcheurs nouveaux ou disparus

    except Exception as e:
        print(e)
        print(traceback.format_exc())
    return out


def clean_frame(frame):
    if VARS["min_depth"] > 0:
        ret, frame = cv2.threshold(
            frame, VARS["min_depth"], 255, cv2.THRESH_TOZERO)

    if VARS["max_depth"] < 255:
        ret, frame = cv2.threshold(
            frame, VARS["max_depth"], 255, cv2.THRESH_TOZERO_INV)

    ret, frame = cv2.threshold(frame, VARS["theta"], 255, 0)
    return frame


def improve_shapes(img, bg_substractor, morph_type):
        # acquisition et sauvegarde d'un masque
        # http://docs.opencv.org/3.0-beta/doc/py_tutorials/py_imgproc/py_morphological_ops/py_morphological_ops.html
    mask = bg_substractor.apply(img, learningRate=VARS["learnBG"])
    kernel = np.ones((VARS["erode_kernel_size"],
                      VARS["erode_kernel_size"]), np.uint8)
    mask_dilate = cv2.morphologyEx(
        mask, morph_type, kernel, VARS["erode_iterations"])
    img_mask_dilate = cv2.bitwise_and(img, mask_dilate)
    return img_mask_dilate


async def kinect_loop():
    global displayed_frame
    bg_mask_path = "/home/thomas/dev/Interlignes/interlignes/"
    bg_depth_mask_path = bg_mask_path + "depth_bg.jpg"
    bg_ir_mask_path = bg_mask_path + "ir_bg.jpg"

    bg_depth_mask = cv2.imread(bg_depth_mask_path, cv2.IMREAD_GRAYSCALE)
    bg_depth_substractor = cv2.createBackgroundSubtractorMOG2(history=1)
    depth_mask = bg_depth_substractor.apply(bg_depth_mask, learningRate=1)

    bg_ir_mask = cv2.imread(bg_ir_mask_path, cv2.IMREAD_GRAYSCALE)
    bg_ir_substractor = cv2.createBackgroundSubtractorMOG2(history=1)
    ir_mask = bg_ir_substractor.apply(bg_ir_mask, learningRate=1)

    # initialisation avec 100x l'image sauvegardée précédement

    while True:
        depth, ir = kinect.get_frame(get_depth=True, get_ir=True)
        if VARS["depth_ir"] == 0:
            video_export(depth)
            shapes = improve_shapes(
                depth, bg_depth_substractor, cv2.MORPH_OPEN)
        elif VARS["depth_ir"] == 1:
            video_export(ir)
            if VARS["blur"] > 0:
                ir = cv2.blur(ir, (VARS["blur"], VARS["blur"]))
            shapes = improve_shapes(ir, bg_ir_substractor, cv2.MORPH_CLOSE)
        elif VARS["depth_ir"] == 2:
            if VARS["blur"] > 0:
                ir = cv2.blur(ir, (VARS["blur"], VARS["blur"]))
            shapes_ir = improve_shapes(ir, bg_ir_substractor, cv2.MORPH_CLOSE)
            shapes_depth = improve_shapes(
                depth, bg_depth_substractor, cv2.MORPH_OPEN)
            shapes = cv2.bitwise_or(shapes_ir, shapes_depth)

        cleaned = clean_frame(shapes)
        blobs = blob_detection(cleaned)

        if VARS["display_mode"] == 0:
            displayed_frame = blobs
        elif VARS["display_mode"] == 1:
            displayed_frame = depth
        elif VARS["display_mode"] == 2:
            displayed_frame = ir

        # displayed_frame = np.hstack((depth_flip, blobs))

        if VARS["learnBG"] == 1:
            VARS["learnBG"] = 0
            cv2.imwrite(bg_depth_mask_path, depth)
            cv2.imwrite(bg_ir_mask_path, ir)

        await asyncio.sleep(0)


async def frame_streamer(response):
    while True:
        ret, jpeg = cv2.imencode('.jpg', displayed_frame)
        f = jpeg.tobytes()
        response.write(
            b'--frame\r\nContent-Type: image/jpeg\r\n\r\n' + bytearray(f) + b'\r\n')
        await asyncio.sleep(0.01)


def create_corpus(path):
    lines = []
    # with open("/home/thomas/dev/Interlignes/tentative.txt", "r") as f:
    # MERCI
    with open(path, "r") as f:

        for l in f:
            l = l.strip()
            if len(l) > 0:
                print(l)
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
    with open("last_params.json", "w") as f:
        js.dump(VARS, f, indent=4)
    # lien symbolique
    return json({"received": True})



# TODO : générer le texte XML directement dans l'appli Web ?
current_paragraph = 0
current_main_paragraph = 0
tentative = create_corpus("/home/thomas/dev/Interlignes/tentative.txt")
merci = create_corpus("/home/thomas/dev/Interlignes/MERCI2.txt")
ponctuation = create_corpus("/home/thomas/dev/Interlignes/ponctuation.txt")
corpus = tentative
# documents = [ponctuation, tentative, ]



# entre chaque chapitre, on devient de la ponctuation
# à la fin du texte, on devient un remerciement

@app.route("/paragraphe/<walker_id>", methods=['POST', 'OPTIONS'])
def paragraphe(request, walker_id):
    global current_paragraph, current_main_paragraph, corpus
    if VARS["init_texte"] == 1:
        VARS["init_texte"] = 0
        current_paragraph = 0

    # if corpus[current_paragraph] in ["I", "II", "III"]:
    #     corpus = ponctuation
    #     current_main_paragraph = current_paragraph
    #     current_paragraph = 0

    texte = corpus[current_paragraph] + VARS['extra_spaces'] * " "
    current_paragraph += 1

    current_paragraph %= len(corpus)
    print("/paragraphe", current_paragraph)
    return json({"received": True, "walker_id": walker_id, "texte": texte, "paragraphe": current_paragraph})


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
    server = app.create_server(host="0.0.0.0", port=8888, debug=True)
    loop = asyncio.get_event_loop()
    task = asyncio.ensure_future(server)
    kinect_task = asyncio.ensure_future(kinect_loop())

    try:
        loop.run_forever()
    except:
        loop.stop()
        kinect.close()
        sys.exit(0)
