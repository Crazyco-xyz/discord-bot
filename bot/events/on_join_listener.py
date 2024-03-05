import asyncio

import nextcord
from nextcord.ext import commands

from bot.commands import command_captcha

from sql.tables import DBGuildConfig

import main


class OnJoinListener(commands.Cog):
    def __init__(self, bot):
        self.bot: main.Bot = bot
        print("OnJoinListener loaded")

    async def remove_user_if_not_completed_captcha(self, member: nextcord.Member):
        logger = self.bot.get_guild_logger(member.guild.id)
        config = DBGuildConfig.from_guild_id(self.bot.db, member.guild.id)

        if config is None:
            config = DBGuildConfig.create(self.bot.db, member.guild.id, refetch_data=True)

        captcha_role = member.guild.get_role(config.guild_captcha_role)

        if captcha_role is None:
            logger.warn(f"Failed to find the captcha role ({config.guild_captcha_role}), skipping the timeout")
            return

        logger.info(f"Waiting for {config.guild_captcha_timeout} mintues to see if user {member.name} has solved the captcha")

        await asyncio.sleep(config.guild_captcha_timeout * 60)

        captcha_role = member.guild.get_role(config.guild_captcha_role)

        if captcha_role is None:
            logger.warn("Could not find captcha role after timeout, cannot determine if user has completed captcha!")
            return

        for role in member.roles:
            if role.id == captcha_role.id:
                logger.info(
                    f"User {member.name} still has the captcha role after {config.guild_captcha_timeout} minutes. Kicking...")
                try:
                    await member.kick(reason="Did not complete captcha in time!")
                    logger.info(f"Kicked user {member.name} for not completing the captcha in time.")
                except nextcord.Forbidden:
                    logger.error(f"Cannot kick user {member.name}, insufficient permissions!")
                return

        logger.info(f"User {member.name} does not have the captcha role anymore")

    @commands.Cog.listener()
    async def on_member_join(self, member: nextcord.Member):
        logger = self.bot.get_guild_logger(member.guild)
        config = DBGuildConfig.from_guild_id(db=self.bot.db, guild_id=member.guild.id)
        logger.info(
            f"A new member just joined: {member.name}.{' Applying captcha role' if config.guild_captcha_enabled else ''}")

        if config.guild_captcha_enabled:

            role = member.guild.get_role(config.guild_captcha_role)

            if role is None:
                logger.error(f"Failed to give out role: Role with id {config.guild_captcha_role} not found!")
                return

            await member.add_roles(role, reason="Needs to complete a captcha")
            data = command_captcha.CaptchaData.from_user_and_guild_id(member.id, member.guild.id)
            if data is not None:
                data.delete()
            self.bot.loop.create_task(self.remove_user_if_not_completed_captcha(member))
            logger.info(f"Added role {role.name} to {member.name}!")


def setup(bot):
    bot.add_cog(OnJoinListener(bot))
