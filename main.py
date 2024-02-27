import pathlib
import sys
import os

import nextcord
from nextcord.ext import commands

from bot.commands import command_test
from bot.events import on_join_listener
from sql.database import Database

from dotenv import load_dotenv


class Bot(nextcord.ext.commands.Bot):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.db: Database = None

    def _load_dir_(self, directory, python_path):
        for filename in os.listdir(directory):
            if filename.endswith(".py"):
                self.load_extension(f"{python_path}.{filename[:-3]}")

    async def on_ready(self):
        print("Loading commands")
        self._load_dir_(f"{project_root}/bot/commands", "bot.commands")
        print("Loading events")
        self._load_dir_(f"{project_root}/bot/events", "bot.events")
        print("Syncing slash commands")
        await self.sync_application_commands(guild_id=1208037232288604250)
        print("Setting up guilds")
        await self.setup_guilds()
        print("Done")

    async def setup_guilds(self):
        sql = "select * from config_guilds"
        result = self.db.execute(sql)

        for (_, guild_id, guild_captcha_channel, guild_captcha_role, guild_last_captcha_msg) in result:
            guild = self.get_guild(guild_id)
            channel = guild.get_channel(guild_captcha_channel)
            if channel is None:
                print(f"Failed to find captcha channel for guild {guild.name}")
                continue

            captcha_module = self.get_cog("CaptchaCommand")

            if captcha_module is None:
                print("Failed to get captcha cog")
                continue

            if guild_last_captcha_msg is not None:
                try:
                    msg = await channel.fetch_message(guild_last_captcha_msg)
                    try:
                        await msg.delete()
                    except nextcord.NotFound:
                        print("Failed to delete the old captcha message since it's not found")

                except nextcord.NotFound:
                    print(f"Unable to find old captcha message ({guild_last_captcha_msg})")

            await captcha_module.send_captcha_message(channel)


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

    bot = Bot(intents=intents)

    bot.db = db
    bot.run(token)
