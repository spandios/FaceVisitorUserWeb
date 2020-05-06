# camera.py

import os

import boto3
import cv2

imagePath = 'customers'
fail_reason = ['EXCEEDS_MAX_FACES', 'EXTREME_POSE', 'LOW_BRIGHTNESS', 'LOW_SHARPNESS', 'LOW_CONFIDENCE',
               'SMALL_BOUNDING_BOX', 'LOW_FACE_QUALITY']
client = boto3.client('rekognition')
import aws_s3

class VideoCamera(object):
    def __init__(self, videoNum):
        self.video = cv2.VideoCapture(videoNum)
        self.frame_rate = self.video.get(5)

    def __del__(self):
        self.video.release()

    def get_frame(self):
        # Grab a single frame of video
        ret, frame = self.video.read()
        return frame

    def get_frame_id(self):
        self.video.get(1)

    def get_second_frame(self):
        return self.get_frame_id() == self.frame_rate

    def picture_shot(self, username, fr, s3=False):
        cv2.imwrite(os.path.join(imagePath, username), fr)
        if s3:
            return aws_s3.upload_file(os.path.join(imagePath, username), "facevisitor-bucket2")

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
