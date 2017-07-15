from .plugin import Plugin
import json
import random


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

plugin = ResponderPlugin()
