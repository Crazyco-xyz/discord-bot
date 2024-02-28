from __future__ import annotations

import os

import nextcord
from nextcord.ext import commands

from bot.utils import logger
from sql.database import Database


class Bot(nextcord.ext.commands.Bot):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.db: Database = None
        self.project_root: str = ""

    def _load_dir_(self, directory, python_path):
        for filename in os.listdir(directory):
            if filename.endswith(".py"):
                self.load_extension(f"{python_path}.{filename[:-3]}")

    def get_guild_logger(self, guild: [nextcord.Guild | int]):
        """
        Returns a logger for the given guild
        :param guild: May be a guild object or a guild id
        :return: logger for that guild
        """
        guild_input = guild if type(guild) is int else guild.id
        return logger.Logger(guild_id=guild_input, bot=self)

    async def on_ready(self):
        print("Loading commands")
        self._load_dir_(f"{self.project_root}/bot/commands", "bot.commands")
        print("Loading events")
        self._load_dir_(f"{self.project_root}/bot/events", "bot.events")
        print("Syncing slash commands")
        await self.sync_application_commands(guild_id=1208037232288604250)
        print("Setting up guilds")
        await self.setup_guilds()
        print("Done")

    async def setup_guilds(self):
        sql = "select * from config_guilds"
        result = self.db.execute(sql)

        for (_, guild_id, guild_captcha_channel, guild_captcha_role, guild_last_captcha_msg, guild_log_retention) in result:
            guild = self.get_guild(guild_id)
            setup_logger = self.get_guild_logger(guild)
            channel = guild.get_channel(guild_captcha_channel)
            if channel is None:
                setup_logger.warn(f"Failed to find captcha channel for guild {guild.name}")
                continue

            captcha_module = self.get_cog("CaptchaCommand")

            if captcha_module is None:
                setup_logger.error("Failed to get captcha cog")
                continue

            if guild_last_captcha_msg is not None:
                try:
                    msg = await channel.fetch_message(guild_last_captcha_msg)
                    try:
                        await msg.delete()
                    except nextcord.NotFound:
                        setup_logger.warn("Failed to delete the old captcha message since it's not found")

                except nextcord.NotFound:
                    setup_logger.warn(f"Unable to find old captcha message ({guild_last_captcha_msg})")

            await captcha_module.send_captcha_message(channel)
