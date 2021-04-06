import os
import time
import re
from slackclient import SlackClient

slack_token = os.environ.get("SLACK_TOKEN")
print(slack_token)
bot_name = "parity bot"
slack_client = SlackClient(slack_token)


def parse_slack_output(slack_rtm_output):
    output_list = slack_rtm_output
    if output_list and len(output_list) > 0:
        for output in output_list:
            if output and "text" in output:
                text = output["text"]

                if bot_name in text.lower():
                    return text.lower().split(bot_name)[1].strip().lower(), output["channel"]

    return None, None


def handle_command(text, channel):
    if text == ".test":
        slack_client.api_call("chat.postMessage", channel=channel, text="I work! :)", as_user=True)


if __name__ == "__main__":
    if slack_client.rtm_connect():
        print("Connected!")
        while True:
            text_input, channel = parse_slack_output(slack_client.rtm_read())
            if text_input and channel:
                handle_command(text_input, channel)
                time.sleep(1)
    else:
        print("Connection Failed")
