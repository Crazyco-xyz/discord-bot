import pathlib
import sys
import os

import discord
from discord import app_commands
from discord.ext import commands

from bot.commands import command_test
from bot.events import message_event_listener
from sql.database import Database


class Bot(discord.ext.commands.Bot):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    async def on_ready(self):
        print("Adding commands")
        for filename in os.listdir(f"{project_root}/bot/commands"):
            if filename.endswith(".py"):
                await self.load_extension(f"bot.commands.{filename[:-3]}")
        print("Syncing slash commands")
        await self.tree.sync()
        print("Ready")

    async def on_message(self, msg):
        await message_event_listener.on_message(self, msg)


if __name__ == '__main__':
    project_root = pathlib.Path(__file__).parent

    db = Database(f"{project_root}/database/database.db")
    db.open()

    token = db.execute("select bot_token from config_global")

    if not token:
        print("Error: Token is not setup in database yet!")
        sys.exit(1)

    token = token[0][0]

    intents = discord.Intents.all()

    bot = Bot(command_prefix="", intents=intents)
    bot.run(token)
