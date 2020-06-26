# main.py
import atexit
import json

import requests
from apscheduler.schedulers.background import BackgroundScheduler
from flask import Flask, render_template, Response, jsonify, request
from flask_cors import CORS

from Face import Face
from Recommend import Recommend

collectionId = 'collection_test'
headers = {'content-type': 'application/json'}

# url = "http://localhost:5001"
url = "http://api.facevisitor.co.kr"


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

faceObject = Face()
recommend = Recommend()


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


@app.route('/login_test')
def get_loin_test():
    return render_template('login_test.html')


@app.route('/login', methods=['POST'])
def post_login():
    try:
        faceId = faceObject.find_face_by_byte(collectionId)
        if len(faceId) > 0:
            loginResponse = requests.post(url + '/api/v1/auth/login', json={"faceId": faceId},
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


def gen(fr, is_test=False):
    while True:
        if is_test:
            jpg_bytes = fr.get_jpg_bytes_test()
        else:
            jpg_bytes = fr.get_jpg_bytes()
        yield (b'--frame\r\n'
               b'Content-Type: image/jpeg\r\n\r\n' + jpg_bytes + b'\r\n\r\n')


@app.route('/video_feed')
def video_feed():
    return Response(gen(faceObject), mimetype='multipart/x-mixed-replace; boundary=frame')


@app.route('/video_count')
def video_count():
    return Response(gen(faceObject, is_test=True), mimetype='multipart/x-mixed-replace; boundary=frame')


@app.route('/count_test')
def video_feed_test_template():
    return render_template('count_test.html')


@app.route('/main')
def get_main():
    return render_template('main.html')


@app.route('/goods/all')
def get_goods_all():
    return render_template('goods_all.html')


@app.route('/goods/<goods_id>')
def get_goods_detail(goods_id):
    return render_template('goods_detail.html', goods_id=goods_id)


@app.route('/self_pay')
def get_self_pay():
    return render_template('self_pay.html')


@app.route('/recommend/<user_id>/<item_id>/<type>')
def add_interaction(user_id, item_id, type):
    user_id = int(user_id)
    item_id = int(item_id)
    recommend.add_interaction(user_id, item_id, type)
    print("interaction subscribe user id : {} item id : {} type : {}".format(user_id, item_id, type))
    return "true", 200


@app.route('/recommend/<user_id>')
def get_recommend(user_id):
    user_id = int(user_id)
    recommend_goods_id = recommend.get_recommend_by_user_id(user_id)

    if not recommend_goods_id:
        print("empty recommend")
        popResponse = requests.get(url + '/api/v1/goods/pop', headers=headers)

        return app.response_class(
            response=json.dumps(popResponse.json()),
            status=200,
            mimetype='application/json'
        )
    else:
        print("recommend exist")
        recommend_response = requests.post(url + '/api/v1/goods/getGoods',
                                           json={"goodsIds": recommend_goods_id, "userId": user_id},
                                           headers=headers)

        recommend_result = recommend_response.json()
        face_response = requests.get(url + "/api/v1/user/{}/face".format(user_id), headers=headers)
        if face_response.status_code == 200:
            faceMeta = face_response.json()
            if (faceMeta != None):
                gender = faceMeta['gender']
                lowAge = faceMeta['lowAge']
                highAge = faceMeta['highAge']
                print(lowAge, highAge)
                age = str((lowAge + highAge + 10) // 2)
                ageFormat = age[:-1] + "0"
                print("유저의 성별 : " + gender)
                print("유저의 나이대 : " + ageFormat)
                print('기본 추천 상품 점수\n')
                for index in range(len(recommend_result)):
                    goods = recommend_result[index]
                    goods['score'] = (len(recommend_result) - 1) - index
                    print("goods id : {} ,  score : {} \n".format(goods['id'], goods['score']))
                    if goods['gender'] == gender:
                        goods['score'] = goods['score'] + 0.6
                    if goods['age'] == ageFormat:
                        goods['score'] = goods['score'] + 0.6

                # for goods in recommend_result:
                #     print("성 나이 계산 후 추천 상품 점수 goods id : {} ,  score : {}".format(goods['id'], goods['score']))

                recommend_result.sort(key=lambda x: x['score'], reverse=True)
        print("\n\n")
        print("----최종 추천 상품 점수 ----")
        for goods in recommend_result:
            print("goods id : {} ,  score : {}\n".format(goods['id'], goods['score']))

        if 0 < len(recommend_goods_id) < 4:
            print("recommend + pop")
            popResponse = requests.get(url + '/api/v1/goods/pop', headers=headers)
            pop_result = popResponse.json()
            recommend_result.extend(pop_result)

        response = app.response_class(
            response=json.dumps(recommend_result),
            status=200,
            mimetype='application/json'
        )

        return response


@app.route('/recommend/pop')
def get_popularity():
    loginResponse = requests.post(url + '/api/v1/goods/getGoods',
                                  json={"goodsIds": recommend.get_popularity_item_id()}, headers=headers)
    response = app.response_class(
        response=json.dumps(loginResponse.json()),
        status=200,
        mimetype='application/json'
    )
    return response


@app.route('/direct_pay/<goods_id>')
def get_direct_self_pay(goods_id):
    return render_template('direct_pay.html', goods_id=goods_id)


@app.route('/order')
def get_order_page():
    return render_template('order_page.html')


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
                loginResponse = requests.post(url + '/api/v1/auth/direct_login',
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
        return "서버에 오류가 있습니다.", 500


# @app.route('/personalize/<user_id>', methods=['GET'])
# def get_personalize(user_id):
#     return jsonify(personalize.getRecommendationByWebEvent(user_id))


@app.route('/join', methods=['POST'])
def join():
    try:
        userJson = request.json['user']
        email = userJson['email']
        password = userJson['password']
        phone = userJson['phone']
        name = userJson['name']
        storeId = userJson['storeId']
        print(storeId)
        # 이미 가입된 얼굴인지 체크
        # print(faceObject.find_face_by_byte('collection_test'))
        # isMatch = faceObject.find_face_by_byte('collection_test')
        #
        # if isMatch is not None:
        #     return "이미 등록된 얼굴입니다. 로그인을 해주세요", 400

        response = requests.post(url + '/api/v1/user/exist', json={"email": email},
                                 headers=headers)
        exist = response.json()
        if exist:
            return "이미 가입된 이메일입니다.", 400

        #  isMatch = None
        if exist is False:
            print("가입되지않은 회원")
            result = faceObject.add_faces_to_collection(email, 'collection_test')
            print(result)

            response = requests.post(url + '/api/v1/auth/join',
                                     json={"email": email, "password": password, "phone": phone, "name": name,
                                           "storeId": storeId,
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
    # every 3 hours re-train user interaction model(face_interaction.csv)
    scheduler = BackgroundScheduler()
    scheduler.add_job(func=recommend.train, trigger="interval", seconds=60 * 60 * 3)
    # every 1 seconds tracking user face
    scheduler.add_job(func=faceObject.facePreference, trigger="interval", seconds=1)
    scheduler.start()
    # Shut down the scheduler when exiting the app
    atexit.register(lambda: scheduler.shutdown())
    app.run(debug=False)
