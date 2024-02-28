import nextcord
from nextcord.ext import commands
from bot import discord_bot


class TestCommand(commands.Cog):
    def __init__(self, bot: discord_bot.Bot):
        self.bot = bot

    @nextcord.slash_command(
        name="test", description="Testing test test", guild_ids=[1208037232288604250]
    )
    async def test_command(self, interaction: nextcord.Interaction) -> None:
        await interaction.response.send_message("test response")

    @nextcord.slash_command(
        name="human_rights",
        description="Does the bot believe in human rights?",
        guild_ids=[1208037232288604250],
    )
    async def human_rights_command(self, interaction: nextcord.Interaction) -> None:
        await interaction.response.send_message(
            "https://media.discordapp.net/attachments/1209986210995638352/1210058400466083900/ydH7aKdd.gif"
        )


async def setup(bot):
    bot.add_cog(TestCommand(bot))
