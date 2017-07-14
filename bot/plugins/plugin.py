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
