import openai
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
    AsyncMessagingApi,
    Configuration,
    ReplyMessageRequest,
    PushMessageRequest,
    TextMessage
)
import os

app = Flask(__name__)

line_bot_api = LineBotApi(os.environ['CHANNEL_ACCESS_TOKEN'])
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
            max_tokens=200)
        return_message = response.choices[0].message.content
    except openai.APIError as e:
        return_message = "OpenAI API returned an API Error: " + str(e)    
        pass
    except openai.APIConnectionError as e:
        return_message = "Failed to connect to OpenAI API: " + str(e)
        pass
    except openai.RateLimitError as e:
        return_message = "OpenAI API request exceeded rate limit: " + str(e)
        pass
    except openai.Timeout as e:
        return_message = "OpenAI API request timed out: " + str(e)
        pass
    except openai.InvalidRequestError as e:
        return_message = "Invalid request to OpenAI API: " + str(e)
        pass
    except openai.AuthenticationError as e:
        return_message = "Authentication error with OpenAI API: " + str(e)
        pass
    except openai.ServiceUnavailableError as e:
        return_message = "OpenAI API service unavailable: " + str(e)
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
        print(f"event: {event}")
        print(f"event type: {type(event)}")
        print(isinstance(event, MessageEvent))
        if not isinstance(event, MessageEvent):
            print("not isinstance(event, MessageEvent)")
            continue

        if not isinstance(event.message, TextMessageContent):
            print("not isinstance TextMessageContent")
            continue

        print("event type = " + type(event).__name__)      
        user_id = event.source.user_id
        if user_id == 'Ucf4bc1a28d7da04ad9056c5ad854945e':
            message = TextMessage(text = gpt_translation("Chinese", event.message.text), quoteToken=event.message.quote_token)
        else:             
            message = TextMessage(text = gpt_translation("Indonesian", event.message.text), quoteToken=event.message.quote_token)

        #print("text: " + event.message.text)
        #print("quote_token: " + event.message.quote_token)
        #print("message: " + str(message)) 
        line_bot_api.push_message(push_message_request=PushMessageRequest(
            to=event.source.user_id,
            messages=message,))
         
        #line_bot_api.reply_message(event.message.quote_token, message)     
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
    line_bot_api.reply_message(reply_quote_token, message)
            result = line_bot_api.push_message(push_message_request=PushMessageRequest(
            to=event.source.user_id,
            messages=[TextMessage(
                text=message,
                quoteToken=event.message.quote_token)],))
"""

import os
if __name__ == "__main__":
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)
