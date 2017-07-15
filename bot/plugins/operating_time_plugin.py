from .plugin import Plugin
import os


class OperatingTimePlugin(Plugin):
    DATA_DIRECTORY = "operating_times"

    def __init__(self):
        if not os.path.exists(self.DATA_DIRECTORY):
            os.makedirs(self.DATA_DIRECTORY)

    def handle_message(self, msg):
        if not self.is_anon(msg):
            if msg.get('event') == "message":
                user = msg.get('user')
                ts = msg.get('sent')
                if user and ts:
                    with open(os.path.join(self.DATA_DIRECTORY, user), 'a') as f:
                        f.write("%s\n" % ts)

plugin = OperatingTimePlugin()

