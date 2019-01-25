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
