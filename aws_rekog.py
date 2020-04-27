import boto3
from botocore.exceptions import ClientError

boto3.setup_default_session(profile_name='face')
session = boto3.Session(profile_name="face")
client = session.client('rekognition')


def find_face_by_frame(collection_id, frame):
    response = client.search_faces_by_image(CollectionId=collection_id,
                                            # Image={'Bytes': self.get_jpg_bytes()},
                                            Image={'Bytes': frame},
                                            FaceMatchThreshold=70,
                                            MaxFaces=1)
    faceMatches = response['FaceMatches']
    if not faceMatches:
        print("not match face")
        return None

    for match in faceMatches:
        print('FaceId:' + match['Face']['FaceId'])
        print('Similarity: ' + "{:.2f}".format(match['Similarity']) + "%")
        return match['Face']['FaceId']


def add_face_to_collection(collection_id, frame):
    response = client.index_faces(CollectionId=collection_id,
                                  Image={'Bytes': frame},
                                  MaxFaces=1,
                                  QualityFilter="HIGH",
                                  DetectionAttributes=['ALL'])
    return response


def list_faces_in_collection(collection_id):
    maxResults = 100
    faces_count = 0
    tokens = True

    response = client.list_faces(CollectionId=collection_id,
                                 MaxResults=maxResults)
    faceIds = []
    print('Faces in collection ' + collection_id)

    while tokens:

        faces = response['Faces']

        for face in faces:
            faceIds.append(face['FaceId'])
            faces_count += 1
        if 'NextToken' in response:
            nextToken = response['NextToken']
            response = client.list_faces(CollectionId=collection_id,
                                         NextToken=nextToken, MaxResults=maxResults)
        else:
            tokens = False

    return faceIds


def delete_collection(collection_id):
    print('Attempting to delete collection ' + collection_id)
    client = boto3.client('rekognition')
    status_code = 0
    try:
        response = client.delete_collection(CollectionId=collection_id)
        status_code = response['StatusCode']

    except ClientError as e:
        if e.response['Error']['Code'] == 'ResourceNotFoundException':
            print('The collection ' + collection_id + ' was not found ')
        else:
            print('Error other than Not Found occurred: ' + e.response['Error']['Message'])
        status_code = e.response['ResponseMetadata']['HTTPStatusCode']
    return (status_code)


def deleteFaceById(faceId):
    response = client.delete_faces(
        CollectionId='collection_test',
        FaceIds=[
            faceId,
        ],
    )
    print(response)


def deleteAllFace():
    collection_id = 'collection_test'
    faceIds = list_faces_in_collection(collection_id)

    for faceId in faceIds:
        # if faceId is '27e6ac47-4b03-4ec2-80c5-6b56d6caad7b' or faceId is '47114780-5e37-4b03-9c4d-49158fc2e9a8' or faceId is 'f6c1cd9b-585e-4221-98fb-45952325954d':
        #     break
        deleteFaceById(faceId)


if __name__ == "__main__":
    # print(list_faces_in_collection('collection_test'))
    deleteAllFace()
