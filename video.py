import sys
from datetime import datetime

import numpy as np
import cv2

from pylibfreenect2 import Freenect2, SyncMultiFrameListener
from pylibfreenect2 import FrameType, Registration, Frame
from pylibfreenect2 import createConsoleLogger, setGlobalLogger
from pylibfreenect2 import LoggerLevel
from pylibfreenect2 import OpenCLKdePacketPipeline

logger = createConsoleLogger(LoggerLevel.Debug)
setGlobalLogger(logger)

from conf import VARS
import traceback



print(cv2.getBuildInformation())

# CUDA KDE : https://github.com/antlai/pylibfreenect2
# Improve detection : https://stackoverflow.com/questions/38094594/detect-approximately-objects-on-depth-map


# WRAPPING distorsion : https://github.com/OpenKinect/libfreenect2/issues/41

class Webcam:
    def __init__(self, webcam_device):
        # cameraPipeline ="v4l2src device=/dev/video1 extra-controls=\"c,exposure_auto=1,exposure_absolute=500\" ! "
        # cameraPipeline+="video/x-raw, format=BGR, framerate=25/1, width=(int)1280,height=(int)720 ! "
        # cameraPipeline+="appsink"

        cameraPipeline ="v4l2src device=/dev/video1 extra-controls=\"c,exposure_auto=0,white_balance_temperature_auto=0\" ! "
        cameraPipeline+="appsink"
        # webcam_device
        # self.cap = cv2.VideoCapture(cameraPipeline)
        pipeline = 'v4l2src device=/dev/video1 ! video/x-raw,framerate=20/1 ! videoscale ! videoconvert ! appsink'
        pipeline = "v4l2src device=/dev/video1 ! videoconvert ! video/x-raw,framerate=10/1 ! appsink"

        pipeline = "v4l2-ctl -d /dev/video1 -c white_balance_automatic=0  -c power_line_frequency=1 -c gain_automatic=0 -c vertical_flip=0"

        self.cap = cv2.VideoCapture(1)
        #, cv2.CAP_GSTREAMER)

        # pos_frame = self.cap.get(1)

    def get_frame(self, get_depth=False, get_ir=False):
        _, frame = self.cap.read()
        gray = frame # cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)

        return gray, gray


class DepthVideo:

    def __init__(self, video_path):
        self.video_path = video_path
        self.cap = cv2.VideoCapture(video_path)
        # self.cap.set(cv2.CAP_PROP_FPS, 25)
        self.frame_counter = 0
        self.gray = None

        # self.pos_frame = self.cap.get(cv2.CAP_PROP_POS_FRAMES)

    # def get_frame_slow(self):
    #     flag, frame = self.cap.read()
    #     if flag:
    #         # The frame is ready and already captured
    #         self.pos_frame = self.cap.get(cv2.CAP_PROP_POS_FRAMES)
    #         print( str(pos_frame)+" frames")
    #     else:
    #         # The next frame is not ready, so we try to read it again
    #         self.cap.set(cv2.cv.CAP_PROP_POS_FRAMES, pos_frame-1)
    #         # It is better to wait for a while for the next frame to be ready
    #         cv2.waitKey(1000)

    def get_frame(self, get_depth=False, get_ir=False):

        # try:
            # if self.gray is not None and ((self.frame_counter%2) == 1):
            #     return self.gray

        if not self.cap.isOpened():
            print("reopen Video")

        ret, frame = self.cap.read()
        if ret:
            self.frame_counter += 1
            if self.frame_counter == self.cap.get(cv2.CAP_PROP_FRAME_COUNT):
                # If the last frame is reached, reset the capture and the frame_counter
                self.frame_counter = 0  # Or whatever as long as it is the same as next line
                self.cap = cv2.VideoCapture(self.video_path)
                # self.cap.set(cv2.CAP_PROP_FPS, 25)

            self.gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        return self.gray, self.gray
        # except Exception as e:
        #     print(e)

    def close(self):
        self.cap.release()


class Kinect:

    max_dist = 70

    def __init__(self, need_bigdepth=False, enable_rgb=False, need_color_depth_map=False):
        self.enable_rgb = enable_rgb
        self.pipeline = OpenCLKdePacketPipeline(0)
        print("Packet pipeline:", type(self.pipeline).__name__)
        self.fn = Freenect2()
        num_devices = self.fn.enumerateDevices()
        if num_devices == 0:
            print("No device connected!")
            raise Exception("Pas de kinect connectée")
            # sys.exit(1)

        serial = self.fn.getDeviceSerialNumber(0)
        self.device = self.fn.openDevice(serial, pipeline=self.pipeline)

        types = (FrameType.Ir | FrameType.Depth)
        if self.enable_rgb:
            types |= FrameType.Color

        self.listener = SyncMultiFrameListener(types)

        if self.enable_rgb:
            self.device.setColorFrameListener(self.listener)
        self.device.setIrAndDepthFrameListener(self.listener)

        # Register listeners
        self.device.start()
        # self.device.startStreams(rgb=self.enable_rgb, depth=True)

        # NOTE: must be called after device.start()
        if self.enable_rgb:
            self.registration = Registration(
                self.device.getIrCameraParams(), self.device.getColorCameraParams())

            self.undistorted = Frame(512, 424, 4)
            self.registered = Frame(512, 424, 4)
            self.bigdepth = Frame(1920, 1082, 4) if need_bigdepth else None
            self.color_depth_map = np.zeros((424, 512), np.int32).ravel() \
                if need_color_depth_map else None

    def get_frame(self, get_depth=False, get_ir=False, record=False):
        frames = self.listener.waitForNewFrame()
        depth = frames["depth"]

        if self.enable_rgb:
            color = frames["color"]
            # ir = frames["ir"]
            self.registration.apply(color, depth, self.undistorted, self.registered,
                                    bigdepth=self.bigdepth, color_depth_map=self.color_depth_map)

        res = []
        if get_depth:
            depth_array = depth.asarray(np.float32)
            depth_dist = np.array(depth_array / self.max_dist, dtype=np.uint8)
            depth_flip = cv2.flip(depth_dist, 1)
            res.append(depth_flip)
        if get_ir:
            ir = frames["ir"]
            ir_norm = np.array(ir.asarray(np.float32) /
                               self.max_dist, dtype=np.uint8)
            # ir_norm = np.array(ir.asarray(np.float32)/2, dtype=np.uint8)
            ir_flip = cv2.flip(ir_norm, 1)
            res.append(ir_flip)

        # depth_array = self.bigdepth.asarray(np.float32)

        self.listener.release(frames)
        return res

    def close(self):
        self.device.stop()
        self.device.close()


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
