import cv2
import time
from video import VideoCaptureTreading

ip = '169.254.72.191'
video_path = f"http://{ip}:8080/stream/video.mjpeg"

def test(n_frames=50, width=640, height=480, async_=False):
    if async_:
        cap = VideoCaptureTreading(video_path)
    else:
        cap = cv2.VideoCapture(video_path)
    cap.set(cv2.CAP_PROP_FRAME_WIDTH, width)
    cap.set(cv2.CAP_PROP_FRAME_HEIGHT, height)
    if async_:
        cap.start()
    t0 = time.time()
    i = 0
    while i < n_frames:
        _, frame = cap.read()
        # cv2.imshow('Frame', frame)
        # cv2.waitKey(1) & 0xFF
        i += 1
    print('[i] Frames per second: {:.2f}, async={}'.format(n_frames / (time.time() - t0), async_))
    if async_:
        cap.stop()
    cv2.destroyAllWindows()


if __name__ == '__main__':
    test(n_frames=50, width=640, height=480, async_=False)
    test(n_frames=50, width=640, height=480, async_=True)

# class RaspiCam:
#     def __init__(self, video_path):
#         self.video_path = video_path
#         self.cap = cv2.VideoCapture(video_path)
#         # self.cap.set(cv2.CAP_PROP_FPS, 25)
#         self.frame_counter = 0
#         self.gray = None

#     def get_frame(self, get_depth=False, get_ir=False):

#         if not self.cap.isOpened():
#             print("reopen Video")

#         ret, frame = self.cap.read()
#         if ret:
#             self.frame_counter += 1
#             if self.frame_counter == self.cap.get(cv2.CAP_PROP_FRAME_COUNT):
#                 # If the last frame is reached, reset the capture and the frame_counter
#                 self.frame_counter = 0  # Or whatever as long as it is the same as next line
#                 self.cap = cv2.VideoCapture(self.video_path)
#                 # self.cap.set(cv2.CAP_PROP_FPS, 25)

#             self.gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
#         return self.gray, self.gray
#         # except Exception as e:
#         #     print(e)

#     def close(self):
#         self.cap.release()
