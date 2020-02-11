# face_recog.py

import base64
import datetime
import os
import threading
import time

import boto3
boto3.setup_default_session(profile_name='face')

import cv2
import face_recognition
import numpy as np

import camera
import aws_rekog

customerCount = {}
# customerCountDataFrame = pd.DataFrame(index=['count', 'like', 'start_time', 'end_time'])
# print(customerCountDataFrame)
fail_reason = ['EXCEEDS_MAX_FACES', 'EXTREME_POSE', 'LOW_BRIGHTNESS', 'LOW_SHARPNESS', 'LOW_CONFIDENCE',
               'SMALL_BOUNDING_BOX', 'LOW_FACE_QUALITY']
session = boto3.Session(profile_name="face")
client = session.client('rekognition')
similarity = 0.4

class FaceRecog():

    def __init__(self):
        # Using OpenCV to capture from device 0. If you have trouble capturing
        # from a webcam, comment the line below out and use a video file
        # instead.
        self.camera = camera.VideoCamera(0)

        self.known_face_encodings = []
        self.known_face_names = []
        #
        # # Load sample pictures and learn how to recognize it.
        dirname = 'customers'
        files = os.listdir(dirname)
        for filename in files:
            name, ext = os.path.splitext(filename)
            name = name.split('_')[0]
            if ext == '.jpg' or ext == '.jpeg' or ext == '.png':
                self.known_face_names.append(name)
                pathname = os.path.join(dirname, filename)
                img = face_recognition.load_image_file(pathname)
                if len(face_recognition.face_encodings(img)) > 0:
                    face_encoding = face_recognition.face_encodings(img)[0]
                    self.known_face_encodings.append(face_encoding)
        print(self.known_face_names)
        # Initialize some variables
        self.face_locations = []
        self.face_encodings = []
        self.face_names = []
        self.process_this_frame = True
        self.face_detected = False
        # 좋아요 계산
        # self.cal_like()

    def __del__(self):
        del self.camera

    def release(self):
        cv2.destroyAllWindows()

    def get_frame(self):
        # Grab a single frame of video

        frame = self.camera.get_frame()
        # Resize frame of video to 1/4 size for faster face recognition processing
        small_frame = cv2.resize(frame, (0, 0), fx=0.25, fy=0.25)

        # Convert the image from BGR color (which OpenCV uses) to RGB color (which face_recognition uses)
        rgb_small_frame = small_frame[:, :, ::-1]

        # Only process every other frame of video to save time
        if self.process_this_frame:

            # Find all the faces and face encodings in the current frame of video
            self.face_locations = face_recognition.face_locations(rgb_small_frame)
            self.face_encodings = face_recognition.face_encodings(rgb_small_frame, self.face_locations)
            self.face_names = []
            for face_encoding in self.face_encodings:
                # See if the face is a match for the known face(s)
                distances = face_recognition.face_distance(self.known_face_encodings, face_encoding)
                if len(distances) > 0:
                    min_value = min(distances)
                    # tolerance: How much distance between faces to consider it a match. Lower is more strict.
                    # 0.6 is typical best performance.
                    name = "NOT CUSTOMER"
                    if min_value < similarity:
                        index = np.argmin(distances)
                        name = self.known_face_names[index]
                        if name in customerCount:
                            customerCount[name]['count'] = customerCount[name]['count'] + 1
                            customerCount[name]['last_time'] = self.now()

                        else:
                            customerCount[name] = {'count': 0, 'like': 0, 'start_time': self.now(),
                                                   'last_time': self.now()}

                    # print("유사성 : " + str(min_value))
                    # print("현재 초 : " + str(time.localtime().tm_sec))
                    # print("카운트 :" + str(customerCountDataFrame[name]['count']))
                    # end = time.time()
                    # process_time = time.time() - start

                    self.face_names.append(name)

            # print(process_time)

        self.process_this_frame = not self.process_this_frame

        # Display the results
        if len(self.face_names) > 0:
            for (top, right, bottom, left), name in zip(self.face_locations, self.face_names):
                # Scale back up face locations since the frame we detected in was scaled to 1/4 size
                top *= 4
                right *= 4
                bottom *= 4
                left *= 4

                # Draw a box around the face
                cv2.rectangle(frame, (left, top), (right, bottom), (0, 0, 255), 2)

                # Draw a label with a name below the face
                cv2.rectangle(frame, (left, bottom), (right, bottom), (0, 0, 255), cv2.FILLED)
                font = cv2.FONT_HERSHEY_DUPLEX
                cv2.putText(frame, name, (left + 6, bottom - 6), font, 2.0, (255, 255, 255), 2)
        else:
            for (top, right, bottom, left) in self.face_locations:
                # Scale back up face locations since the frame we detected in was scaled to 1/4 size
                top *= 4
                right *= 4
                bottom *= 4
                left *= 4

                # Draw a box around the face
                cv2.rectangle(frame, (left, top), (right, bottom), (0, 0, 255), 2)

                # # Draw a label with a name below the face
                # cv2.rectangle(frame, (left, bottom), (right, bottom), (0, 0, 255), cv2.FILLED)
                # font = cv2.FONT_HERSHEY_DUPLEX
                # cv2.putText(frame, name, (left + 6, bottom - 6), font, 2.0, (255, 255, 255), 2)

        return frame

    def get_jpg_bytes(self):
        frame = self.get_frame()
        # We are using Motion JPEG, but OpenCV defaults to capture raw images,
        # so we must encode it into JPEG in order to correctly display the
        # video stream.
        ret, jpg = cv2.imencode('.jpg', frame)
        return jpg.tobytes()

    def picture_shot_for_join(self, username):
        self.camera.picture_shot(username)

    def get_64_frame(self):
        frame = self.camera.get_frame()
        return base64.b64encode(frame)

    def add_faces_to_collection(self, email, collection_id):
        count = 0
        process = []
        faceIds = []
        result = {}
        while count < 3:
            time.sleep(1)
            tempFrame = self.camera.get_frame()
            response = aws_rekog.add_face_to_collection(collection_id,self.get_jpg_bytes())
            if len(response['UnindexedFaces']) > 0:
                for unindexedFace in response['UnindexedFaces']:
                    if len(unindexedFace['Reasons']) > 0:
                        print(unindexedFace['Reasons'], None)
            elif len(response['FaceRecords']) > 0:
                for faceRecord in response['FaceRecords']:
                    faceId = faceRecord['Face']['FaceId']
                    faceIds.append(faceId)
                    faceQuality = faceRecord['FaceDetail']['Quality']
                    print('  Face ID: ' + faceRecord['Face']['FaceId'])
                    print(faceRecord['FaceDetail']['Quality'])
                    process.append([tempFrame, faceQuality['Sharpness'], faceId])
            else:
                print("NO_FACE_ERROR", None)
            count += 1

        # 가장 정확한 얼굴로 사진 캡쳐
        # max(process, key=lambda x: x[1])
        (pictureFrame, sharpness, faeId) = max(process, key=lambda x: x[1])
        print("가장 정확한 얼굴 모양 데이터 : {}".format(max(process, key=lambda x: x[1])))
        ret, jpg = cv2.imencode('.jpg', pictureFrame)
        faceMeta = self.detect_face(jpg.tobytes())
        result['faceIds'] = faceIds
        result['faceMeta'] = faceMeta
        result['faceImageUrl'] = []
        for idx, (pictureFrame, sharpness, faceId) in enumerate(process):
            result['faceImageUrl'].append(self.camera.picture_shot(str(email) + "_" + str(idx) + ".jpg",pictureFrame,s3=True))
        return result

    def find_face_by_byte(self, collection_id):
        faceIds = []
        response = client.search_faces_by_image(CollectionId=collection_id,
                                                # Image={'Bytes': self.get_jpg_bytes()},
                                                Image={'Bytes': self.get_jpg_bytes()},
                                                FaceMatchThreshold=70,
                                                MaxFaces=1)

        faceMatches = response['FaceMatches']
        if not faceMatches:
            print("not match face")
            return None

        for match in faceMatches:
            print('FaceId:' + match['Face']['FaceId'])
            print('Similarity: ' + "{:.2f}".format(match['Similarity']) + "%")
            faceIds.append(match['Face']['FaceId'])
            # return match['Face']['FaceId']
        return faceIds

    def detect_face(self, byte):
        response = client.detect_faces(Image={'Bytes': byte}, Attributes=['ALL'])
        for faceDetail in response['FaceDetails']:
            lowAge = faceDetail['AgeRange']['Low']
            highAge = faceDetail['AgeRange']['High']
            gender = faceDetail['Gender']['Value']
            return {'lowAge': lowAge, 'highAge': highAge, 'gender': gender}

    def now(self):
        return datetime.datetime.now().strftime("%y/%m/%d, %H:%M:%S")

    def cal_like(self):
        for email in customerCount:
            count = customerCount[email]['count']
            # 140 이하일 시 무시
            if count is not None and count > 140:
                customerCount[email]['like'] += count / 420
                # 좋아요의 숫자는 머물었던 분
        threading.Timer(60, self.cal_like).start()

    def login(self):
        faceIds = self.find_face_by_byte('collection_test')


if __name__ == '__main__':
    face_recog = FaceRecog()
    while True:
        frame = face_recog.get_frame()
        # show the frame
        cv2.imshow("Frame", frame)
        key = cv2.waitKey(1) & 0xFF

        # if the `q` key was pressed, break from the loop
        if key == ord("q"):
            break

    # do a bit of cleanup
    cv2.destroyAllWindows()
