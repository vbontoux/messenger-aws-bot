from __future__ import print_function

import json
import requests

print('Loading function')

def send_message(recipient_id, message_text, page_access_token):
    print("sending message to {recipient}: {text}".format(recipient=recipient_id, text=message_text))
    params = {
        "access_token": page_access_token
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
       print(r.status_code)
       print(r.text)


def lambda_handler(event, context):
    #print("Received event: " + json.dumps(event, indent=2))
    message = event['Records'][0]['Sns']['Message']
    message = json.loads(message)
    sender_id = message.get("participation_message", {}).get("sender_id", "")
    page_access_token = message.get("participation_message", {}).get("channel_properties", {}).get("PAGE_ACCESS_TOKEN", "")
    match_result = message.get("match_result", {}).get("status", "unknown")
    
    message_text = "Bravo you got a match!" if match_result == "match" else "Sorry there is no match"
    send_message(sender_id, message_text, page_access_token)
    return message_text
