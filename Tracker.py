import os
import cv2
import numpy as np
import bgs
import traceback
from sort import Sort
from conf import VARS


# class BGStrategy:

#     def __init(self, name, algo_name):
#         self.name = name
#         self.set_algo(algo_name)

#     def set_algo(self, algo_name):
#         if algo_name == "MOG2":
#             self.algo = BGSubstractor(self.name)
#         else:
#             self.algo = BGSWrapper()

#     def save(self, frame):
#         self.algo.


class DummySubstractor:
    """Wrapper for OpenCv BG Substractor"""

    def __init__(self, name, bg_mask_path="/home/thomas/dev/Interlignes/interlignes/"):
        self.mask_path = f"{bg_mask_path}/{name}.jpg"
        self.init = False
        # self.bg_substractor = cv2.createBackgroundSubtractorMOG2()
        # self.bg_substractor = cv2.createBackgroundSubtractorMOG2(
        # history=1, detectShadows=False, varThreshold=8)
        if os.path.exists(self.mask_path):
            self.bg_mask = cv2.imread(self.mask_path, cv2.IMREAD_GRAYSCALE)
            self.init = True
        # self.algo = None
        # TODO répliquer ce comportement sur la librairie BGS
        # Prendre 10 secondes pour apprendre le masque sur une frame
        # Ou faire apprendre le masque toutes les X frames (paramétrable)

    def apply(self, frame, lr=VARS["learnBG"]):
        """acquisition et sauvegarde d'un masque
           http://docs.opencv.org/3.0-beta/doc/py_tutorials/py_imgproc/py_morphological_ops/py_morphological_ops.html
        """
        # return self.bg_substractor.apply(frame, learningRate=lr)
        return frame
        # return cv2.bitwise_and(frame, mask)

    def save(self, frame):
        self.bg_mask = frame
        _ = self.apply(self.bg_mask, lr=1)
        cv2.imwrite(self.mask_path, self.bg_mask)


class BGSubstractor:
    """Wrapper for OpenCv BG Substractor"""

    def __init__(self, name, bg_mask_path="/home/thomas/dev/Interlignes/interlignes/"):
        self.mask_path = f"{bg_mask_path}/{name}.jpg"
        self.init = False
        # self.bg_substractor = cv2.createBackgroundSubtractorMOG2()
        self.bg_substractor = cv2.createBackgroundSubtractorMOG2(
            history=1, detectShadows=False, varThreshold=8)
        if os.path.exists(self.mask_path):
            self.bg_mask = cv2.imread(self.mask_path, cv2.IMREAD_GRAYSCALE)
            self.init = True
        # self.algo = None
        # TODO répliquer ce comportement sur la librairie BGS
        # Prendre 10 secondes pour apprendre le masque sur une frame
        # Ou faire apprendre le masque toutes les X frames (paramétrable)

    def apply(self, frame, lr=VARS["learnBG"]):
        """acquisition et sauvegarde d'un masque
           http://docs.opencv.org/3.0-beta/doc/py_tutorials/py_imgproc/py_morphological_ops/py_morphological_ops.html
        """
        return self.bg_substractor.apply(frame, learningRate=lr)
        # return cv2.bitwise_and(frame, mask)

    def save(self, frame):
        self.bg_mask = frame
        _ = self.apply(self.bg_mask, lr=1)
        cv2.imwrite(self.mask_path, self.bg_mask)


class BGSWrapper:
    def __init__(self):
        self.algo_a = bgs.CodeBook()
        # self.algo_b = bgs.CodeBook()
        self.nb_frames = 0
        self.init = True
        # bgs.LBSimpleGaussian() #
        # bg_algo = bgs.LBFuzzyGaussian()

    def apply(self, frame, lr=VARS["learnBG"]):
        # self.nb_frames += 1
        mask = self.algo_a.apply(frame)
        return mask
        # if lr == 1:
        #     mask = self.algo_b.apply(frame)
        # self.algo_a = self.algo_b

    def save(self, bg_mask):
        pass


class FrameProcessor:
    bgs = BGSubstractor("depth_ir") # BGSWrapper()
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
        self.blur(blur=VARS["blur"])
        # self.threshold(
        #     min_depth=VARS["min_depth"], max_depth=VARS["max_depth"], theta=VARS["theta"])
        self.frame = self.clean(self.frame, VARS["erode_kernel_size"],
                                VARS["erode_iterations"])

        self.blobs = self.blob_detection(
            VARS["min_blob_size"],  VARS["max_blob_size"])

    def threshold(self, min_depth=VARS["min_depth"], max_depth=VARS["max_depth"], theta=VARS["theta"]):
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
        self.bgs.save(self.frame)

    def bg_substract(self):
        return self.bgs.apply(self.frame)

    def blur(self, blur=VARS["blur"]):
        if blur:
            self.frame = cv2.blur(self.frame, (blur, blur))

    def clean(self, mask, kernel_size=VARS["erode_kernel_size"], iterations=VARS["erode_iterations"]):
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

    def blob_detection(self, min_blob_size=VARS["min_blob_size"],  max_blob_size=VARS["max_blob_size"]):
        global tracked_points

        # http://opencv-python-tutroals.readthedocs.io/en/latest/py_tutorials/py_imgproc/py_contours/py_contour_features/py_contour_features.html
        # https://stackoverflow.com/questions/32414559/opencv-contour-minimum-dimension-location-in-python
        out = self.frame.copy()
        # out = cv2.cvtColor(out, cv2.COLOR_GRAY2BGR)

        # out2 = np.zeros((512, 424,3), np.uint8)
        # cv2.add(out, out2)

        _im2, contours, _hier = cv2.findContours(
            self.frame, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

        # frame, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)
        # cv2.RETR_CCOMP,cv2.CHAIN_APPROX_SIMPLE

        rects = []
        detections = []
        for i, cnt in enumerate(contours):
            # compute the bounding box for the contour
            (x, y, w, h) = cv2.boundingRect(cnt)
            # reject contours outside size range
            if w > max_blob_size or w < min_blob_size or h > max_blob_size or h < min_blob_size:
                continue
            rects.append((x, y, w, h))
            detections.append((x, y, x + w, y + h, 1))
            cv2.rectangle(out, (x, y), (x + w, y + h), (255, 0, 0), 2)
        try:
            detections = self.sort_tracker.update(np.array(detections))

            new_tracked_points = {}

            for x1, y1, x2, y2, walker_id in detections:
                w_id = str(int(walker_id))
                x = int((x2 + x1) / 2)
                y = int((y2 + y1) / 2)
                new_tracked_points[w_id] = [x, y2]
                cv2.circle(out, (x, int(y2)), 5, (0, 0, 255), -1)
                cv2.putText(out, w_id, (x, y), self.font, 1,
                            (128, 128, 0), 1, cv2.LINE_AA)

            tracked_points = new_tracked_points

        except Exception as e:
            print(e)
            print(traceback.format_exc())
        return out

    async def get_jpeg_bytes(self, display_mode):
        if display_mode == 0:
            displayed_frame = self.blobs
        elif display_mode == 1:
            displayed_frame = self.frame0
        elif display_mode == 2:
            displayed_frame = self.frame

        ret, jpeg = cv2.imencode('.jpg', displayed_frame)
        f = jpeg.tobytes()  # bytearray
        if ret:
            return b'--frame\r\nContent-Type: image/jpeg\r\n\r\n' + f + b'\r\n'

        # displayed_frame = np.hstack((depth_flip, blobs))


class Tracker:

    def blob_detection(self, frame):
        pass

    def clean_frame(self, frame):
        pass

    def improve_shapes(self, img, bg_substractor, morph_type):
        pass

    def bg_substract(self, img):
        pass

    def kinect_loop(self):
        pass

    def frame_streamer(self, response):
        pass


class Corpus:
    def __init(self, path):
        pass
    # def create_corpus(path):
