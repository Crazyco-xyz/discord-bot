from __future__ import annotations

import nextcord
from nextcord.ext import commands

import pathlib

import dataclasses

from bot.utils import captcha_generator
from bot import discord_bot

from sql.tables import DBGuildConfig

GUILD_USER_ID_CAPTCHA_MAP: dict[str, CaptchaData] = {}

MAX_CAPTCHA_ATTEMPTS = 3


@dataclasses.dataclass
class CaptchaData:
    user_id: int
    guild_id: int
    attempts: int
    captcha_generation_attempts: int
    expected_solution: str

    def delete(self):
        GUILD_USER_ID_CAPTCHA_MAP.pop(f"{self.guild_id}-{self.user_id}")

    @staticmethod
    def from_user_and_guild_id(user_id: int, guild_id: int) -> CaptchaData:
        return GUILD_USER_ID_CAPTCHA_MAP.get(f"{guild_id}-{user_id}")


def get_captcha_role(bot: discord_bot.Bot, guild_id: int) -> [nextcord.Role | None]:
    sql = "select guild_captcha_role from config_guilds where guild_id = %(id)s"
    result = bot.db.execute(sql, {"id": guild_id})

    if not result:
        return None

    if not result[0][0]:
        return None

    return bot.get_guild(guild_id).get_role(result[0][0])


class CaptchaSolveModal(nextcord.ui.Modal):

    def __init__(self, bot: discord_bot.Bot):
        super().__init__(title="Captcha Solution")

        self.captcha_input = nextcord.ui.TextInput(
            label="Solution",
            style=nextcord.TextInputStyle.short,
            required=True,
            max_length=captcha_generator.CAPTCHA_CODE_LENGTH
        )

        self.bot = bot

        self.add_item(self.captcha_input)

    async def callback(self, interaction: nextcord.Interaction):
        logger = self.bot.get_guild_logger(interaction.guild)

        captcha_data = CaptchaData.from_user_and_guild_id(interaction.user.id, interaction.guild.id)
        if captcha_data.expected_solution is None:
            await interaction.response.send_message(
                embed=nextcord.Embed(
                    title="Captcha Failure",
                    description="Something is seriously wrong. Maybe try again?",
                    color=nextcord.Color.red()
                ),
                ephemeral=True
            )
            return
        captcha_data.attempts += 1

        print(
            f"Captcha solution submitted: {self.captcha_input.value} | Expected: {captcha_data.expected_solution} | Attempt: {captcha_data.attempts}")

        if self.captcha_input.value != captcha_data.expected_solution:
            if captcha_data.attempts >= MAX_CAPTCHA_ATTEMPTS:
                try:
                    await interaction.user.kick(reason="Failed the captcha 3 times")
                    logger.info(f"Kicked user {interaction.user.name} for failing the captcha {MAX_CAPTCHA_ATTEMPTS} times")
                except nextcord.Forbidden:
                    logger.error(f"Failed to kick user {interaction.user.name} for failing the captcha: Missing Permissions")
                return

            await interaction.response.send_message(
                embed=nextcord.Embed(
                    title="Captcha Failed",
                    description="Unfortunately you failed the captcha. Please try again",
                    color=nextcord.Color.red()
                ),
                ephemeral=True
            )
            return

        captcha_data.delete()
        captcha_role = get_captcha_role(self.bot, interaction.guild.id)
        await interaction.user.remove_roles(captcha_role, reason="Passed captcha")
        logger.info(f"{interaction.user.name} has passed the captcha")


class CaptchaSolveButton(nextcord.ui.View):
    def __init__(self, bot: discord_bot.Bot):
        self.bot = bot
        super().__init__()

    @nextcord.ui.button(label="Submit Solution", style=nextcord.ButtonStyle.primary)
    async def on_click(self, button: nextcord.Button, interaction: nextcord.Interaction):
        await interaction.response.send_modal(CaptchaSolveModal(bot=self.bot))


class CaptchaButtonView(nextcord.ui.View):
    def __init__(self, bot):
        self.bot: discord_bot.Bot = bot
        super().__init__(timeout=None)

    @nextcord.ui.button(label="Verify", style=nextcord.ButtonStyle.primary)
    async def on_click(self, button, interaction: nextcord.Interaction):
        logger = self.bot.get_guild_logger(interaction.guild)

        code, data = captcha_generator.generate_captcha(f"{self.bot.project_root}/bot/utils/fonts/arial.ttf")
        await interaction.response.send_message(
            embed=nextcord.Embed(
                title="Verify yourself",
                description="Please solve the captcha",
            ).set_image("attachment://captcha.png"),
            ephemeral=True,
            file=nextcord.File(data, filename="captcha.png"),
            view=CaptchaSolveButton(bot=self.bot)
        )

        result = CaptchaData.from_user_and_guild_id(interaction.user.id, interaction.guild.id)

        if result is not None:
            result.expected_solution = code
            result.captcha_generation_attempts += 1

            if result.captcha_generation_attempts > MAX_CAPTCHA_ATTEMPTS:
                await interaction.user.kick(reason=f"Generated too many captchas ({MAX_CAPTCHA_ATTEMPTS})")
                logger.info(f"Kicked user {interaction.user.name} for generating too many captchas ({MAX_CAPTCHA_ATTEMPTS})")
                result.delete()
        else:
            GUILD_USER_ID_CAPTCHA_MAP[f"{interaction.guild.id}-{interaction.user.id}"] = CaptchaData(
                attempts=0,
                captcha_generation_attempts=0,
                expected_solution=code,
                guild_id=interaction.guild.id,
                user_id=interaction.user.id
            )

    @nextcord.ui.button(label="Verify (audio)", style=nextcord.ButtonStyle.primary)
    async def on_click_audio(self, button, interaction: nextcord.Interaction):
        logger = self.bot.get_guild_logger(interaction.guild)

        path = f"{self.bot.project_root}/data/captcha/audio/{interaction.guild.id}/{interaction.user.id}"
        pathlib.Path(path).mkdir(parents=True, exist_ok=True)
        code = captcha_generator.generate_audio(f"{path}/captcha.wav")

        result = CaptchaData.from_user_and_guild_id(interaction.user.id, interaction.guild.id)

        if result is not None:
            result.expected_solution = code
            result.captcha_generation_attempts += 1

            if result.captcha_generation_attempts > MAX_CAPTCHA_ATTEMPTS:
                await interaction.user.kick(reason=f"Generated too many captchas ({MAX_CAPTCHA_ATTEMPTS})")
                logger.info(
                    f"Kicked user {interaction.user.name} for generating too many captchas ({MAX_CAPTCHA_ATTEMPTS})")
                result.delete()
        else:
            GUILD_USER_ID_CAPTCHA_MAP[f"{interaction.guild.id}-{interaction.user.id}"] = CaptchaData(
                attempts=0,
                captcha_generation_attempts=0,
                expected_solution=code,
                guild_id=interaction.guild.id,
                user_id=interaction.user.id
            )

        await interaction.response.send_message(
            embed=nextcord.Embed(
                title="Verify yourself",
                description="Please solve the captcha"
            ),
            ephemeral=True,
            file=nextcord.File(f"{path}/captcha.wav"),
            view=CaptchaSolveButton(bot=self.bot)
        )


class CaptchaCommand(commands.Cog):
    def __init__(self, bot: discord_bot.Bot):
        self.bot = bot

    async def send_captcha_message(self, channel):
        message = await channel.send(
            embed=nextcord.Embed(
                title="Beep-Boop, are you human?",
                description="Hit the button below to verify yourself"
            ), view=CaptchaButtonView(self.bot)
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

        logger = self.bot.get_guild_logger(interaction.guild.id)
        config = DBGuildConfig.from_guild_id(self.bot, interaction.guild.id)

        if config is None:
            config = DBGuildConfig.create(
                bot=self.bot,
                guild_id=interaction.guild.id
            )

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

        config.guild_captcha_channel = channel.id

        logger.info(f"Successfully set captcha channel to {channel.name} ({channel.id})")

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

        logger = self.bot.get_guild_logger(guild)
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
            logger.error("Failed to create captcha role. Insufficient permissions")
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
        logger.info("Created captcha role successfully!")

    @captcha_command.subcommand(
         name="set_role",
         description="Select a captcha role"
    )
    async def captcha_set_role(self, interaction: nextcord.Interaction, role: nextcord.Role):
        logger = self.bot.get_guild_logger(interaction.guild)

        config = DBGuildConfig.from_guild_id(bot=self.bot, guild_id=interaction.guild.id)
        if not config:
            config = DBGuildConfig.create(bot=self.bot, guild_id=interaction.guild.id)

        config.guild_captcha_role = role.id

        logger.info(f"Successfully set captcha role to {role.name} ({role.id})")
        await interaction.response.send_message(
            embed=nextcord.Embed(
                title="Captcha Settings",
                description=f"Successfully set the captcha role to {role.mention}!",
                color=nextcord.Color.green()
            ),
            ephemeral=True
        )


async def setup(bot: discord_bot.Bot):
    bot.add_cog(CaptchaCommand(bot))
