import nextcord
from nextcord.ext import commands

from bot.commands import command_captcha

from sql.tables import DBGuildConfig

import main


class OnJoinListener(commands.Cog):
    def __init__(self, bot):
        self.bot: main.Bot = bot
        print("OnJoinListener loaded")

    @commands.Cog.listener()
    async def on_member_join(self, member: nextcord.Member):
        logger = self.bot.get_guild_logger(member.guild)
        config = DBGuildConfig.from_guild_id(db=self.bot.db, guild_id=member.guild.id)
        logger.info(f"A new member just joined: {member.name}.{' Applying captcha role' if config.guild_captcha_enabled else ''}")

        if config.guild_captcha_enabled:

            role = member.guild.get_role(config.guild_captcha_role)

            if role is None:
                logger.error(f"Failed to give out role: Role with id {config.guild_captcha_role} not found!")
                return

            await member.add_roles(role, reason="Needs to complete a captcha")
            data = command_captcha.CaptchaData.from_user_and_guild_id(member.id, member.guild.id)
            if data is not None:
                data.delete()
            logger.info(f"Added role {role.name} to {member.name}!")

def setup(bot):
    bot.add_cog(OnJoinListener(bot))
