import logging

import boto3
from botocore.exceptions import ClientError

boto3.setup_default_session(profile_name='face')

s3 = boto3.resource('s3')


def checkBucket():
    for bucket in s3.buckets.all():
        print(bucket.name)


def upload_file(file_name, bucket, object_name=None):
    boto3.setup_default_session(profile_name='face')
    # If S3 object_name was not specified, use file_name
    if object_name is None:
        object_name = file_name

    # Upload the file
    s3_client = boto3.client('s3')

    try:
        response = s3_client.upload_file(file_name, bucket, object_name,ExtraArgs={'ACL': 'public-read'})
        return "https://facevisitor-bucket2.s3.ap-northeast-2.amazonaws.com/" + object_name

    except ClientError as e:
        logging.error(e)
        return False
    return True



if __name__ == '__main__':
    checkBucket()
    # resposne = upload_file('customers/awe_0_2020-01-21 20:40:24.969938.jpg', 'facevisitor-bucket')
    # print(resposne)

