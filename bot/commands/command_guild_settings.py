from nextcord.ext import commands
from bot import discord_bot


class GuildSettingsCommand(commands.Cog):
    def __init__(self, bot: discord_bot.Bot):
        self.bot = bot


def setup(bot):
    bot.add_cog(GuildSettingsCommand(bot))