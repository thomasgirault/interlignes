import os
import cv2
import numpy as np
from conf import VARS
import bgs


class BGSubstractor:
    """Wrapper for OpenCv BG Substractor"""

    def __init__(self, name, bg_mask_path="/home/thomas/dev/Interlignes/interlignes/"):
        self.mask_path = f"{bg_mask_path}/{name}.jpg"
        self.init = False

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

    def save(self, bg_mask):
        self.bg_mask = bg_mask
        _ = self.apply(self.bg_mask, lr=1)
        cv2.imwrite(self.mask_path, self.bg_mask)


class BGSWrapper:
    def __init__(self):
        self.algo_a = bgs.CodeBook()
        self.algo_b = bgs.CodeBook()
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

class Frame:

    def __init__(self, frame):
        self.frame = frame

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

    def bg_substract(self):
        pass

    def blur(self, blur=VARS["blur"]):
        if blur:
            self.frame = cv2.blur(self.frame, (blur, blur))

    def clean(self, mask, morph_type=cv2.MORPH_OPEN, kernel_size=VARS["erode_kernel_size"], iterations=VARS["erode_iterations"]):

        kernel = np.ones((kernel_size, kernel_size), np.uint8)
        mask_dilate = cv2.morphologyEx(
            mask, morph_type, kernel, iterations)
        # img_mask_dilate = cv2.bitwise_and(self.frame, mask_dilate)
        return mask_dilate
        # depth = cv2.fastNlMeansDenoising(depth, None, 9, 13)
        # depth = cv2.GaussianBlur(depth, cv2.BLUR_KERNEL_SIZE, 3)

    def save(self):
        pass

    def to_jpeg(self):
        ret, jpeg = cv2.imencode('.jpg', self.frame)
        f = jpeg.tobytes()
        if ret:
            return b'--frame\r\nContent-Type: image/jpeg\r\n\r\n' + bytearray(f) + b'\r\n'


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
