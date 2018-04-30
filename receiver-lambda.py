import json
import requests
VERIFY_TOKEN = "jeton_test_messenger_webhook"
PAGE_ACCESS_TOKEN = "xxxxxxxxxxxxxxxxxxxxxxxxxxx"
# Page ID, PAGE_ACCESS_TOKEN, APPID to be stored in dynamo db campaign table

import boto3
dynamodb = boto3.resource('dynamodb')
participation_table = dynamodb.Table("participations")
sns = boto3.client('sns')
new_participation_sns_arn =  'arn:aws:sns:eu-west-2:458847123929:new-participation' #[t["TopicArn"] for t in sns.list_topics()['Topics'] if t["TopicArn"].endswith(':' + 'new-participation')][0] 

def send_message(recipient_id, message_text):
    print "sending message to {recipient}: {text}".format(recipient=recipient_id, text=message_text)
    params = {
        "access_token": PAGE_ACCESS_TOKEN
    }
    headers = {
        "Content-Type": "application/json"
    }
    data = json.dumps({
        "recipient": {
            "id": recipient_id
        },
        "message": {
            "text": message_text
        }
    })
    r = requests.post("https://graph.facebook.com/v2.6/me/messages", params=params, headers=headers, data=data)
    if r.status_code != 200:
       print r.status_code
       print r.text

def receive_message(event):
    body = event.get("body", "")
    res = {"sender_id": None, "attachement": None, "page_id": None, "time": None, "message_id": None}
    if body:
        print 'Received message:' + body
        body = json.loads(body)
        for e in body.get("entry", []):
            page_id = e.get("id", "")           # todo pass it to dynamodb cappaign table to get the PAGE_ACCESS_TOKEN (for reply)
            time = e.get("time", "")
            for m in e.get("messaging", []):
                print 'sender:' + m['sender']['id']
                print 'recipient:' + m['recipient']['id']
                message = m.get("message", {})
                text = message.get("text", "")
                mid = message.get("mid", "")
                print 'message text:' + text
                attachments = message.get("attachments", {})
                print 'message attachments :' + str(attachments)
                if attachments and attachments[0].get("type", "") == "image":
                    # process Image
                    print 'image found'
                    return {"sender_id": m['sender']['id'], "attachment": attachments[0], "page_id": page_id, "time": time, "message_id": mid}
                return {"sender_id": m['sender']['id'], "attachment": None, "page_id": page_id, "time": time, "message_id": mid}
    return res

def verify(event):
    qs = event.get("queryStringParameters", "")
    if qs:
        rVerifyToken = qs.get('hub.verify_token', "")
        if rVerifyToken:
            challenge = qs.get('hub.challenge', "")
            response = {
               'body': str(challenge),
               'statusCode': 200
            }
            return response
    return None
    
def handler(event, context):
    message = "No image found in your message ..."

    # Case mode verify
    verif = verify(event)
    if verif:
        return verif

    # Case message received
    print 'Received event:' + str(event)

    # Get message sender and attachments
    recv = receive_message(event)
    url = "-"
    attachment = recv['attachment']
    if attachment :
        message="Image found, processing is starting ..."
        url = attachment.get("payload", {}).get("url", "-")

    # Add participation into dynamodb
    import time
    item = {
            "id": recv['message_id'],
            "cid": recv['page_id'], # to be changed to actual campaign id read from campaign table
            "time": recv['time'],
            "channel_type": "messenger",
            "channel_id": recv['page_id'],
            "sender_id": recv['sender_id'],
            "image_url": url,
            "channel_properties": { "PAGE_ACCESS_TOKEN": PAGE_ACCESS_TOKEN }
            # todo add timestamp from FB
    }
    participation_table.put_item(
        Item=item
    )
    if item['image_url'] != "-":
        sns.publish(
            TopicArn=new_participation_sns_arn,
            Message=json.dumps(item),
            Subject='A new participation with image has bee created.',
            MessageStructure="raw"
        )

    send_message(recv['sender_id'], message)

    print message
    response = {
        'body': message,
        'statusCode': 200
    }
    return response
