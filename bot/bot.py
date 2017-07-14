import os
import re
import importlib

class Bot:
    def __init__(self):
        self.plugins = self.load_plugins()

    def load_plugins(self):
        files = os.listdir(os.path.join(os.path.dirname(__file__), "plugins"))
        plugins = [os.path.splitext(f)[0] for f in files if re.search("_plugin.py$", f)]
        return [importlib.import_module("bot.plugins.%s" % p).plugin for p in plugins]

    def handle_message(self, msg):
        for plugin in self.plugins:
            resp = plugin.handle_message(msg)
            if resp:
                return resp
