import openai
import sys
import uvicorn
from flask import Flask, request, abort
from openai import OpenAI
from linebot import LineBotApi, WebhookHandler
from linebot.v3.webhook import WebhookParser
from linebot.exceptions import InvalidSignatureError
from linebot.v3.webhooks import (
    MessageEvent,
    TextMessageContent
)
from linebot.v3.messaging import (
    AsyncApiClient,
    ApiClient,
    AsyncMessagingApi,
    MessagingApi,
    Configuration,
    ReplyMessageRequest,
    PushMessageRequest,
    TextMessage
)
import os

app = Flask(__name__)

configuration = Configuration(access_token=os.environ['CHANNEL_ACCESS_TOKEN'])
async_api_client = ApiClient(configuration)
line_bot_api = MessagingApi(async_api_client)
#line_bot_api = LineBotApi(os.environ['CHANNEL_ACCESS_TOKEN'])
handler = WebhookHandler(os.environ['CHANNEL_SECRET'])
parser = WebhookParser(os.environ['CHANNEL_SECRET'])

def gpt_translation(to_language, input_string):
     
    client = OpenAI()

    message=[
                {"role": "user", "content": "please translate " + input_string + " to " + to_language + ".  just show me " + to_language + "."}
     ]
    try:
        response = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=message,
            max_tokens=500,
            timeout=30)
        return_message = response.choices[0].message.content
    except BaseException as e:
        return_message = f"OpenAI API returned an API Error: {str(e)}"
        pass

    return return_message
     
@app.route("/callback", methods=['POST'])
def callback():
    signature = request.headers['X-Line-Signature']
    body = request.data.decode('utf-8')

    try:
        events = parser.parse(body, signature)
    except InvalidSignatureError:
        raise HTTPException(status_code=400, detail="Invalid signature")
   
    for event in events:
        print(str(event))
        sys.stdout.flush()
        if not isinstance(event, MessageEvent):
            print("not isinstance(event, MessageEvent)")
            continue

        if not isinstance(event.message, TextMessageContent):
            print("not isinstance TextMessageContent")
            continue
        if event.source.type == 'user':
            to_id = event.source.user_id
        elif event.source.type == 'group':  
            to_id = event.source.group_id
        else:
            to_id = event.source.room_id

        user_id = event.source.user_id
        if user_id == 'Ucf4bc1a28d7da04ad9056c5ad854945e':
            translated_text = gpt_translation("Chinese", event.message.text)
            to_message = TextMessage(text = translated_text, quoteToken=event.message.quote_token)
        else:       
            translated_text = gpt_translation("Indonesian", event.message.text)
            to_message = TextMessage(text = translated_text, quoteToken=event.message.quote_token)

        #print("text: " + event.message.text)
        #print("quote_token: " + event.message.quote_token)
        #print("message: " + str(to_message)) 
        push_message_request = PushMessageRequest(to=to_id, messages=[to_message])
        line_bot_api.push_message(push_message_request)
         
        #.reply_message(event.message.quote_token, message)     
    return 'OK'
"""
@handler.add(MessageEvent, message=TextMessage)
def handle_message(event):
    user_id = event.source.user_id
    #AttributeError: 'TextMessage' object has no attribute 'quoteToken'
    reply_quote_token = event.reply_token
    print("event" + str(event))
    if user_id == 'Ucf4bc1a28d7da04ad9056c5ad854945e':
        message = TextSendMessage(text = gpt_translation("Chinese", event.message.text))
    else:
        message = TextSendMessage(text = gpt_translation("Indonesian", event.message.text))
    .reply_message(reply_quote_token, message)
            result = .push_message(push_message_request=PushMessageRequest(
            to=event.source.user_id,
            messages=[TextMessage(
                text=message,
                quoteToken=event.message.quote_token)],))
"""

import os
if __name__ == "__main__":
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)
