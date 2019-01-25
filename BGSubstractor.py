import os
import cv2
import bgs
from conf import VARS


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


class MogSubstractor:
    """Wrapper for OpenCv BG Substractor"""

    def __init__(self, name, bg_mask_path="/home/thomas/dev/Interlignes/interlignes/"):
        self.mask_path = f"{bg_mask_path}/{name}.jpg"
        self.init = False
        self.blur_kernel_size = None

        # self.bg_substractor = cv2.createBackgroundSubtractorMOG2(
        #     history=1, detectShadows=False, varThreshold=8)
        self.bg_substractor = cv2.createBackgroundSubtractorMOG2(
            history=1, detectShadows=True, varThreshold=8)


        if os.path.exists(self.mask_path):
            self.bg_mask = cv2.imread(self.mask_path, cv2.IMREAD_GRAYSCALE)
            _ = self.apply(self.bg_mask, lr=1)
            self.init = True

        # self.algo = None
        # TODO répliquer ce comportement sur la librairie BGS
        # Prendre 10 secondes pour apprendre le masque sur une frame
        # Ou faire apprendre le masque toutes les X frames (paramétrable)

    def blur(self, frame):
        # TODO : appliquer le blur sur l'image de référence
        if self.blur_kernel_size:
            return cv2.blur(frame, (self.blur_kernel_size, self.blur_kernel_size))
        else:
            return frame

    def apply(self, frame, lr=VARS["learnBG"]):
        """acquisition et sauvegarde d'un masque
           http://docs.opencv.org/3.0-beta/doc/py_tutorials/py_imgproc/py_morphological_ops/py_morphological_ops.html
        """
        if VARS["blur"] != self.blur_kernel_size:  # UPDATE MASK BLUR
            self.blur_kernel_size = VARS["blur"]
            blured = self.blur(self.bg_mask)
            _ = self.substract(blured, lr=1)

        blured = self.blur(frame)
        return self.substract(blured, lr)
        # return cv2.bitwise_and(frame, mask)

    def substract(self, frame, lr):
        return self.bg_substractor.apply(frame, learningRate=lr)

    def save(self, frame):
        self.bg_mask = frame
        _ = self.apply(self.bg_mask, lr=1)
        cv2.imwrite(self.mask_path, self.bg_mask)


class SimpleSubstractor(MogSubstractor):
    def substract(self, frame, lr):
        frameDelta = cv2.absdiff(self.bg_mask, frame)
        return cv2.threshold(frameDelta, 5, 255, cv2.THRESH_BINARY)[1]


class BGSWrapper:
    def __init__(self, name):
        # self.algo_b = bgs.CodeBook()
        self.nb_frames = 0
        self.init = True
        self.algo_a = bgs.CodeBook()
        # self.algo_a = bgs.LBFuzzyGaussian()

        # bgs.LBSimpleGaussian() #
        # bg_algo = bgs.LBFuzzyGaussian()

    def apply(self, frame, lr=VARS["learnBG"]):
        return self.algo_a.apply(frame)  # or frame

    def save(self, bg_mask):
        pass


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
