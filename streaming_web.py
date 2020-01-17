# streaming_web.py

import requests
from flask import Flask, render_template, Response, jsonify, request
from flask_cors import CORS

import face_recog

collectionId = 'collection_test'
headers = {'content-type': 'application/json'}


class CustomFlask(Flask):
    jinja_options = Flask.jinja_options.copy()
    jinja_options.update(dict(
        block_start_string='(%',
        block_end_string='%)',
        variable_start_string='((',
        variable_end_string='))',
        comment_start_string='(#',
        comment_end_string='#)',
    ))


app = CustomFlask(__name__)
cors = CORS(app)

faceObject = face_recog.FaceRecog()


@app.route('/')
def index():
    return render_template('index.html')


@app.route('/hello')
def hello():
    return "hello"


@app.route('/register')
def get_register():
    return render_template('register.html')


@app.route('/login')
def get_login():
    return render_template('login.html')


def gen(fr):
    while True:
        jpg_bytes = fr.get_jpg_bytes()
        yield (b'--frame\r\n'
               b'Content-Type: image/jpeg\r\n\r\n' + jpg_bytes + b'\r\n\r\n')


@app.route('/video_feed')
def video_feed():
    return Response(gen(faceObject), mimetype='multipart/x-mixed-replace; boundary=frame')


@app.route('/is_face_detected')
def face_detectd():
    return jsonify(is_face_detected=faceObject.face_detected)


@app.route('/auth/join', methods=['POST'])
def join():
    try:
        userJson = request.json['user']
        email = userJson['email']
        password = userJson['password']
        phone = userJson['phone']
        name = userJson['name']
        # 이미 가입된 얼굴인지 체크
        # print(faceObject.find_face_by_byte('collection_test'))
        # isMatch = faceObject.find_face_by_byte('collection_test')
        isMatch = None
        if isMatch is None:
            print("가입되지않은 회원")
            faceIds, faceMeta = faceObject.add_faces_to_collection(email, 'collection_test')
            response = requests.post('http://localhost:5001/api/v1/auth/join',
                                     json={"email": email, "password": password, "phone": phone, "name": name,
                                           "faceIds": faceIds, "lowAge": faceMeta['lowAge'],
                                           "highAge": faceMeta['highAge'], "gender": faceMeta['gender']},
                                     headers=headers)
            if (response.status_code == 200):
                return "ok", 200
            else:
                return "가입에 실패했습니다.", 400

        else:
            print("이미 등록된 회원")
            return "이미 등록되어있는 얼굴입니다.", 400
    except ValueError:
        print(ValueError)
        return '얼굴 인식을 올바르게 해주세요.', 400


if __name__ == '__main__':
    app.run(host='localhost', debug=True)
