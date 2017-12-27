import os
import sys
import json

import requests
from flask import Flask, request

app = Flask(__name__)


@app.route('/', methods=['GET'])
def verify():
    # when the endpoint is registered as a webhook, it must echo back
    # the 'hub.challenge' value it receives in the query arguments
    if request.args.get("hub.mode") == "subscribe" and request.args.get("hub.challenge"):
        if not request.args.get("hub.verify_token") == os.environ["VERIFY_TOKEN"]:
            return "Verification token mismatch", 403
        return request.args["hub.challenge"], 200

    return "Hello world", 200


@app.route('/', methods=['POST'])   
def webhook():

    # endpoint for processing incoming messaging events

    data = request.get_json()
    log(data)  # you may not want to log every incoming message in production, but it's good for testing

    if data["object"] == "page":   # make sure this is a page subscription

        for entry in data["entry"]:
            for messaging_event in entry["messaging"]:

                if messaging_event.get("message"):     # someone sent us a message
                    received_message(messaging_event)

                elif messaging_event.get("delivery"):  # delivery confirmation
                    pass
                    # received_delivery_confirmation(messaging_event)

                elif messaging_event.get("optin"):     # optin confirmation
                    pass
                    # received_authentication(messaging_event)

                elif messaging_event.get("postback"):  # user clicked/tapped "postback" button in earlier message
                    received_postback(messaging_event)

                else:    # uknown messaging_event
                    log("Webhook received unknown messaging_event: " + str(messaging_event))

    return "ok", 200


def received_message(event):

    sender_id = event["sender"]["id"]        # the facebook ID of the person sending you the message
    recipient_id = event["recipient"]["id"]  # the recipient's ID, which should be your page's facebook ID
    
    # could receive text or attachment but not both
    if "text" in event["message"]:
        message_text = event["message"]["text"]

        # parse message_text and give appropriate response   
        if message_text == 'image':
            send_image_message(sender_id)

        elif message_text == 'file':
            send_file_message(sender_id)

        elif message_text == 'audio':
            send_audio_message(sender_id)

        elif message_text == 'video':
            send_video_message(sender_id)

        elif message_text == 'button':
            send_button_message(sender_id)

        # elif message_text == 'generic':
        #     send_generic_message(sender_id)

        elif message_text == 'share':
            send_share_message(sender_id)

        else: # default case
            send_text_message(sender_id, "Echo: " + message_text)

    elif "attachments" in event["message"]:
        message_attachments = event["message"]["attachments"]   
        send_text_message(sender_id, "Message with attachment received")


# Message event functions
def send_text_message(recipient_id, message_text):

    # encode('utf-8') included to log emojis to heroku logs
    log("sending message to {recipient}: {text}".format(recipient=recipient_id, text=message_text.encode('utf-8')))

    message_data = json.dumps({
        "recipient": {
            "id": recipient_id
        },
        "message": {
            "text": message_text
        }
    })

    call_send_api(message_data)
    

# def send_image_message(recipient_id):

#     message_data = json.dumps({
#         "recipient": {
#             "id": recipient_id
#         },
#         "message": {
#             "attachment": {
#                 "type":"image",
#                 "payload":{
#                     "url":"http://i.imgur.com/76rJlO9.jpg"
#                 }
#             }
#         }
#     })

#     log("sending image to {recipient}: ".format(recipient=recipient_id))

#     call_send_api(message_data)


# def send_file_message(recipient_id):

#     message_data = json.dumps({
#         "recipient": {
#             "id": recipient_id
#         },
#         "message": {
#             "attachment": {
#                 "type":"file",
#                 "payload":{
#                     "url":"http://ee.usc.edu/~redekopp/ee355/EE355_Syllabus.pdf"
#                 }
#             }
#         }
#     })

#     log("sending file to {recipient}: ".format(recipient=recipient_id))

#     call_send_api(message_data)


# def send_audio_message(recipient_id):

#     message_data = json.dumps({
#         "recipient": {
#             "id": recipient_id
#         },
#         "message": {
#             "attachment": {
#                 "type":"audio",
#                 "payload":{
#                     "url":"http://www.stephaniequinn.com/Music/Allegro%20from%20Duet%20in%20C%20Major.mp3"
#                 }
#             }
#         }
#     })

#     log("sending audio to {recipient}: ".format(recipient=recipient_id))

#     call_send_api(message_data)


# def send_video_message(recipient_id):

#     message_data = json.dumps({
#         "recipient": {
#             "id": recipient_id
#         },
#         "message": {
#             "attachment": {
#                 "type":"video",
#                 "payload":{
#                     "url":"http://techslides.com/demos/sample-videos/small.mp4"
#                 }
#             }
#         }
#     })

#     log("sending video to {recipient}: ".format(recipient=recipient_id))

#     call_send_api(message_data)


# def send_button_message(recipient_id):

#     message_data = json.dumps({
#         "recipient": {
#             "id": recipient_id
#         },
#         "message": {
#             "attachment": {
#                 "type":"template",
#                 "payload":{
#                     "template_type":"button",
#                     "text":"What do you want to do next?",
#                     "buttons":[
#                     {
#                         "type":"web_url",
#                         "url":"https://www.google.com",
#                         "title":"Google"
#                     },
#                     {
#                         "type":"postback",
#                         "title":"Call Postback",
#                         "payload":"Payload for send_button_message()"
#                     }
#                     ]
#                 }
#             }
#         }
#     })

#     log("sending button to {recipient}: ".format(recipient=recipient_id))

#     call_send_api(message_data)

def send_quickreply_message(recipient_id, message, quick_replies):

    # List of objects {content_type, title, pyaload}
    quick_reply_list = []
    
    for title_payload in quick_replies:
        quick_reply_list.append({'content_type':"text", 'title':title_payload, 'payload':title_payload})

    message_data = json.dumps({
            "recipient": {
                "id": recipient_id
            },
            "message": {
                "text": message,
                "quick_replies": quick_reply_list
            }
        })

    log("sending quickreply message to {recipient}: ".format(recipient=recipient_id))

    call_send_api(message_data)


# def send_share_message(recipient_id):

#     # Share button only works with Generic Template
#     message_data = json.dumps({
#         "recipient": {
#             "id": recipient_id
#         },
#         "message": {
#             "attachment": {
#                 "type":"template",
#                 "payload":{
#                     "template_type":"generic",
#                     "elements":[
#                     {
#                         "title":"Reddit link",
#                         "subtitle":"Something funny or interesting",
#                         "image_url":"https://pbs.twimg.com/profile_images/667516091330002944/wOaS8FKS.png",
#                         "buttons":[
#                         {
#                             "type":"element_share"
#                         }
#                         ]
#                     }    
#                     ]
#                 }
        
#             }
#         }
#     })

#     log("sending share button to {recipient}: ".format(recipient=recipient_id))

#     call_send_api(message_data)


def received_postback(event):

    sender_id = event["sender"]["id"]        # the facebook ID of the person sending you the message
    recipient_id = event["recipient"]["id"]  # the recipient's ID, which should be your page's facebook ID

    # The payload param is a developer-defined field which is set in a postback
    # button for Structured Messages
    payload = event["postback"]["payload"]

    log("received postback from {recipient} with payload {payload}".format(recipient=recipient_id, payload=payload))

    if payload == 'Get Started':
        # Get Started button was pressed
        # send_text_message(sender_id, "Welcome to the Engage Bot! This platform enables you anonymously comments on Facebook posts. You simply just have to send us the unique post URL and then write your comment. [SEND VID].")
        # Engage quickreply
        txt = "Welcome to the Engage Bot! This platform enables you anonymously comments on Facebook posts. You simply just have to send us the unique post URL and then write your comment. [SEND VID]."
        send_quickreply_message(sender_id, txt, ["Engage"])
    else:
        # Notify sender that postback was successful
        send_text_message(sender_id, "Postback called")


def call_send_api(message_data):

    params = {
        "access_token": os.environ["PAGE_ACCESS_TOKEN"]
    }
    headers = {
        "Content-Type": "application/json"
    }
    
    r = requests.post("https://graph.facebook.com/v2.6/me/messages", params=params, headers=headers, data=message_data)
    if r.status_code != 200:
        log(r.status_code)
        log(r.text)


def log(message):  # simple wrapper for logging to stdout on heroku
    print str(message)
    sys.stdout.flush()


# import os
# import sys
# import json
# from datetime import datetime

# import requests
# from flask import Flask, request

# app = Flask(__name__)


# @app.route('/', methods=['GET'])
# def verify():
#     # when the endpoint is registered as a webhook, it must echo back
#     # the 'hub.challenge' value it receives in the query arguments
#     if request.args.get("hub.mode") == "subscribe" and request.args.get("hub.challenge"):
#         if not request.args.get("hub.verify_token") == os.environ["VERIFY_TOKEN"]:
#             return "Verification token mismatch", 403
#         return request.args["hub.challenge"], 200

#     return "Facebook Messenger Bot - Engage", 200


# @app.route('/', methods=['POST'])
# def webhook():

#     # endpoint for processing incoming messaging events

#     data = request.get_json()
#     # log(data)

#     if data["object"] == "page":

#         for entry in data["entry"]:
#             for messaging_event in entry["messaging"]:

#                 if messaging_event.get("message"):  # someone sent us a message

#                     sender_id = messaging_event["sender"]["id"]        # the facebook ID of the person sending you the message
#                     recipient_id = messaging_event["recipient"]["id"]  # the recipient's ID, which should be your page's facebook ID
#                     message_text = messaging_event["message"]["text"]  # the message's text

#                     send_message(sender_id, "Initial setup works!")

#                 if messaging_event.get("delivery"):  # delivery confirmation
#                     pass

#                 if messaging_event.get("optin"):  # optin confirmation
#                     pass

#                 if messaging_event.get("postback"):  # user clicked/tapped "postback" button in earlier message
#                     pass

#     return "ok", 200


# def send_message(recipient_id, message_text):

#     log("sending message to {recipient}: {text}".format(recipient=recipient_id, text=message_text))

#     params = {
#         "access_token": os.environ["PAGE_ACCESS_TOKEN"]
#     }
#     headers = {
#         "Content-Type": "application/json"
#     }
#     data = json.dumps({
#         "recipient": {
#             "id": recipient_id
#         },
#         "message": {
#             "text": message_text
#         }
#     })
#     r = requests.post("https://graph.facebook.com/v2.6/me/messages", params=params, headers=headers, data=data)
#     if r.status_code != 200:
#         log(r.status_code)
#         log(r.text)


# def log(msg, *args, **kwargs):  # simple wrapper for logging to stdout on heroku
#     try:
#         if type(msg) is dict:
#             msg = json.dumps(msg)
#         else:
#             msg = unicode(msg).format(*args, **kwargs)
#         print u"{}: {}".format(datetime.now(), msg)
#     except UnicodeEncodeError:
#         pass  # squash logging errors in case of non-ascii text
#     sys.stdout.flush()


if __name__ == '__main__':
    app.run(debug=True)
