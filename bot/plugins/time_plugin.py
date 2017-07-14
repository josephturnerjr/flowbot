from .plugin import Plugin
import datetime


class TimePlugin(Plugin):
    def handle_content(self, msg):
        if self.is_direct_address(msg):
            if self.get_direct_content(msg) == "time":
                return str(datetime.datetime.now())

plugin = TimePlugin()
