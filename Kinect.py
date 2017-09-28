import sys
import numpy as np
import cv2

from pylibfreenect2 import Freenect2, SyncMultiFrameListener
from pylibfreenect2 import FrameType, Registration, Frame
from pylibfreenect2 import createConsoleLogger, setGlobalLogger
from pylibfreenect2 import LoggerLevel
from pylibfreenect2 import OpenCLKdePacketPipeline

logger = createConsoleLogger(LoggerLevel.Debug)
setGlobalLogger(logger)

# CUDA KDE : https://github.com/antlai/pylibfreenect2
# Improve detection : https://stackoverflow.com/questions/38094594/detect-approximately-objects-on-depth-map


# WRAPPING distorsion : https://github.com/OpenKinect/libfreenect2/issues/41

class DepthVideo:

    def __init__(self, video_path):
        self.video_path = video_path
        self.cap = cv2.VideoCapture(video_path)
        self.frame_counter = 0
        self.gray = None

    def get_frame(self):
        try:
            # if self.gray is not None and ((self.frame_counter%2) == 1):
            #     return self.gray

            if not self.cap.isOpened():
                print("reopen Video")

            ret, frame = self.cap.read()
            self.frame_counter += 1
            if self.frame_counter == self.cap.get(cv2.CAP_PROP_FRAME_COUNT):
                # If the last frame is reached, reset the capture and the frame_counter
                self.frame_counter = 0  # Or whatever as long as it is the same as next line
                self.cap = cv2.VideoCapture(self.video_path)
                # self.cap.set(cv2.cv.CV_CAP_PROP_POS_FRAMES, 0)

            self.gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
            return self.gray
        except Exception as e:
            print(e)

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

    
    def get_frame(self):
        frames = self.listener.waitForNewFrame()
        depth = frames["depth"]

        if self.enable_rgb:
            color = frames["color"]
            ir = frames["ir"]
            
            self.registration.apply(color, depth, self.undistorted, self.registered,
                                    bigdepth=self.bigdepth, color_depth_map=self.color_depth_map)


        # depth_dist = np.array(ir.asarray() / 2, dtype=np.uint8)
        # depth_array = self.bigdepth.asarray(np.float32)
        depth_array = depth.asarray(np.float32)
        depth_dist = np.array(depth_array / self.max_dist, dtype=np.uint8)
        depth_flip = cv2.flip(depth_dist, 1)

        self.listener.release(frames)
        return depth_flip

    def close(self):
        self.device.stop()
        self.device.close()

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
