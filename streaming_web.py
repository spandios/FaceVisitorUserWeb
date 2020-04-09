# streaming_web.py

import requests
from flask import Flask, render_template, Response, jsonify, request
from flask_cors import CORS

import aws_personalize as personalize
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


def make_error(status_code, sub_code, message, action):
    response = jsonify({
        'status': status_code,
        'sub_code': sub_code,
        'message': message,
        'action': action
    })
    response.status_code = status_code
    return response


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


@app.route('/login', methods=['POST'])
def post_login():
    try:
        faceId = faceObject.find_face_by_byte(collectionId)
        if len(faceId) > 0:
            loginResponse = requests.post('http://localhost:5001/api/v1/auth/login', json={"faceId": faceId},
                                          headers=headers)

            if loginResponse.status_code is 200:
                return loginResponse.json()
        else:
            return "얼굴을 인식하지 못했습니다", 400
    except Exception as e:
        return e, 500

#
# def login():
#


def gen(fr):
    while True:
        jpg_bytes = fr.get_jpg_bytes()
        yield (b'--frame\r\n'
               b'Content-Type: image/jpeg\r\n\r\n' + jpg_bytes + b'\r\n\r\n')


@app.route('/video_feed')
def video_feed():
    return Response(gen(faceObject), mimetype='multipart/x-mixed-replace; boundary=frame')


@app.route('/main')
def get_main():
    return render_template('main.html')


@app.route('/goods/<goods_id>')
def get_goods_detail(goods_id):
    return render_template('goods_detail.html', goods_id=goods_id)


@app.route('/self_pay')
def get_self_pay():
    return render_template('self_pay.html')


@app.route('/direct_pay/<goods_id>')
def get_direct_self_pay(goods_id):
    return render_template('direct_pay.html',goods_id=goods_id)


@app.route('/order/complete/<order_id>')
def get_pay_complete(order_id):
    return render_template('pay_complete.html', order_id=order_id)

@app.route('/cart')
def get_cart():
    return render_template('cart.html')


@app.route('/is_face_detected')
def face_detectd():
    return jsonify(is_face_detected=faceObject.face_detected)


@app.route('/is_user')
def is_user():
    try:
        response = faceObject.find_face_by_byte(collectionId)
        result = response is not None
        if result is True:
            if len(response) > 0:
                loginResponse = requests.post('http://localhost:5001/api/v1/auth/direct_login',
                                              json={"faceId": response},
                                              headers=headers)
                if loginResponse.status_code is 200:
                    return loginResponse.json()
                else:
                    return "요청 중 문제가 있습니다.", 400
            else:
                return "요청 중 문제가 있습니다.", 400
        else:
            return "false", 200
    except Exception as e:
        print(e)
        return "서버에 오류가 있습니다.", 400


@app.route('/personalize/<user_id>', methods=['GET'])
def get_personalize(user_id):
    return jsonify(personalize.getRecommendationByWebEvent(user_id))


@app.route('/join', methods=['POST'])
def join():
    try:
        userJson = request.json['user']
        email = userJson['email']
        password = userJson['password']
        phone = userJson['phone']
        name = userJson['name']
        # 이미 가입된 얼굴인지 체크
        # print(faceObject.find_face_by_byte('collection_test'))
        isMatch = faceObject.find_face_by_byte('collection_test')
        if isMatch is not None:
            return "이미 등록된 얼굴입니다. 로그인을 해주세요", 400

        response = requests.post('http://localhost:5001/api/v1/user/exist', json={"email": email}, headers=headers)
        exist = response.json()
        if exist:
            return "이미 가입된 이메일입니다.", 400

        #  isMatch = None
        if isMatch is None and exist is False:
            print("가입되지않은 회원")
            result = faceObject.add_faces_to_collection(email, 'collection_test')
            print(result)

            response = requests.post('http://localhost:5001/api/v1/auth/join',
                                     json={"email": email, "password": password, "phone": phone, "name": name,
                                           "faceIds": result['faceIds'], "lowAge": result['faceMeta']['lowAge'],
                                           "highAge": result['faceMeta']['highAge'],
                                           "gender": result['faceMeta']['gender'],
                                           "faceImageUrl": result['faceImageUrl']},
                                     headers=headers)
            if (response.status_code == 200):
                return "ok", 200
            else:
                return "가입에 실패했습니다.", 400

        else:
            print("이미 등록된 회원")
            return "이미 등록되어있는 얼굴입니다.", 400
    except Exception as err:
        print(err)
        return '가입에 실패했습니다. 다시 시도해주세요.', 500


if __name__ == '__main__':
    app.run(host='localhost', debug=True)
