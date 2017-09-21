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

class Kinect:
    def __init__(self):
        self.pipeline = OpenCLKdePacketPipeline(0)
        print("Packet pipeline:", type(self.pipeline).__name__)
        fn = Freenect2()
        num_devices = fn.enumerateDevices()
        if num_devices == 0:
            print("No device connected!")
            sys.exit(1)

        serial = fn.getDeviceSerialNumber(0)
        device = fn.openDevice(serial, pipeline=self.pipeline)

        self.listener = SyncMultiFrameListener(FrameType.Color | FrameType.Ir | FrameType.Depth)

        # Register listeners
        device.setColorFrameListener(self.listener)
        device.setIrAndDepthFrameListener(self.listener)

        device.start()

        # NOTE: must be called after device.start()
        self.registration = Registration(device.getIrCameraParams(),
                                    device.getColorCameraParams())

        self.undistorted = Frame(512, 424, 4)
        self.registered = Frame(512, 424, 4)

        # Optinal parameters for registration
        # set True if you need
        need_bigdepth = False
        need_color_depth_map = False

        self.bigdepth = Frame(1920, 1082, 4) if need_bigdepth else None
        self.color_depth_map = np.zeros((424, 512),  np.int32).ravel() \
            if need_color_depth_map else None


    def update(self):
        frames = self.listener.waitForNewFrame()

        color = frames["color"]
        depth = frames["depth"]
        ir = frames["ir"]

        self.registration.apply(color, depth, self.undistorted, self.registered,
                        bigdepth=self.bigdepth,
                        color_depth_map=self.color_depth_map
                        )

        color_img = self.registered.asarray(np.uint8)
        depth_arr = np.array((depth.asarray(np.float32))  / depth_range['MAX_DIST'], dtype=np.uint8)

        self.video_export(depth)

        displayed_frame = self.blob_detection(depth_arr)
        f = self.get_frame(displayed_frame)

        # response.write(b'--frame\r\n'
        #     b'Content-Type: image/jpeg\r\n\r\n' + bytearray(f) + b'\r\n')
        
        self.listener.release(frames)


    def rotate(self, x, y, z):
        """http://mathworld.wolfram.com/RotationMatrix.html"""
        pass

    def setDepthClipping(self, nearClip=500, farClip=4000):
        pass

    def draw(self):
        pass
    
    def close(self):
        pass

async def kinect_loop(response):

    kinect = Kinect()
    while True:
        kinect.update()


