import nextcord
from nextcord.ext import commands

import main


class OnJoinListener(commands.Cog):
    def __init__(self, bot):
        self.bot: main.Bot = bot
        print("OnJoinListener loaded")

    @commands.Cog.listener()
    async def on_member_join(self, member: nextcord.Member):
        print(f"A new member just joined: {member.name}. Applying captcha role")
        sql = "select guild_captcha_role from config_guilds where guild_id = %(id)s"
        result = self.bot.db.execute(sql, {"id": member.guild.id})

        if not result:
            # no entry in the config_guilds table yet
            pass

        role_id = result[0][0]

        if not role_id:
            # captcha role has not been set
            pass

        role = member.guild.get_role(role_id)

        if role is None:
            print(f"Failed to give out role: Role with id {role_id} not found!")
            return

        await member.add_roles(role, reason="Needs to complete a captcha")
        print(f"Added role {role.name} to {member.name}!")

def setup(bot):
    bot.add_cog(OnJoinListener(bot))
