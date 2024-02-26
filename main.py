import asyncio

from sql.database import Database
import pathlib
import discord
from discord.ext import commands

from bot.events.message_event_listener import OnMessageEvent
from bot.commands.test import TestCommand
from discord import app_commands


class Bot(discord.ext.commands.Bot):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    async def on_ready(self):
        print("Ready!")
        await self.add_cog(OnMessageEvent(self))
        await self.add_cog(TestCommand(self), guilds=[discord.Object(id=1208037232288604250)])
        print("Added cogs")


if __name__ == '__main__':
    project_root = pathlib.Path(__file__).parent

    db = Database(f"{project_root}/database/database.db")
    db.open()

    token = db.execute("select bot_token from config_global")[0][0]

    intents = discord.Intents.all()

    bot = Bot(command_prefix="!", intents=intents)
    bot.run(token)
