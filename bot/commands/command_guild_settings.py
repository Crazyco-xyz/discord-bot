import nextcord
from nextcord.ext import commands
from bot import discord_bot

from sql.tables import DBGuildConfig

GUILD_ID = [1208037232288604250]


class GuildSettingsCommand(commands.Cog):
    def __init__(self, bot: discord_bot.Bot):
        self.bot = bot

    @nextcord.slash_command(
        name="guild",
        description="Lets you edit the guild config",
        guild_ids=GUILD_ID
    )
    async def command_guild(self, interaction: nextcord.Interaction):
        pass

    @command_guild.subcommand(
        name="admins",
        description="Set members as a guild admin in order to use the bot"
    )
    async def guild_admins(self, interaction: nextcord.Interaction):
        pass

    @guild_admins.subcommand(
        name="list",
        description="List the guild admins of your guild"
    )
    async def guild_admins_list(self, interaction: nextcord.Interaction):
        if not await self.bot.has_perms(interaction.user, interaction):
            return

        config = DBGuildConfig.from_guild_id(self.bot.db, interaction.guild.id)

        if config is None:
            config = DBGuildConfig.create(self.bot.db, interaction.guild.id)

        if not config.guild_admins:
            await interaction.response.send_message(
                embed=nextcord.Embed(
                    title="Guild Admins",
                    description="You currently have no guild admins set!",
                    color=nextcord.Color.green()
                ),
                ephemeral=True
            )
            return

        admins = [interaction.guild.get_member(i).name for i in config.guild_admins]

        await interaction.response.send_message(
            embed=nextcord.Embed(
                title="Guild Admins",
                description=f"You currently have following guild admins set!\n\n`{', '.join(admins)}`",
                color=nextcord.Color.green(),
            ),
            ephemeral=True
        )


    @guild_admins.subcommand(
        name="add",
        description="Adds a guild admin"
    )
    async def guild_admins_add(self, interaction: nextcord.Interaction, user: nextcord.Member):
        pass


def setup(bot):
    bot.add_cog(GuildSettingsCommand(bot))