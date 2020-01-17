import boto3

if __name__ == "__main__":
    collectionId = 'collection-test'
    photo = 'knowns/me.jpeg'
    threshold = 70
    maxFaces = 2
    client = boto3.client('rekognition')
    with open(photo, 'rb') as image:
        response = client.search_faces_by_image(CollectionId=collectionId,
                                                Image={'Bytes': image.read()},
                                                FaceMatchThreshold=threshold,
                                                MaxFaces=maxFaces)
        faceMatches = response['FaceMatches']
        print('Matching faces')
        for match in faceMatches:
            print('FaceId:' + match['Face']['FaceId'])
            print('Similarity: ' + "{:.2f}".format(match['Similarity']) + "%")
            print
