import discord
from discord import app_commands
from discord.ext import commands

import main


class CaptchaCommand(commands.Cog):
    def __init__(self, bot: main.Bot):
        self.bot = bot

    @app_commands.command(
        name="captcha",
        description="Configure the captcha"
    )
    async def captcha_command(self, interaction: discord.Interaction):
        await interaction.response.send_message("Captcha response")


async def setup(bot: main.Bot):
    await bot.add_cog(CaptchaCommand(bot))
