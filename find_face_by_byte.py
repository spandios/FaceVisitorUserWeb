def find_face_by_byte(collectionId, byte):
    response = client.search_faces_by_image(CollectionId=collectionId,
                                            Image={'Bytes': byte},
                                            FaceMatchThreshold=threshold,
                                            MaxFaces=1)
    faceMatches = response['FaceMatches']
    print('Matching faces')
    for match in faceMatches:
        print('FaceId:' + match['Face']['FaceId'])
        print('Similarity: ' + "{:.2f}".format(match['Similarity']) + "%")
