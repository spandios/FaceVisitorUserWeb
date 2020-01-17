# camera.py

import os

import boto3
import cv2

imagePath = 'customers'
fail_reason = ['EXCEEDS_MAX_FACES', 'EXTREME_POSE', 'LOW_BRIGHTNESS', 'LOW_SHARPNESS', 'LOW_CONFIDENCE',
               'SMALL_BOUNDING_BOX', 'LOW_FACE_QUALITY']
client = boto3.client('rekognition')


class VideoCamera(object):
    def __init__(self, videoNum):
        self.video = cv2.VideoCapture(videoNum)

    def __del__(self):
        self.video.release()

    def get_frame(self):
        # Grab a single frame of video
        ret, frame = self.video.read()
        return frame

    def picture_shot(self, username, fr):
        cv2.imwrite(os.path.join(imagePath, username), fr)

# if __name__ == '__main__':
#     cam = VideoCamera()
#     while True:
#         frame = cam.get_frame()
#
#         # show the frame
#         cv2.imshow("Frame", frame)
#         key = cv2.waitKey(1) & 0xFF
#
#         # if the `q` key was pressed, break from the loop
#         if key == ord("q"):
#             break
#
#     # do a bit of cleanup
#     cv2.destroyAllWindows()
#     print('finish')
