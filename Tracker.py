import cv2
import numpy as np
import traceback
from sort import Sort
from conf import VARS
from BGSubstractor import BGSubstractor


class FrameProcessor:
    bgs = BGSubstractor("depth_ir")  # BGSWrapper()
    sort_tracker = Sort(max_age=5, min_hits=10)
    font = cv2.FONT_HERSHEY_SIMPLEX
    morph_type = cv2.MORPH_OPEN

    def __init__(self):
        self.frame = None
        self.blobs = None
        self.mask = None

    def update(self, frame):
        self.frame0 = frame.copy()
        self.frame = frame

    def process(self):
        self.frame = self.bg_substract()
        # self.threshold(
        #     min_depth=VARS["min_depth"], max_depth=VARS["max_depth"], theta=VARS["theta"])
        self.frame = self.clean(self.frame,
                                VARS["erode_kernel_size"],
                                VARS["erode_iterations"])

        detections = self.blob_detection(VARS["min_blob_size"],
                                         VARS["max_blob_size"])
        return self.track(detections)

    def threshold(self, min_depth, max_depth, theta):
        if min_depth > 0:
            _, self.frame = cv2.threshold(
                self.frame, min_depth, 255, cv2.THRESH_TOZERO)

        if max_depth < 255:
            _, self.frame = cv2.threshold(
                self.frame, max_depth, 255, cv2.THRESH_TOZERO_INV)

        _, self.frame = cv2.threshold(self.frame, theta, 255, 0)

        # frame = cv2.adaptiveThreshold(frame, 255,cv2.ADAPTIVE_THRESH_MEAN_C, cv2.THRESH_BINARY,11,2)
        # return frame

    def save_background(self):
        self.bgs.save(self.frame0)

    def bg_substract(self):
        return self.bgs.apply(self.frame, lr=VARS["learnBG"])

    def clean(self, mask, kernel_size, iterations):
        kernel = np.ones((kernel_size, kernel_size), np.uint8)
        mask_dilate = cv2.morphologyEx(
            mask, self.morph_type, kernel, iterations)
        return mask_dilate

        # self.frame = cv2.bitwise_and(self.frame, mask_dilate)
        # img_mask_dilate = cv2.bitwise_and(self.frame, mask_dilate)
        # return img_mask_dilate
        # depth = cv2.fastNlMeansDenoising(depth, None, 9, 13)
        # depth = cv2.GaussianBlur(depth, cv2.BLUR_KERNEL_SIZE, 3)

    def save(self):
        pass

    def blob_detection(self, min_blob_size,  max_blob_size):
        # http://opencv-python-tutroals.readthedocs.io/en/latest/py_tutorials/py_imgproc/py_contours/py_contour_features/py_contour_features.html
        # https://stackoverflow.com/questions/32414559/opencv-contour-minimum-dimension-location-in-python
        # self.blobs = self.frame.copy()
        self.blobs = cv2.cvtColor(self.frame, cv2.COLOR_GRAY2BGR)
        _im2, contours, _hier = cv2.findContours(self.frame,
                                                 cv2.RETR_EXTERNAL,
                                                 cv2.CHAIN_APPROX_SIMPLE)

        # frame, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)
        # cv2.RETR_CCOMP,cv2.CHAIN_APPROX_SIMPLE

        rects = []
        detections = []
        for _i, cnt in enumerate(contours):
            # compute the bounding box for the contour
            (x, y, w, h) = cv2.boundingRect(cnt)
            # reject contours outside size range
            if w > max_blob_size or w < min_blob_size or h > max_blob_size or h < min_blob_size:
                continue
            rects.append((x, y, w, h))
            detections.append((x, y, x + w, y + h, 1))
            cv2.rectangle(self.blobs, (x, y), (x + w, y + h), (255, 0, 0), 2)
        return np.array(detections)

    def track(self, detections):
        try:
            tracked_points = {}

            for x1, y1, x2, y2, walker_id in self.sort_tracker.update(detections):
                w_id = str(int(walker_id))
                x = int((x2 + x1) / 2)
                y = int((y2 + y1) / 2)
                tracked_points[w_id] = [x, y2]
                cv2.circle(self.blobs, (x, int(y2)), 5, (0, 0, 255), -1)
                cv2.putText(self.blobs, w_id, (x, y),
                            self.font, 1, (128, 128, 0), 1, cv2.LINE_AA)

        except Exception as e:
            print(e)
            print(traceback.format_exc())

        return tracked_points

    async def get_jpeg_bytes(self, display_mode):
        if display_mode == 0:
            displayed_frame = self.blobs
        elif display_mode == 1:
            displayed_frame = self.frame
        elif display_mode == 2:
            displayed_frame = self.frame0

        ret, jpeg = cv2.imencode('.jpg', displayed_frame)
        f = jpeg.tobytes()  # bytearray
        if ret:
            return b'--frame\r\nContent-Type: image/jpeg\r\n\r\n' + f + b'\r\n'

    # def create_simple_detector(self):

    #     params = cv2.SimpleBlobDetector_Params()

    #     # Change thresholds
    #     params.minThreshold = 100
    #     params.maxThreshold = 5000

    #     # Filter by Area.
    #     params.filterByArea = True
    #     params.minArea = 10000  # min_blob_size

    #     # Filter by Circularity
    #     params.filterByCircularity = False
    #     # params.minCircularity = 0.785

    #     # Filter by Convexity
    #     params.filterByConvexity = False
    #     # params.minConvexity = 0.87

    #     # Filter by Inertia
    #     #params.filterByInertia = True
    #     #params.minInertiaRatio = 0.01

    #     # Set up the detector with default parameters.
    #     self.simple_detector = cv2.SimpleBlobDetector(params)

    # def simple_detection(self, min_blob_size=VARS["min_blob_size"],  max_blob_size=VARS["max_blob_size"]):
    #     self.blobs = cv2.cvtColor(self.frame, cv2.COLOR_GRAY2BGR)

    #     # Detect blobs.
    #     detections = []
    #     for p in self.simple_detector.detect(self.frame):
    #         x = p.pt[0]
    #         y = p.pt[1]
    #         w, h = p.size, p.size
    #         detections.append((x, y, x + w, y + h, 1))
    #         cv2.rectangle(self.blobs, (x, y), (x + w, y + h), (0, 0, 255), 2)
    #     return []

    # def hog_detection(self):
    #     self.blobs = cv2.cvtColor(self.frame, cv2.COLOR_GRAY2BGR)
    #     # self.frame0.copy()

    #     # detect people in the image
    #     (rects, _weights) = self.hog.detectMultiScale(self.frame, winStride=(4, 4),
    #                                                   padding=(8, 8), scale=1.05)

    #     # draw the original bounding boxes
    #     detections = []

    #     for (x, y, w, h) in rects:
    #         detections.append((x, y, x + w, y + h, 1))
    #         cv2.rectangle(self.blobs, (x, y), (x + w, y + h), (0, 0, 255), 2)
    #     return detections

        # self.hog.setSVMDetector(cv2.HOGDescriptor_getDefaultPeopleDetector())
        # self.simple_detect = False
        # self.create_simple_detector()

        # if self.simple_detect:
        #     # detections = self.hog_detection()
        #     detections = self.simple_detection()
        # else:
