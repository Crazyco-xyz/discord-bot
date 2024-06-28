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
            "https://tenor.com/view/racoon-raccoon-raccoon-in-a-circle-silly-raccooon-dancing-raccoon-gif-402674747635664052"
        )


async def setup(bot):
    bot.add_cog(TestCommand(bot))
