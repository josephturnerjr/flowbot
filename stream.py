import traceback
import requests
import json
import datetime
import os
import sys
import random

from bot import Bot


STREAM_URL = "https://stream.flowdock.com/flows/%s/%s"
POST_URL = "https://api.flowdock.com/flows/%s/%s/messages"


if __name__ == "__main__":
    if len(sys.argv) != 3:
        print("Usage: %s <org name> <flow name>" % sys.argv[0])
        sys.exit(0)
    _, org_name, flow_name = sys.argv
    flow_params = (org_name, flow_name)
    stream_url = STREAM_URL % flow_params
    post_url = POST_URL % flow_params

    api_key = os.environ.get('FLOWDOCK_API_KEY')
    if not api_key:
        print("You must specify the flowdock API key in the env variable FLOWDOCK_API_KEY")
        sys.exit(0)
    auth = (api_key, "")

    bot = Bot()
    r = requests.get(stream_url, stream=True, auth=auth)
    print(r.status_code)
    
    for line in r.iter_lines(decode_unicode=True, delimiter='\r'.encode()):
        try:
            comment_data = json.loads(line.decode('utf-8'))
            resp = bot.handle_message(comment_data)
            if resp:
                print(resp)
                r = requests.post(post_url, data={"external_user_name": "rbot", "event": "message", "content": resp}, auth=auth)
                print(r.status_code)
                print(r.content)
        except Exception as e:
            print(line)
            print(e)
            traceback.print_exc()
