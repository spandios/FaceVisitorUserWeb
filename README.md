


![](https://facevisitor-bucket2.s3.ap-northeast-2.amazonaws.com/logo-facevisiter%402x.png)
<br>

페이스 비지터는 얼굴인식을 이용한 매장 고객관리 시스템입니다.
#  



# FaceVisitor User Web Server 
Python Flask 기반 웹 서버 + Vue 

## Features
- 고객의 얼굴인식을 통한 빠른 **가입 및 로그인**
- 어떤 상품섹션에 고객이 일정시간 동안 얼굴인식이 된다면(머문다면), 그 상품에 관심이 있는 것으로 간주하여 **선호도 점수** 추가. 
- 선호도 데이터를 SVD 알고리즘을 이용해 훈련된 결과를 기반으로, 협업 필터링 추천시스템을 통해 **상품을 추천**
- QR코드를 통한 **셀프결제**


## DEMO
![Alt Text](https://facevisitor-bucket2.s3.ap-northeast-2.amazonaws.com/ezgif.com-resize+(1).gif)


## DB
<img src="https://facevisitor-bucket2.s3.ap-northeast-2.amazonaws.com/MySQL+for+5.png" width="1000%"></img>
<br>
AWS RDS MYSQL 5.7

## POSTMAN API DOCS
https://documenter.getpostman.com/view/2047162/SzKVSyMa

## API Production HOST URL
http://api.facevisitor.co.kr

