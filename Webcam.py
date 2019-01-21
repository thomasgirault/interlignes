import cv2


class RaspiCam:
    def __init__(self, video_path):
        self.video_path = video_path
        self.cap = cv2.VideoCapture(video_path)
        # self.cap.set(cv2.CAP_PROP_FPS, 25)
        self.frame_counter = 0
        self.gray = None

    def get_frame(self, get_depth=False, get_ir=False):

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
