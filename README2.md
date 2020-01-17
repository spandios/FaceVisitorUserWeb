# Face Visitor

Face Visitor 고객용

* camera.py - webcam
* face_recog.py - 웹캠 프레임안에 얼굴을 분석합니다.
* streaming_web.py - http://IP_addr:5000/으로 웹 서버를 엽니다.

All 3 files are runnable like this:
```
$ python3 camera.py
$ python3 face_recog.py
$ python3 live_streaming.py
```

Put picture with one person's face in `knowns` directory. 
Change the file name as the person's name like: `john.jpg` or `jane.jpg`. Then run `python face_recog.py`. Or `python live_streaming.py` to send video over network.

Visit [https://ukayzm.github.io/python-face-recognition/](https://ukayzm.github.io/python-face-recognition/) for more information.
