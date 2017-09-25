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

class Kinect:
    def __init__(self, need_bigdepth = False, enable_rgb= True, need_color_depth_map = False):
        self.pipeline = OpenCLKdePacketPipeline(0)
        print("Packet pipeline:", type(self.pipeline).__name__)
        self.fn = Freenect2()
        num_devices = self.fn.enumerateDevices()
        if num_devices == 0:
            print("No device connected!")
            sys.exit(1)

        serial = self.fn.getDeviceSerialNumber(0)
        self.device = self.fn.openDevice(serial, pipeline=self.pipeline)


        types = (FrameType.Ir | FrameType.Depth)
        self.enable_rgb = enable_rgb
        if self.enable_rgb:
            types |= FrameType.Color

        self.listener = SyncMultiFrameListener(types)
        self.device.setIrAndDepthFrameListener(self.listener)
    
        if self.enable_rgb:
            self.device.setColorFrameListener(self.listener)

        # Register listeners
        self.device.start()
        # self.device.startStreams(rgb=self.enable_rgb, depth=True)


        # NOTE: must be called after device.start()
        if self.enable_rgb:
            self.registration = Registration(self.device.getIrCameraParams(), self.device.getColorCameraParams())

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

        depth_array = depth.asarray(np.float32)
        self.listener.release(frames)
        return depth_array


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
    
