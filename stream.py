import requests
import json
import datetime
import os
import sys
import random
from sumy.parsers.html import HtmlParser
from sumy.parsers.plaintext import PlaintextParser
from sumy.nlp.tokenizers import Tokenizer
from sumy.summarizers.lsa import LsaSummarizer as Summarizer
from sumy.nlp.stemmers import Stemmer
from sumy.utils import get_stop_words


STREAM_URL = "https://stream.flowdock.com/flows/%s/%s"
POST_URL = "https://api.flowdock.com/flows/%s/%s/messages"


class Plugin:
    BOT_NAME = "rbot"
    BOT_PREFIX = "%s:" % BOT_NAME

    def __init__(self):
        pass

    def help(self):
        pass

    def handle_message(self, msg):
        # Don't look at anonymous messages (e.g., rbot messages)
        if msg.get('external_user_name') == None:
            # Handle direct-to-channel postings
            if msg.get('event', '') == "message":
                return self.handle_content(msg['content'])
        
    def is_direct_address(self, content):
        return content.startswith(self.BOT_PREFIX)

    def get_direct_content(self, content):
        if self.is_direct_address(content):
            return content[len(self.BOT_PREFIX):].strip()


class ResponderPlugin(Plugin):
    RESPONSES_FILE = "responder_plugin.json"

    def __init__(self):
        self.responses = self.load_responses()

    def load_responses(self):
        try:
            with open(self.RESPONSES_FILE) as f:
                return json.load(f)
        except FileNotFoundError as e:
            return {}
            
    def save_responses(self):
        with open(self.RESPONSES_FILE, 'w') as f:
            json.dump(self.responses, f)

    def handle_content(self, msg):
        direct = self.get_direct_content(msg)
        if direct:
            tokens = direct.split()
            if tokens[0] == "reply":
                if tokens[1] == "add":
                    fields = " ".join(tokens[2:]).split("||")
                    if len(fields) in [2,3]:
                        if len(fields) == 2:
                            prob = 1.0
                        else:
                            prob = float(fields[2])
                        before = fields[0].strip()
                        after = fields[1].strip()
                        self.responses[before] = (after, prob)
                        self.save_responses()
                        return "Ok, I'll reply to %s with %s (%s%%)" % (before, after, 100 * prob)
                elif tokens[1] == "delete":
                    k = " ".join(tokens[2:])
                    if k in self.responses:
                        del self.responses[k]
                        self.save_responses()
                        return "Ok, yolo"
                elif tokens[1] == "list":
                    return str(self.responses)
        else:
            for k in self.responses:
                if k in msg:
                    resp, prob = self.responses[k]
                    r = random.random()
                    if r < prob:
                        return resp

 
class SummarizerPlugin(Plugin):
    def handle_content(self, msg):
        direct = self.get_direct_content(msg)
        if direct:
            tokens = direct.split()
            if tokens[0] == "summarize":
                if len(tokens) == 2:
                    return self.summarize_url(tokens[1])

    def summarize_url(self, url, sentences=3, language="english"):
        parser = HtmlParser.from_url(url, Tokenizer(language))
        stemmer = Stemmer(language)

        summarizer = Summarizer(stemmer)
        summarizer.stop_words = get_stop_words(language)

        text = " ".join(map(str, summarizer(parser.document, sentences)))
        return " ".join(text.split())


class TimePlugin(Plugin):
    def handle_content(self, msg):
        if self.is_direct_address(msg):
            if self.get_direct_content(msg) == "time":
                return str(datetime.datetime.now())


class Bot:
    def __init__(self):
        self.plugins = self.load_plugins()

    def load_plugins(self):
        return [TimePlugin(), ResponderPlugin(), SummarizerPlugin()]

    def handle_message(self, msg):
        for plugin in self.plugins:
            resp = plugin.handle_message(msg)
            if resp:
                return resp

        
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
