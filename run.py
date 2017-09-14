import numpy as np
import cv2
import sys
from signal import signal, SIGINT


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

# Config.REQUEST_TIMEOUT = 1000

import asyncio


def create_corpus():
    lines = []
    with open("/home/thomas/dev/Interlignes/tentative.txt", "r") as f:
        for l in f:
            l = l.strip()
            if len(l) > 0:
                lines.append(l)
    return lines

app = Sanic(__name__)
CORS(app)

corpus = create_corpus()


MAX_DIST = 18750. / 255.
depth_range = {"min_depth":0, "max_depth":255, "theta":127, "save":0, "MAX_DIST":MAX_DIST}

w,h = 512, 424
# out = cv2.VideoWriter('/tmp/output.avi', -1, 20.0, (512, 424))
# codec = -1
# font = cv2.FONT_HERSHEY_SIMPLEX
# textCol = (0,255,0)
fps = 25
filename = '/tmp/depth.avi'
codec = cv2.VideoWriter_fourcc(*'MJPG')
# codec = cv2.VideoWriter_fourcc(*'XVID')
video_out = cv2.VideoWriter(filename, codec, fps, (w,h))

# detector = create_detector()
pipeline = OpenCLKdePacketPipeline(0)

print("Packet pipeline:", type(pipeline).__name__)


# MAX_DIST = 18750. / 255.



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

listener = SyncMultiFrameListener(
    FrameType.Color | FrameType.Ir | FrameType.Depth)

# Register listeners
device.setColorFrameListener(listener)
device.setIrAndDepthFrameListener(listener)

device.start()

# NOTE: must be called after device.start()
registration = Registration(device.getIrCameraParams(),
                            device.getColorCameraParams())

undistorted = Frame(512, 424, 4)
registered = Frame(512, 424, 4)

# Optinal parameters for registration
# set True if you need
need_bigdepth = False
need_color_depth_map = False

bigdepth = Frame(1920, 1082, 4) if need_bigdepth else None
color_depth_map = np.zeros((424, 512),  np.int32).ravel() \
    if need_color_depth_map else None

font = cv2.FONT_HERSHEY_SIMPLEX



def blob_detection(depth_arr):
    # http://opencv-python-tutroals.readthedocs.io/en/latest/py_tutorials/py_imgproc/py_contours/py_contour_features/py_contour_features.html
    # https://stackoverflow.com/questions/32414559/opencv-contour-minimum-dimension-location-in-python


    # ret,frame = cv2.threshold(depth_arr,70,100,0)
    # frame = cv2.bitwise_not(frame)
    # frame = cv2.adaptiveThreshold(depth_arr,255,cv2.ADAPTIVE_THRESH_GAUSSIAN_C, cv2.THRESH_BINARY,11,2)

    ret,frame = cv2.threshold(depth_arr, depth_range["min_depth"], 255, cv2.THRESH_TOZERO)
    ret,frame = cv2.threshold(frame, depth_range["max_depth"],255,cv2.THRESH_TOZERO_INV)
    ret,frame = cv2.threshold(frame, depth_range["theta"],255,0)

    im2, contours, hierarchy = cv2.findContours(frame,cv2.RETR_TREE,cv2.CHAIN_APPROX_SIMPLE)
    cv2.drawContours(frame, contours, -1, (0,255,0), 3)

    displayed_frame = depth_arr.copy()
    for i, cnt in enumerate(contours):
        # compute the bounding box for the contour
        (x, y, w, h) = cv2.boundingRect(cnt)
        # reject contours outside size range
        if w > 500 or w < 100 or h > 500 or h < 100 :
            continue
        # # make sure the box is inside the frame
        if x <= 0 or y <= 0 or x+w >= (512 -1) or y+h >= (424 -1):
            continue
        center = ( int((x + w)/2), int((y + h) / 2) )
        cv2.putText(displayed_frame, f'{i}', center, font, 1, (0,0,255),1,cv2.LINE_AA)
        cv2.rectangle(displayed_frame,(x,y),(x+w,y+h),(255,0,0),2)
    return displayed_frame

def video_export(depth):
    # garder en mémoire le précédent état
    if depth_range['save'] == 1:
        print("saving video")
        gray = depth.asarray(np.uint8)
        # v_img = cv2.cvtColor(depth_arr,depth_arr, cv2.CV_BGR2GRAY)
        # gray = cv2.cvtColor(depth_arr, cv2.COLOR_BGR2GRAY) 
        video_out.write(gray)
    elif depth_range['save'] == 2:
        video_out.release()

displayed_frame = None
async def kinect_loop():
    global displayed_frame
    while True:
        frames = listener.waitForNewFrame()

        color = frames["color"]
        depth = frames["depth"]
        ir = frames["ir"]

        registration.apply(color, depth, undistorted, registered,
                        bigdepth=bigdepth,
                        color_depth_map=color_depth_map
                        )

        color_img = registered.asarray(np.uint8)
        depth_arr = np.array((depth.asarray(np.float32))  / depth_range['MAX_DIST'], dtype=np.uint8)
        video_export(depth)
        displayed_frame = blob_detection(depth_arr)
        listener.release(frames)
        # pourquoi ?
        # key = cv2.waitKey(delay=1)
        await asyncio.sleep(0.01)

# def get_frame(frame):
#     ret, jpeg = cv2.imencode('.jpg', frame)
#     return jpeg.tobytes()

async def frame_streamer(response):
    while True:
        # f = get_frame(displayed_frame)
        ret, jpeg = cv2.imencode('.jpg', displayed_frame)
        f = jpeg.tobytes()
        response.write(b'--frame\r\n'
            b'Content-Type: image/jpeg\r\n\r\n' + bytearray(f) + b'\r\n')
        await asyncio.sleep(0.01)

@app.route('/video_feed')
def video_feed(request):
    """Video streaming route. Put this in the src attribute of an img tag."""
    return stream(frame_streamer, content_type='multipart/x-mixed-replace; boundary=frame')
#    return stream(kinect_loop, content_type='multipart/x-mixed-replace; boundary=frame')

@app.route("/param/<name>/<value>", methods=['POST', 'OPTIONS'])
def post_json(request, name, value):
    depth_range[name] = int(value)
    return json({ "received": True, "name":name, "value": value })

@app.websocket('/')
async def feed(request, ws):
    while True:
        for line in corpus:
            await ws.send(str(line))
            print(line)
            await asyncio.sleep(int(len(line) / 10) + 2)

@app.websocket('/tracker')
async def feed(request, ws):
    while True:
        if new_coord:
            await ws.send(str(line))
        await asyncio.sleep(0.01)

app.static('/visualisation', './visualisation')


if __name__ == '__main__':

    server = app.create_server(host="0.0.0.0", port=8888, debug=True)
    loop = asyncio.get_event_loop()
    task = asyncio.ensure_future(server)
    kinect_task = asyncio.ensure_future(kinect_loop())

    # signal(SIGINT, lambda s, f: loop.stop())
    try:
        loop.run_forever()
    except:
        loop.stop()
        device.stop()
        device.close()
        sys.exit(0)
