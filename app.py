import os
import time
import re
from slackclient import SlackClient
import urllib
from bs4 import BeautifulSoup
import json
from PIL import Image
from io import BytesIO
import requests
slack_client = SlackClient(os.environ.get('SLACK_BOT_TOKEN'))
starterbot_id = None

RTM_READ_DELAY = 1 # 1 second delay between reading from RTM
HAVA = "hava"
EURO = "euro"

MENTION_REGEX = "^<@(|[WU].+?)>(.*)"

def parse_bot_commands(slack_events):
    for event in slack_events:
        if event["type"] == "message" and not "subtype" in event:
            user_id, message = parse_direct_mention(event["text"])
            if user_id == starterbot_id:
                return message, event["channel"]
    return None, None

def parse_direct_mention(message_text):
    matches = re.search(MENTION_REGEX, message_text)
    return (matches.group(1), matches.group(2).strip()) if matches else (None, None)

def handle_command(command, channel):

    # Default response is help text for the user
    default_response = "Yazdığın komutu anlayamadım."

    # Finds and executes the given command, filling in response
    response = None
    # This is where you start to implement more commands!
    
    if HAVA in command:
        response ="http://www.mgm.gov.tr/sunum/sondurum-show-2.aspx?m=ANKARA&rC=111&rZ=fff"
        resp=requests.get(response)
        slack_client.api_call(
        "files.upload",
        channel=channel,
        file=resp.raw,
        title="Hava Durumu",
        filename="hava.png"
    	)
        response ="http://www.mgm.gov.tr/sunum/sondurum-show-2.aspx?m=ANKARA&rC=111&rZ=fff"

    if EURO in command:
        kur =urllib.requests.urlopen("http://data.fixer.io/api/latest?access_key=*********&format=1").read()
        val = json.loads(kur)
        deger=val['rates']['TRY']
        response="1 EURO "+str(deger)+" TL"
    

    slack_client.api_call(
        "chat.postMessage",
        channel=channel,
        text=response or default_response
    )
if __name__ == "__main__":
    if slack_client.rtm_connect(with_team_state=False):
        print("Starter Bot connected and running!")
        # Read bot's user ID by calling Web API method `auth.test`
        starterbot_id = slack_client.api_call("auth.test")["user_id"]
        while True:
            command, channel = parse_bot_commands(slack_client.rtm_read())
            if command:
                handle_command(command, channel)
            time.sleep(RTM_READ_DELAY)
    else:
        print("Connection failed. Exception traceback printed above.")
