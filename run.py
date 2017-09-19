import numpy as np
import cv2
import sys
import asyncio
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

Config.REQUEST_TIMEOUT = 100000
Config.KEEP_ALIVE = False


from MultiObjectTracker import MultiObjectTracker

def create_corpus():
    lines = []
    with open("/home/thomas/dev/Interlignes/tentative.txt", "r") as f:
        for l in f:
            l = l.strip()
            if len(l) > 0:
                lines.append(l)
    return lines

corpus = create_corpus()

mot = MultiObjectTracker()

MAX_DIST = 18750. / 255.
depth_range = {"min_depth":0, "max_depth":255, "theta":0, "save":0, "MAX_DIST":MAX_DIST}

# Doit être stocké comme un JSON à l'exterieur de l'application


font = cv2.FONT_HERSHEY_SIMPLEX
# textCol = (0,255,0)
fps = 25
w,h = 512, 424
filename = '/tmp/depth.avi'
codec = cv2.VideoWriter_fourcc(*'MJPG')
# out = cv2.VideoWriter('/tmp/output.avi', -1, 20.0, (512, 424))
video_out = cv2.VideoWriter(filename, codec, fps, (w,h))

pipeline = OpenCLKdePacketPipeline(0)

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

listener = SyncMultiFrameListener(FrameType.Depth) #  | FrameType.Color | FrameType.Ir)

# Register listeners
# device.setColorFrameListener(listener)
device.setIrAndDepthFrameListener(listener)

device.start()

# NOTE: must be called after device.start()
# registration = Registration(device.getIrCameraParams(),
#                             device.getColorCameraParams())

undistorted = Frame(512, 424, 4)
registered = Frame(512, 424, 4)

# Optinal parameters for registration
# set True if you need
need_bigdepth = False
need_color_depth_map = False

bigdepth = Frame(1920, 1082, 4) if need_bigdepth else None
color_depth_map = np.zeros((424, 512),  np.int32).ravel() \
    if need_color_depth_map else None


def blob_detection(depth):
    # http://opencv-python-tutroals.readthedocs.io/en/latest/py_tutorials/py_imgproc/py_contours/py_contour_features/py_contour_features.html
    # https://stackoverflow.com/questions/32414559/opencv-contour-minimum-dimension-location-in-python


    # ret,frame = cv2.threshold(depth_arr,70,100,0)
    # frame = cv2.bitwise_not(frame)
    # frame = cv2.adaptiveThreshold(depth_arr,255,cv2.ADAPTIVE_THRESH_GAUSSIAN_C, cv2.THRESH_BINARY,11,2)

    ret,frame = cv2.threshold(depth, depth_range["min_depth"], 255, cv2.THRESH_TOZERO)
    ret,frame = cv2.threshold(frame, depth_range["max_depth"],255,cv2.THRESH_TOZERO_INV)
    ret,frame = cv2.threshold(frame, depth_range["theta"],255,0)

    out = frame.copy()
    im2, contours, hierarchy = cv2.findContours(frame,cv2.RETR_TREE,cv2.CHAIN_APPROX_SIMPLE)
    # cv2.drawContours(depth, contours, -1, (255,255,0), 255)

    points = []
    rects = []

    for i, cnt in enumerate(contours):
        # compute the bounding box for the contour
        (x, y, w, h) = cv2.boundingRect(cnt)
        # reject contours outside size range
        if w > 500 or w < 30 or h > 500 or h < 30 :
            continue
        # # make sure the box is inside the frame
        # if x <= 0 or y <= 0 or x+w >= (512 -1) or y+h >= (424 -1):
        #     continue
        center = ( int((x + w)/2), int((y + h) / 2) )
        points.append(center)
        rects.append((x, y, w, h))
        cv2.putText(out, f'{i}', center, font, 1, (0,0,255),1,cv2.LINE_AA)
        cv2.rectangle(out,(x,y),(x+w,y+h),(255,0,0),2)
    mot.update(np.array(points), rects)
    return out


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

    # fgmask = None
    # for t in range(100):
    #     frames = listener.waitForNewFrame()
    #     depth = frames["depth"]
    #     fgmask = bg_substractor.apply(depth_arr)
    #     listener.release(frames)
    #     await asyncio.sleep(0.01)

    bg_ref = cv2.imread("/home/thomas/dev/Interlignes/interlignes/bg.jpg")
    fg_img = None
    t = 0
    bg_substractor = cv2.createBackgroundSubtractorMOG2()

    while True:
        frames = listener.waitForNewFrame()
        depth = frames["depth"]

        depth_arr = np.array((depth.asarray(np.float32))  / depth_range['MAX_DIST'], dtype=np.uint8)
        depth_arr = cv2.blur(depth_arr,(5,5))
        depth_arr=cv2.flip(depth_arr,1)

        if t < 200:
            # c'est possible de l'initialiser avec 100x l'image sauvegardée précédement
            mask = bg_substractor.apply(bg_ref, learningRate=0.5)        # depth_arr
        elif t == 200:
            cv2.imwrite("/tmp/fg.jpg", depth_arr)

        else:
            mask = bg_substractor.apply(depth_arr, learningRate=0)       
            blobs = blob_detection(mask)        
            displayed_frame = np.hstack((mask, blobs)) # , mask

        listener.release(frames)
        await asyncio.sleep(0.01)
        t += 1


async def frame_streamer(response):
    while True:
        ret, jpeg = cv2.imencode('.jpg', displayed_frame)
        f = jpeg.tobytes()
        response.write(b'--frame\r\nContent-Type: image/jpeg\r\n\r\n' + bytearray(f) + b'\r\n')
        await asyncio.sleep(0.01)


app = Sanic(__name__)
CORS(app)

@app.route('/video_feed')
def video_feed(request):
    """Video streaming route. Put this in the src attribute of an img tag."""
    return stream(frame_streamer, content_type='multipart/x-mixed-replace; boundary=frame') # , keep_alive = True)
    

@app.route("/param/<name>/<value>", methods=['POST', 'OPTIONS'])
def post_json(request, name, value):
    depth_range[name] = int(value)
    return json({ "received": True, "name":name, "value": value})

@app.websocket('/')
async def feed(request, ws):
    while True:
        for line in corpus:
            await ws.send(str(line))
            print(line)
            await asyncio.sleep(int(len(line) / 10) + 2)

@app.websocket('/tracker')
async def feed(request, ws):
    # http://damienclarke.me/code/posts/writing-a-better-noise-reducing-analogread
    # exponential moving avg
    alpha = 0.5
    previous = np.array([1.0,1.0])
    convert = np.array([1920./512., 1080 / 424.])
    while True:
        norm = np.linalg.norm(previous - mot.tracked)
        # print(norm)
        if norm > 1:
            previous = mot.tracked
            # not np.allclose(previous, mot.tracked):
            # previous = (mot.tracked - previous) * alpha
            res = (previous * convert).astype(int)
            await ws.send(str(res.tolist()))
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
