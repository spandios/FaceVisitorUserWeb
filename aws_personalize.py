import datetime
import json

import boto3

boto3.setup_default_session(profile_name='face')
session = boto3.Session(profile_name="face")
client = session.client('personalize-events')
personalize = session.client('personalize')
personalizeRuntime = session.client('personalize-runtime')
trackingId = '872bda53-fe70-4761-8704-69d357e47efa'


def trackingViewEvent(userId, itemId):
    events = client.put_events(trackingId=trackingId, userId=str(userId),
                               sessionId='session1',
                               eventList=[{'eventId': 'event1', 'sentAt': datetime.datetime.now().timestamp(),
                                           'eventType': 'VIEW',
                                           'properties': json.dumps(
                                               {'itemId': str(itemId), 'eventValue': 2})}])
    print(events)


def trackingLikeEvent(userId, itemId):
    events = client.put_events(trackingId=trackingId, userId=str(userId),
                               sessionId='session1',
                               eventList=[{'eventId': 'event1', 'sentAt': datetime.datetime.now().timestamp(),
                                           'eventType': 'LIKE',
                                           'properties': json.dumps(
                                               {'itemId': str(itemId), 'eventValue': 4})}])
    print(events)
    return events


def trackingDisLikeEvent(userId, itemId):
    events = client.put_events(trackingId=trackingId, userId=str(userId),
                               sessionId='session1',
                               eventList=[{'eventId': 'event1', 'sentAt': datetime.datetime.now().timestamp(),
                                           'eventType': 'LIKE',
                                           'properties': json.dumps(
                                               {'itemId': str(itemId), 'eventValue': -4})}])
    print(events)
    return events


def trackingCartEvent(userId, itemId):
    events = client.put_events(trackingId=trackingId, userId=str(userId),
                               sessionId='session1',
                               eventList=[{'eventId': 'event1', 'sentAt': datetime.datetime.now().timestamp(),
                                           'eventType': 'CART',
                                           'properties': json.dumps(
                                               {'itemId': str(itemId), 'eventValue': 5})}])
    print(events)
    return events


def trackingOrderEvent(userId, itemId):
    events = client.put_events(trackingId=trackingId, userId=str(userId),
                               sessionId='session1',
                               eventList=[{'eventId': 'event1', 'sentAt': datetime.datetime.now().timestamp(),
                                           'eventType': 'ORDER',
                                           'properties': json.dumps(
                                               {'itemId': str(itemId), 'eventValue': 10})}])
    print(events)
    return events


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
    trackingViewEvent(1, 2300)
