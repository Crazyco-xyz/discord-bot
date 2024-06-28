from __future__ import annotations

import pathlib
import sys

import nextcord
from dotenv import load_dotenv

from bot import discord_bot
from sql.database import Database

Bot = discord_bot.Bot

if __name__ == "__main__":
    project_root = pathlib.Path(__file__).parent

    load_dotenv()

    db = Database()

    token = db.execute("select bot_token from config_global")

    if not token:
        print("Error: Token is not setup in database yet!")
        sys.exit(1)

    token = token[0][0]

    intents = nextcord.Intents.all()

    bot = discord_bot.Bot(intents=intents)

    bot.db = db
    bot.project_root = project_root
    bot.run(token)
