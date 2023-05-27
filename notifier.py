import re

import telegram

class TelegramNotifier:
    _bot = None
    _users = []

    def __init__(self, token, users):
        self._bot = telegram.Bot(token)
        self._users = users

    def escapeText(self, text: str):
        chars = '|'.join(list(map(lambda char: re.escape(char), r'_*[]()~`>#+-=|{}.!')))
        return re.sub(r'(' + chars + r')', r'\\\1', text)
    
    async def notify(self, text):
        # Skip if can't notify
        if not self._bot or len(self._users) == 0: return

        async with self._bot:
            for userId in self._users:
                await self._bot.send_message(text=text, chat_id=userId, parse_mode='MarkdownV2')
