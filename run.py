import numpy as np
import cv2
import sys
from datetime import datetime

import traceback

import asyncio
from signal import signal, SIGINT
import json as js

from pylibfreenect2 import Freenect2, SyncMultiFrameListener
from pylibfreenect2 import FrameType, Registration, Frame
from pylibfreenect2 import createConsoleLogger, setGlobalLogger
from pylibfreenect2 import LoggerLevel
from pylibfreenect2 import OpenCLKdePacketPipeline


from sanic import Sanic, response
from sanic_cors import CORS, cross_origin
from sanic.response import text, json, stream
from sanic.config import Config
from sanic.exceptions import RequestTimeout

Config.REQUEST_TIMEOUT = 100000
Config.KEEP_ALIVE = False


from MultiObjectTracker import MultiObjectTracker
from sort import Sort


mot = MultiObjectTracker()
sort_tracker = Sort(max_age=5, min_hits=10)


MAX_DIST = 18750. / 255.
VARS = {"min_depth": 0,
        "max_depth": 255,
        "theta": 0,
        "save": 0,
        "last_save": 0,
        "max_age":5, 
        "min_hits":10,
        "MAX_DIST": MAX_DIST,
        "min_blob_size": 30,
        "max_blob_size": 500,
        "learnBG": 0,
        "min_norm": 1,
        "extra_spaces": 5}

# TODO : Doit être stocké comme un JSON à l'exterieur de l'application en lien avec l'appli JS


font = cv2.FONT_HERSHEY_SIMPLEX

video_out = None 
#cv2.VideoWriter(filename, codec, fps, (w, h))

pipeline = OpenCLKdePacketPipeline(0)
displayed_frame = None

print("Packet pipeline:", type(pipeline).__name__)


# Create and set logger
logger = createConsoleLogger(LoggerLevel.Debug)
setGlobalLogger(logger)

fn = Freenect2()
num_devices = fn.enumerateDevices()
if num_devices == 0:
    print("No device connected!")
    sys.exit(1)

serial = fn.getDeviceSerialNumber(0)
device = fn.openDevice(serial, pipeline=pipeline)

# | FrameType.Color | FrameType.Ir)
listener = SyncMultiFrameListener(FrameType.Depth)

# Register listeners
# device.setColorFrameListener(listener)
device.setIrAndDepthFrameListener(listener)

device.start()


def video_export(depth):
    global video_out

    # garder en mémoire le précédent état
    if VARS['save'] == 1 and VARS['last_save'] == 0:
        print("saving video")
        now = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        fps = 25
        w, h = 512, 424
        codec = cv2.VideoWriter_fourcc(*'MJPG')
        filename = f"/home/thomas/Vidéos/interlignes/{now}.avi"
        video_out = cv2.VideoWriter(filename, codec, fps, (w, h))

        VARS['last_save'] == 1
    if VARS['save'] == 1 and VARS['last_save'] == 1:
        video_out.write(depth)
        # gray = depth.asarray(np.uint8)
        # v_img = cv2.cvtColor(depth_arr,depth_arr, cv2.CV_BGR2GRAY)
        # gray = cv2.cvtColor(depth_arr, cv2.COLOR_BGR2GRAY)
    elif VARS['save'] == 0 and VARS['last_save'] == 1:
        video_out.release()
        VARS['last_save'] == 0
        

tracked_points = {}


def blob_detection(depth):
    global tracked_points

    # http://opencv-python-tutroals.readthedocs.io/en/latest/py_tutorials/py_imgproc/py_contours/py_contour_features/py_contour_features.html
    # https://stackoverflow.com/questions/32414559/opencv-contour-minimum-dimension-location-in-python
    ret, frame = cv2.threshold(
        depth, VARS["min_depth"], 255, cv2.THRESH_TOZERO)
    ret, frame = cv2.threshold(
        frame, VARS["max_depth"], 255, cv2.THRESH_TOZERO_INV)
    ret, frame = cv2.threshold(frame, VARS["theta"], 255, 0)

    # remove noise, highlighting the car
    # cv.Erode(car, car, iterations=2)
    # cv.Dilate(car, car, iterations=5)

    out = frame.copy()
    im2, contours, hierarchy = cv2.findContours(
        frame, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)
    # cv2.drawContours(depth, contours, -1, (255,255,0), 255)

    rects = []
    detections = []
    for i, cnt in enumerate(contours):
        # compute the bounding box for the contour
        (x, y, w, h) = cv2.boundingRect(cnt)
        # reject contours outside size range
        if w > VARS["max_blob_size"] or w < VARS["min_blob_size"] or h > VARS["max_blob_size"] or h < VARS["min_blob_size"]:
            continue
        # # make sure the box is inside the frame
        # if x <= 0 or y <= 0 or x+w >= (512 -1) or y+h >= (424 -1):
        #     continue
        # center = (int((x + w) / 2), int((y + h) / 2))
        # points.append(center)
        rects.append((x, y, w, h))
        detections.append((x, y, x + w, y + h, 1))
        # cv2.putText(out, f'{i}', center, font, 1, (0, 0, 255), 1, cv2.LINE_AA)
        cv2.rectangle(out, (x, y), (x + w, y + h), (255, 0, 0), 2)
    try:
        # tracked_points = dict(mot.update(np.array(points), rects))

        detections = sort_tracker.update(np.array(detections))
        tracked_points = {str(int(walker_id)):[int((x2+x1)/2), int((y2+y1)/2)] for x1, y1, x2, y2, walker_id in detections}
        # tracked_points = dict()

        # TODO : vérifier si 'il y a des marcheurs nouveaux ou disparus
        # vérifier les distances entre les précédents et les nouveaux 
        # pour n'envoyer que les points necessaires
        print(tracked_points)


    except Exception as e:
        print(e)
        print(traceback.format_exc())
    return out


async def kinect_loop():
    global displayed_frame
    bg_mask_path = "/home/thomas/dev/Interlignes/interlignes/bg.jpg"
    bg_mask = cv2.imread(bg_mask_path, cv2.IMREAD_GRAYSCALE)
    bg_substractor = cv2.createBackgroundSubtractorMOG2(history=1)
    mask = bg_substractor.apply(bg_mask, learningRate=1)
    # initialisation avec 100x l'image sauvegardée précédement

    while True:
        frames = listener.waitForNewFrame()
        depth = frames["depth"]

        depth_arr = np.array((depth.asarray(np.float32)) /
                             VARS['MAX_DIST'], dtype=np.uint8)
        depth_flip = cv2.flip(depth_arr, 1)

        video_export(depth_flip)

        depth_blur = cv2.blur(depth_flip, (7, 7))

        # acquisition et sauvegarde d'un masque
        mask = bg_substractor.apply(depth_blur, learningRate=VARS["learnBG"])

        blobs = blob_detection(mask)
        displayed_frame = np.hstack((depth_flip, blobs))

        if VARS["learnBG"] == 1:
            VARS["learnBG"] = 0
            cv2.imwrite(bg_mask_path, depth_blur)

        listener.release(frames)
        await asyncio.sleep(0.01)


async def frame_streamer(response):
    while True:
        ret, jpeg = cv2.imencode('.jpg', displayed_frame)
        f = jpeg.tobytes()
        response.write(
            b'--frame\r\nContent-Type: image/jpeg\r\n\r\n' + bytearray(f) + b'\r\n')
        await asyncio.sleep(0.01)


def create_corpus():
    lines = []
    with open("/home/thomas/dev/Interlignes/tentative.txt", "r") as f:
        for l in f:
            l = l.strip()
            if len(l) > 0:
                lines.append(l)
    return lines


corpus = create_corpus()
current_paragraph = 30

app = Sanic(__name__)
CORS(app)


@app.route('/video_feed')
def video_feed(request):
    """Video streaming route. Put this in the src attribute of an img tag."""
    return stream(frame_streamer, content_type='multipart/x-mixed-replace; boundary=frame')


@app.route("/param/<name>/<value>", methods=['POST', 'OPTIONS'])
def post_json(request, name, value):
    VARS[name] = int(value)
    return json({"received": True, "name": name, "value": value})


@app.route("/paragraphe/<walker_id>", methods=['POST', 'OPTIONS'])
def paragraphe(request, walker_id):
    global current_paragraph
    texte = corpus[current_paragraph] + VARS['extra_spaces'] * " "
    current_paragraph += 1
    current_paragraph %= len(corpus)
    return json({"received": True, "walker_id": walker_id, "texte": texte})


# TODO : fusionner corpus et tracker
@app.websocket('/tracker')
async def tracker(request, ws):
    # http://damienclarke.me/code/posts/writing-a-better-noise-reducing-analogread
    # exponential moving avg
    alpha = 0.5
    # previous = np.array([0.0, 0.0])
    # convert = np.array([1920. / 512., 1080 / 424.])
    while True:
        if tracked_points != {}:
            await ws.send(js.dumps(tracked_points))
        await asyncio.sleep(0.01)

        # norm = np.linalg.norm(previous - mot.tracked)
        # faire une serie de normes sur un vecteur de coordonnée ?
        # if norm > VARS["min_norm"]:
        #     previous = mot.tracked
        #     # not np.allclose(previous, mot.tracked):
        #     # previous = (mot.tracked - previous) * alpha
        #     res = (previous * convert).astype(int)
        #     await ws.send(str(res.tolist()))
app.static('/visualisation', './visualisation')


if __name__ == '__main__':
    server = app.create_server(host="0.0.0.0", port=8888, debug=True)
    loop = asyncio.get_event_loop()
    task = asyncio.ensure_future(server)
    kinect_task = asyncio.ensure_future(kinect_loop())

    try:
        loop.run_forever()
    except:
        loop.stop()
        device.stop()
        device.close()
        sys.exit(0)
