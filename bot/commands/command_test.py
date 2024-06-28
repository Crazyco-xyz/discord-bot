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
            "https://media.discordapp.net/attachments/1112030896728584243/1256189308864565269/GWEG4Fe.jpg?ex=667fdcf6&is=667e8b76&hm=aac28345455eec5be201d42538cc53459f2323c86987fde37497fca4dbf229fe&=&format=webp&width=513&height=549"
        )


async def setup(bot):
    bot.add_cog(TestCommand(bot))
