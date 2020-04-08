import datetime
import json

import boto3

boto3.setup_default_session(profile_name='face')
session = boto3.Session(profile_name="face")
client = session.client('personalize-events')
personalize = session.client('personalize')
personalizeRuntime = session.client('personalize-runtime')


def trackingViewEvent(userId, itemId):
    client.put_events(
        trackingId='872bda53-fe70-4761-8704-69d357e47efa',
        userId=userId,
        sessionId='session1',
        eventList=[{
            'eventId': 'event1',
            'sentAt': datetime.datetime.now().timestamp(),
            'eventType': 'view',
            'properties': json.dumps({
                'itemId': itemId,
                'eventValue': 2,
            })
        }]
    )


def trackingCartEvent(userId, itemId):
    client.put_events(
        trackingId='872bda53-fe70-4761-8704-69d357e47efa',
        userId=userId,
        sessionId='session1',
        eventList=[{
            'eventId': 'event2',
            'sentAt': datetime.datetime.now().timestamp(),
            'eventType': 'cart',
            'properties': json.dumps({
                'itemId': itemId,
                'eventValue': 5,
            })
        }]
    )


def trackingOrderEvent(userId, itemId):
    client.put_events(
        trackingId='872bda53-fe70-4761-8704-69d357e47efa',
        userId=userId,
        sessionId='session1',
        eventList=[{
            'eventId': 'event3',
            'sentAt': datetime.datetime.now().timestamp(),
            'eventType': 'order',
            'properties': json.dumps({
                'itemId': itemId,
                'eventValue': 10,
            })
        }]
    )


def getRecommendationByWebEvent(userId):
    response = personalizeRuntime.get_recommendations(
        campaignArn='arn:aws:personalize:ap-northeast-2:007731194585:campaign/MyFaceVisitorCampaign',
        userId=str(userId))

    print("Recommended items")
    for item in response['itemList']:
        print(item['itemId'])
    return response


def getRecommendationByFaceEvent():
    response = personalizeRuntime.get_recommendations(
        campaignArn='Campaign ARN',
        userId='User ID')

    print("Recommended items")
    for item in response['itemList']:
        print(item['itemId'])


if __name__ == '__main__':
    getRecommendationByWebEvent(1)
