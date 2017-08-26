import json
import requests
VERIFY_TOKEN = "jeton_test_messenger_webhook"
PAGE_ACCESS_TOKEN = "EAAYf24MXlloBAIShXxff8LlsG4ZCAA9ECQLWzci9Th5HlVVpOONNXbPUUBksJxUyHS3xqMAMzj5pmZCg1VMDZBETWQZCIZA8Mf0fM47jXsRZArqcrEEJoLzZAkQrWdA9YZBbjatQL1fC3lwI2qUMT5SZCToDZAXcdv3BcRPEZC5sLIe0wZDZD"

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
    if body:
        print 'Received message:' + body
        body = json.loads(body)
        for e in body.get("entry", []):
            for m in e.get("messaging", []):
                print 'sender:' + m['sender']['id']
                print 'recipient:' + m['recipient']['id']
                text = m.get("message", {}).get("text", "")
                print 'message text:' + text
                attachments = m.get("message", {}).get("attachments", {})
                print 'message attachments :' + str(attachments)
                if attachments and attachments[0].get("type", "") == "image":
                    # process Image
                    print 'image found'
                    return m['sender']['id'], attachments
                return m['sender']['id'], None
    return None

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
    verif = verify(event)
    if verif:
        return verif

    sender_id, attachments = receive_message(event)
    if attachments :
        message="Image found, processing is starting ..."

    send_message(sender_id, message)

    print message
    response = {
        'body': message,
        'statusCode': 200
    }
    return response
