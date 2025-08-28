"""
Entry point for the Meeting Calculator Bot.
"""
from .bot import Bot
from .email_server import EmailServer
from .db import DB

if __name__ == "__main__":
    bot = Bot(EmailServer(), DB())
    bot.run()
