import pathlib

import discord
from discord import app_commands

from bot.commands import command_test
from bot.events import message_event_listener
from sql.database import Database


class Bot(discord.Client):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.tree = None

    async def on_ready(self):
        print("Adding commands")
        command_test.register_command(self.tree)
        print("Syncing slash commands")
        await tree.sync(guild=discord.Object(id=1208037232288604250))
        print("Ready")

    async def on_message(self, msg):
        await message_event_listener.on_message(self, msg)


if __name__ == '__main__':
    project_root = pathlib.Path(__file__).parent

    db = Database(f"{project_root}/database/database.db")
    db.open()

    token = db.execute("select bot_token from config_global")[0][0]

    intents = discord.Intents.all()

    bot = Bot(intents=intents)
    tree = app_commands.CommandTree(bot)
    bot.tree = tree
    bot.run(token)
