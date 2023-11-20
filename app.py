from openai import OpenAI
from flask import Flask, request, abort
from linebot import LineBotApi, WebhookHandler
from linebot.exceptions import InvalidSignatureError
from linebot.models import *
import os

app = Flask(__name__)

line_bot_api = LineBotApi(os.environ['CHANNEL_ACCESS_TOKEN'])
handler = WebhookHandler(os.environ['CHANNEL_SECRET'])

def gpt_translation(to_language, input_string):
    client = OpenAI(api_key='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')
    message=[
                {"role": "user", "content": "please translate " + input_string + " to " + to_language + ".  just show me " + to_language + "."}
     ]
    response = client.chat.completions.create(
        model="gpt-4-1106-preview",
        messages=message,
        max_tokens=200
    )
    return response.choices[0].message.content
     
@app.route("/callback", methods=['POST'])
def callback():
    signature = request.headers['X-Line-Signature']
    body = request.get_data(as_text=True)
    app.logger.info("Request body: " + body)
    try:
        handler.handle(body, signature)
    except InvalidSignatureError:
        abort(400)
    return 'OK'

@handler.add(MessageEvent, message=TextMessage)
def handle_message(event):
    user_id = event.source.user_id
    if user_id == 'SPECIAL_USER_ID':
        message = TextSendMessage(text = user_id + ": " + gpt_translation("Chinese", event.message.text))
    else:
        message = TextSendMessage(text = user_id + ": " + gpt_translation("Indonesian", event.message.text))
        
    line_bot_api.reply_message(event.reply_token, message)

import os
if __name__ == "__main__":
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)
