"""
Entry point for the Meeting Calculator Bot.
"""
from src.bot.bot import Bot
from src.bot.email_server import EmailServer
from src.bot.db import DB

if __name__ == "__main__":
    bot = Bot(EmailServer(), DB())
    bot.run()
