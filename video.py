import traceback
from conf import VARS
import sys
from datetime import datetime
import threading
import numpy as np
import cv2

# logger = createConsoleLogger(LoggerLevel.Debug)
# setGlobalLogger(logger)


print(cv2.getBuildInformation())

# CUDA KDE : https://github.com/antlai/pylibfreenect2
# Improve detection : https://stackoverflow.com/questions/38094594/detect-approximately-objects-on-depth-map


# WRAPPING distorsion : https://github.com/OpenKinect/libfreenect2/issues/41

class Webcam:
    def __init__(self, webcam_device):
        # cameraPipeline ="v4l2src device=/dev/video1 extra-controls=\"c,exposure_auto=1,exposure_absolute=500\" ! "
        # cameraPipeline+="video/x-raw, format=BGR, framerate=25/1, width=(int)1280,height=(int)720 ! "
        # cameraPipeline+="appsink"

        cameraPipeline = "v4l2src device=/dev/video1 extra-controls=\"c,exposure_auto=0,white_balance_temperature_auto=0\" ! "
        cameraPipeline += "appsink"
        # webcam_device
        # self.cap = cv2.VideoCapture(cameraPipeline)
        pipeline = 'v4l2src device=/dev/video1 ! video/x-raw,framerate=20/1 ! videoscale ! videoconvert ! appsink'
        pipeline = "v4l2src device=/dev/video1 ! videoconvert ! video/x-raw,framerate=10/1 ! appsink"

        pipeline = "v4l2-ctl -d /dev/video1 -c white_balance_automatic=0  -c power_line_frequency=1 -c gain_automatic=0 -c vertical_flip=0"

        self.cap = cv2.VideoCapture(1)
        # , cv2.CAP_GSTREAMER)

        # pos_frame = self.cap.get(1)

    def get_frame(self, get_depth=False, get_ir=False):
        _, frame = self.cap.read()
        gray = frame  # cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)

        return gray, gray

# https://github.com/gilbertfrancois/video-capture-async/blob/master/main/gfd/py/video/capture.py
# http://blog.blitzblit.com/2017/12/24/asynchronous-video-capture-in-python-with-opencv/


class VideoCaptureTreading:
    def __init__(self, src=0, width=640, height=400):
        self.src = src
        self.cap = cv2.VideoCapture(self.src)
        # self.cap.set(cv2.CAP_PROP_FRAME_WIDTH, width)
        # self.cap.set(cv2.CAP_PROP_FRAME_HEIGHT, height)
        self.cap.set(cv2.CAP_PROP_FPS, 12)

        self.grabbed, self.frame = self.cap.read()
        self.started = False
        self.read_lock = threading.Lock()

    def set(self, var1, var2):
        self.cap.set(var1, var2)

    def start(self):
        if self.started:
            print('[!] Threaded video capturing has already been started.')
            return None
        self.started = True
        self.thread = threading.Thread(target=self.update, args=())
        self.thread.start()
        return self

    def update(self):
        while self.started:
            grabbed, frame = self.cap.read()
            with self.read_lock:
                self.grabbed = grabbed
                self.frame = frame

    def read(self):
        with self.read_lock:
            frame = self.frame.copy()
            grabbed = self.grabbed
        return grabbed, frame

    def get_frame(self):
        with self.read_lock:
            gray = cv2.cvtColor(self.frame, cv2.COLOR_BGR2GRAY)
        return gray

    def stop(self):
        self.started = False
        self.thread.join()

    def __exit__(self, exec_type, exc_value, traceback):
        self.cap.release()


class VideoReader:

    def __init__(self, video_path):
        self.video_path = video_path
        self.cap = cv2.VideoCapture(video_path)
        self.cap.set(cv2.CAP_PROP_FPS, 12)
        self.frame_counter = 0
        self.gray = None

    def get_frame(self, get_depth=False, get_ir=False):
        if not self.cap.isOpened(): # or self.frame_counter == self.cap.get(cv2.cv.CV_CAP_PROP_FRAME_COUNT):
            print("reopen Video")
            self.frame_counter = 0
            self.cap = cv2.VideoCapture(self.video_path)
        ret, frame = self.cap.read()
        if ret:
            self.gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        else:
            self.cap.set(cv2.CAP_PROP_POS_FRAMES, 0)
            self.cap = cv2.VideoCapture(self.video_path)
        return self.gray

    def close(self):
        self.cap.release()

    def stop(self):
        self.cap.release()


class VideoRecorder:
    def __init__(self, path="/home/thomas/Vidéos/interlignes"):
        self.path = path
        self.video_out = None
        self.recording = False

    def start_recording(self):
        print("start recording video")
        self.recording = True
        now = datetime.now().strftime('%Y-%m-%d_%H:%M:%S')
        fps = 25
        w, h = 512, 424
        codec = cv2.VideoWriter_fourcc(*'MJPG')
        filename = f"{self.path}/{now}.avi"
        self.video_out = cv2.VideoWriter(filename, codec, fps, (w, h))
        VARS['last_save'] = 1

    def record(self, frame):
        try:
            color = cv2.cvtColor(frame, cv2.COLOR_GRAY2BGR)
            self.video_out.write(color)
        except Exception as e:
            print(e)
            print(traceback.format_exc())

    def stop_recording(self):
        if self.video_out:
            VARS['last_save'] = 0
            self.video_out.release()
            self.video_out = None
        self.recording = False

# async def kinect_loop(response):
#     kinect = Kinect()
#     while True:
#         depth_array = kinect.get_frame()

        # color_img = self.registered.asarray(np.uint8)
        # depth_arr = np.array((depth.asarray(np.float32))  / depth_range['MAX_DIST'], dtype=np.uint8)

        # self.video_export(depth)

        # displayed_frame = self.blob_detection(depth_arr)
        # f = self.get_frame(displayed_frame)

        # # response.write(b'--frame\r\n'
        # #     b'Content-Type: image/jpeg\r\n\r\n' + bytearray(f) + b'\r\n')

    # def rotate(self, x, y, z):
    #     """http://mathworld.wolfram.com/RotationMatrix.html"""
    #     pass

    # def setDepthClipping(self, nearClip=500, farClip=4000):
    #     pass

    # def draw(self):
    #     pass
