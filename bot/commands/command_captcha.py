import nextcord
from nextcord.ext import commands

import main

from bot.utils import captcha_generator


class CaptchaButtonView(nextcord.ui.View):
    @nextcord.ui.button(label="Verify", style=nextcord.ButtonStyle.primary)
    async def on_click(self, button, interaction):
        code, data = captcha_generator.generate_captcha()
        await interaction.response.send_message(
            embed=nextcord.Embed(
                title="Verify yourself",
                description="Please solve the captcha",
            ).set_image("attachment://captcha.png"),
            ephemeral=True,
            file=nextcord.File(data, filename="captcha.png")
        )


class CaptchaCommand(commands.Cog):
    def __init__(self, bot: main.Bot):
        self.bot = bot

    async def send_captcha_message(self, channel):
        message = await channel.send(
            embed=nextcord.Embed(
                title="Beep-Boop, are you human?",
                description="Hit the button below to verify yourself"
            ), view=CaptchaButtonView()
        )

        sql = "select guild_last_captcha_msg from config_guilds where guild_id = %(id)s"
        result = self.bot.db.execute(sql, {"id": channel.guild.id})

        if not result:
            sql = "insert into config_guilds (guild_id, guild_captcha_channel, guild_last_captcha_msg) values (%(id)s, %(channel)s, %(msg)s)"

        else:
            sql = "update config_guilds set guild_last_captcha_msg = %(msg)s where guild_id = %(id)s"

        self.bot.db.execute(sql, {"id": channel.guild.id, "channel": channel.id, "msg": message.id})

    @nextcord.slash_command(
        name="captcha",
        description="Configure the captcha",
        guild_ids=[1208037232288604250],
    )
    async def captcha_command(self, interaction: nextcord.Interaction) -> None:
        pass

    @captcha_command.subcommand(
        name="enable", description="Enables or disables the required captcha"
    )
    async def captcha_enable(
            self,
            interaction: nextcord.Interaction,
            choice: int = nextcord.SlashOption(name="option", choices={"on": 1, "off": 0}),
    ) -> None:
        await interaction.response.send_message(
            f"You have {'enabled' if choice else 'disabled'} the captcha requirement."
        )

    @captcha_command.subcommand(
        name="set_channel", description="Set the captcha channel"
    )
    async def captcha_set(
            self, interaction: nextcord.Interaction, channel: nextcord.TextChannel
    ):
        sql = f"select * from config_guilds where guild_id = %(id)s"
        result = self.bot.db.execute(sql, {"id": interaction.guild.id})
        if not result:
            sql = "insert into config_guilds (guild_id, guild_captcha_channel) VALUES (%(id)s, %(channel)s)"

        else:
            sql = "update config_guilds set guild_captcha_channel = %(channel)s where guild_id = %(id)s"

        self.bot.db.execute(sql, {"id": interaction.guild.id, "channel": channel.id})

        self.bot.db.commit()

        try:
            await self.send_captcha_message(channel)
        except nextcord.Forbidden:
            await interaction.response.send_message(
                embed=nextcord.Embed(
                    title="Captcha Settings",
                    description=f"Failed to send in verify message in {channel.mention} due to missing permissions.",
                    color=nextcord.Color.red()
                )
            )

            return

        await interaction.response.send_message(
            embed=nextcord.Embed(
                title="Captcha Settings",
                description=f"You have picked {channel.mention}",
                color=nextcord.Color.green(),
            )
        )


    @captcha_command.subcommand(
        name="create_role",
        description="Create the captcha role which will be assigned to new users",
    )
    async def captcha_create_role(self, interaction: nextcord.Interaction):
        guild = interaction.guild
        try:
            role = await guild.create_role(name="Captcha Required")
        except nextcord.Forbidden:
            await interaction.response.send_message(
                embed=nextcord.Embed(
                    title="Captcha Settings",
                    description="Failed to create role. Insufficient permissions.",
                    color=nextcord.Color.red(),
                )
            )
            print("Failed to create captcha role. Insufficient permissions")
            return

        sql = "select * from config_guilds where guild_id = %(id)s"
        result = self.bot.db.execute(sql, {"id": guild.id})

        if not result:
            sql = "insert into config_guilds (guild_id, guild_captcha_role) VALUES (%(id)s, %(role)s)"

        else:
            sql = "update config_guilds set guild_captcha_role = %(role)s where guild_id = %(id)s"

        self.bot.db.execute(sql, {"id": guild.id, "role": role.id}, commit=True)

        await interaction.response.send_message(
            embed=nextcord.Embed(
                title="Captcha Settings",
                description=f"Successfully created role {role.mention}!",
                color=nextcord.Color.green(),
            )
        )


async def setup(bot: main.Bot):
    bot.add_cog(CaptchaCommand(bot))
