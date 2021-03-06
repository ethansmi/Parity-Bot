import json, re

from flask import Flask, Response, request, abort, jsonify
from slackeventsapi import SlackEventAdapter
import os
from threading import Thread
from slack import WebClient

import discord
from discord import Webhook, RequestsWebhookAdapter, Embed, Color

# This `app` represents your existing Flask app
app = Flask(__name__)

greetings = ["hi", "hello", "hello there", "hey"]

bot_name = os.environ['BOT_NAME']
SLACK_SIGNING_SECRET = os.environ['SLACK_SIGNING_SECRET']
slack_token = os.environ['SLACK_BOT_TOKEN']
VERIFICATION_TOKEN = os.environ['VERIFICATION_TOKEN']

# instantiating slack client
slack_client = WebClient(slack_token)


# An example of one of your Flask app's routes
@app.route("/")
def event_hook(request):
    json_dict = json.loads(request.body.decode("utf-8"))
    if json_dict["token"] != VERIFICATION_TOKEN:
        return {"status": 403}

    if "type" in json_dict:
        if json_dict["type"] == "url_verification":
            response_dict = {"challenge": json_dict["challenge"]}
            return response_dict
    return {"status": 500}


slack_events_adapter = SlackEventAdapter(
    SLACK_SIGNING_SECRET, "/parity", app
)


@slack_events_adapter.on("message")
def handle_message(event_data):
    def send_reply(value):
        event_data = value
        message = event_data["event"]
        if not message.get("subtype"):
            command = message.get("text")
            channel_id = message["channel"]
            if any(item in command.lower() for item in greetings) and "bot_profile" not in message.keys():
                message = (
                        "Hello <@%s>! :tada:"
                        % message["user"]  # noqa
                )
                slack_client.chat_postMessage(channel=channel_id, text=message)

    thread = Thread(target=send_reply, kwargs={"value": event_data})
    thread.start()
    return Response(status=200)


# Start the server on port 3000
if __name__ == "__main__":
    app.run(port=3000)
