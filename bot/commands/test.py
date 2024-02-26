import discord
from discord.ext.commands import Cog
from discord import app_commands

class TestCommand(Cog):
    def __init__(self, bot):
        self.bot = bot

    @app_commands.command(name="test", description="Testing test test")
    async def test_command(self, interaction: discord.Interaction):
        await interaction.response.send_message("Response!")