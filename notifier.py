import re

import telegram

class TelegramNotifier:
    _bot = None
    _users = []

    def __init__(self, token, users):
        if token is not None and users is not None:
            self._bot = telegram.Bot(token)
            self._users = users

    _prefix = None
    def setPrefix(self, prefix: str):
        self._prefix = prefix

    def escapeText(self, text: str):
        chars = '|'.join(list(map(lambda char: re.escape(char), r'_*[]()~`>#+-=|{}.!')))
        return re.sub(r'(' + chars + r')', r'\\\1', text)
    
    async def notify(self, text):
        # Skip if can't notify
        if not self._bot or len(self._users) == 0: return

        async with self._bot:
            for userId in self._users:
                notificationPrefix = f'*{self._prefix}*: ' if self._prefix is not None else ''
                message = notificationPrefix + text
                await self._bot.send_message(text=message, chat_id=userId, parse_mode='MarkdownV2')
