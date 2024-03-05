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

GUILD_ID = [1208037232288604250]


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
    config = DBGuildConfig.from_guild_id(db=bot.db, guild_id=guild_id)

    if config is None:
        return None

    return bot.get_guild(guild_id).get_role(config.guild_captcha_role)


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
        if captcha_data is None:
            await interaction.response.send_message(
                embed=nextcord.Embed(
                    title="Captcha Failure",
                    description="Something went wrong. Please generate a new captcha"
                ),
                ephemeral=True
            )
            logger.error(f"{interaction.user.name} attempted the captcha, but there was no captcha data!")
            return

        if captcha_data.expected_solution is None:
            await interaction.response.send_message(
                embed=nextcord.Embed(
                    title="Captcha Failure",
                    description="Something went wrong. Please generate a new captcha",
                    color=nextcord.Color.red()
                ),
                ephemeral=True
            )
            return
        captcha_data.attempts += 1

        logger.info(
            f"Captcha solution submitted ({interaction.user.name}): {self.captcha_input.value} | Expected: {captcha_data.expected_solution} | Attempt: {captcha_data.attempts}")

        if self.captcha_input.value.lower() != captcha_data.expected_solution.lower():
            if captcha_data.attempts >= MAX_CAPTCHA_ATTEMPTS:
                try:
                    await interaction.user.kick(reason="Failed the captcha 3 times")
                    logger.info(
                        f"Kicked user {interaction.user.name} for failing the captcha {MAX_CAPTCHA_ATTEMPTS} times")
                except nextcord.Forbidden:
                    logger.error(
                        f"Failed to kick user {interaction.user.name} for failing the captcha: Missing Permissions")
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
        if captcha_role is None:
            logger.error(f"Invalid captcha role ({captcha_role}) set! Cannot remove from user!")
            return
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

        config = DBGuildConfig.from_guild_id(db=self.bot.db, guild_id=interaction.guild.id)

        code, data = captcha_generator.generate_captcha(
            font_path=f"{self.bot.project_root}/bot/utils/fonts/arial.ttf",
            background_color=config.guild_captcha_background_color,
            text_color=config.guild_captcha_text_color
        )

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
                captcha_generation_attempts=1,
                expected_solution=code,
                guild_id=interaction.guild.id,
                user_id=interaction.user.id
            )

        await interaction.response.send_message(
            embed=nextcord.Embed(
                title="Verify yourself",
                description="Please solve the captcha",
            ).set_image("attachment://captcha.png"),
            ephemeral=True,
            file=nextcord.File(data, filename="captcha.png"),
            view=CaptchaSolveButton(bot=self.bot)
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
                captcha_generation_attempts=1,
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

        pathlib.Path(f"{path}/captcha.wav").unlink()


class CaptchaCommand(commands.Cog):
    def __init__(self, bot: discord_bot.Bot):
        self.bot = bot

    async def send_captcha_message(self, channel: nextcord.TextChannel, delete_old=False):
        logger = self.bot.get_guild_logger(channel.guild)
        config = DBGuildConfig.from_guild_id(self.bot.db, channel.guild.id)

        if config is None:
            config = DBGuildConfig.create(self.bot.db, channel.guild.id)

        if delete_old:
            old_message = await channel.fetch_message(config.guild_captcha_last_msg)
            if old_message is None:
                logger.error(f"Failed to find old captcha message ({config.guild_captcha_last_msg})")
            else:
                try:
                    await old_message.delete()
                except nextcord.Forbidden:
                     logger.error("Failed to delete old captcha message. Insufficient permissions!")

        message = await channel.send(
            embed=nextcord.Embed(
                title=config.guild_captcha_embed_title,
                description=config.guild_captcha_embed_description
            ), view=CaptchaButtonView(self.bot)
        )

        config.guild_captcha_last_msg = message.id

    @nextcord.slash_command(
        name="captcha",
        description="Configure the captcha",
        guild_ids=GUILD_ID,
    )
    async def captcha_command(self, interaction: nextcord.Interaction) -> None:
        pass

    @captcha_command.subcommand(
        name="enable", description="Enables or disables the required captcha"
    )
    async def captcha_enable(
            self,
            interaction: nextcord.Interaction,
            enabled: int = nextcord.SlashOption(name="option", choices={"on": 1, "off": 0}),
    ) -> None:
        logger = self.bot.get_guild_logger(interaction.guild.id)

        if not await self.bot.has_perms(interaction.guild.get_member(interaction.user.id), interaction):
            return

        config = DBGuildConfig.from_guild_id(db=self.bot.db, guild_id=interaction.guild.id)

        config.guild_captcha_enabled = enabled

        logger.info(f"The captcha has been {'enabled' if enabled else 'disabled'} by {interaction.user.name}!")

        await interaction.response.send_message(
            embed=nextcord.Embed(
                title="Captcha Settings",
                description=f"You have {'enabled' if enabled else 'disabled'} the captcha requirement.",
                color=nextcord.Color.green()
            ),
            ephemeral=True
        )

    @captcha_command.subcommand(
        name="set_channel",
        description="Set the captcha channel"
    )
    async def captcha_set(
            self, interaction: nextcord.Interaction, channel: nextcord.TextChannel
    ):
        logger = self.bot.get_guild_logger(interaction.guild.id)

        if not await self.bot.has_perms(interaction.guild.get_member(interaction.user.id), interaction):
            return

        try:
            await self.send_captcha_message(channel)
        except nextcord.Forbidden:
            await interaction.response.send_message(
                embed=nextcord.Embed(
                    title="Captcha Settings",
                    description=f"Failed to send in verify message in {channel.mention} due to missing permissions.",
                    color=nextcord.Color.red()
                ),
                ephemeral=True
            )
            logger.error(f"Failed to send in verify message in channel {channel.name} ({channel.id})")
            return

        config = DBGuildConfig.from_guild_id(self.bot.db, interaction.guild.id)

        config.guild_captcha_channel = channel.id

        logger.info(f"Successfully set captcha channel to {channel.name} ({config.guild_captcha_channel})")

        await interaction.response.send_message(
            embed=nextcord.Embed(
                title="Captcha Settings",
                description=f"You have picked {channel.mention}",
                color=nextcord.Color.green(),
            ),
            ephemeral=True
        )

    @captcha_command.subcommand(
        name="create_role",
        description="Create the captcha role which will be assigned to new users",
    )
    async def captcha_create_role(self, interaction: nextcord.Interaction):
        guild = interaction.guild

        if not await self.bot.has_perms(interaction.guild.get_member(interaction.user.id), interaction):
            return

        logger = self.bot.get_guild_logger(guild)
        try:
            role = await guild.create_role(name="Captcha Required")
        except nextcord.Forbidden:
            await interaction.response.send_message(
                embed=nextcord.Embed(
                    title="Captcha Settings",
                    description="Failed to create role. Insufficient permissions.",
                    color=nextcord.Color.red(),
                ),
                ephemeral=True
            )
            logger.error("Failed to create captcha role. Insufficient permissions")
            return

        config = DBGuildConfig.from_guild_id(db=self.bot.db, guild_id=interaction.guild.id)

        if config is None:
            config = DBGuildConfig.create(db=self.bot.db, guild_id=interaction.guild.id)

        config.guild_captcha_role = role.id

        await interaction.response.send_message(
            embed=nextcord.Embed(
                title="Captcha Settings",
                description=f"Successfully created role {role.mention}!",
                color=nextcord.Color.green(),
            ),
            ephemeral=True
        )
        logger.info("Created captcha role successfully!")

    @captcha_command.subcommand(
        name="set_role",
        description="Select a captcha role"
    )
    async def captcha_set_role(self, interaction: nextcord.Interaction, role: nextcord.Role):
        logger = self.bot.get_guild_logger(interaction.guild)

        if not await self.bot.has_perms(interaction.guild.get_member(interaction.user.id), interaction):
            return

        config = DBGuildConfig.from_guild_id(db=self.bot.db, guild_id=interaction.guild.id)
        if not config:
            config = DBGuildConfig.create(db=self.bot.db, guild_id=interaction.guild.id)

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

    @captcha_command.subcommand(
        name="status",
        description="Shows the status of the captcha"
    )
    async def captcha_status(self, interaction: nextcord.Interaction):
        logger = self.bot.get_guild_logger(interaction.guild)

        if not await self.bot.has_perms(interaction.guild.get_member(interaction.user.id), interaction):
            return

        config = DBGuildConfig.from_guild_id(self.bot.db, interaction.guild.id)

        if config is None:
            await interaction.response.send_message(
                embed=nextcord.Embed(
                    title="Captcha Settings Overview",
                    description="Captchas are currently not configured"
                ),
                ephemeral=True
            )
            return

        description = (f"Captchas are currently **{'enabled' if config.guild_captcha_enabled else 'disabled'}**\n"
                       f"Captcha channel is set to {interaction.guild.get_channel(config.guild_captcha_channel).mention}\n"
                       f"Captcha role is set to {interaction.guild.get_role(config.guild_captcha_role).mention}")

        await interaction.response.send_message(
            embed=nextcord.Embed(
                title="Captcha Settings Overview",
                description=description,
                color=nextcord.Color.green()
            ),
            ephemeral=True
        )

    @captcha_command.subcommand(
        name="edit_embed",
        description="Edit various aspects of the captcha message embed"
    )
    async def edit_embed(self, interaction: nextcord.Interaction) -> None:
        pass

    @edit_embed.subcommand(
        name="title",
        description="Allows you to set a embed title for the captcha welcome message"
    )
    async def edit_embed_title(self, interaction: nextcord.Interaction, title: str):
        logger = self.bot.get_guild_logger(interaction.guild)

        if not await self.bot.has_perms(interaction.guild.get_member(interaction.user.id), interaction):
            return

        config = DBGuildConfig.from_guild_id(self.bot.db, guild_id=interaction.guild.id)

        if config is None:
            config = DBGuildConfig.create(self.bot.db, interaction.guild.id)

        logger.info(
            f"User {interaction.user.name} changed the captcha embed title from \"{config.guild_captcha_embed_title}\" to \"{title}\"")

        config.guild_captcha_embed_title = title

        await self.send_captcha_message(interaction.guild.get_channel(config.guild_captcha_channel), delete_old=True)

        await interaction.response.send_message(
            embed=nextcord.Embed(
                title="Captcha Embed Settings",
                description=f"Successfully changed the embed title to `{title}`",
                color=nextcord.Color.green()
            ),
            ephemeral=True
        )

    class CaptchaEmbedDescriptionEditor(nextcord.ui.Modal):
        def __init__(self, cog: CaptchaCommand, guild_id: int):
            super().__init__(title="Edit description of the captcha embed")

            self.cog = cog

            self.config = DBGuildConfig.from_guild_id(self.cog.bot.db, guild_id)

            self.description = nextcord.ui.TextInput(
                label="Edit description",
                style=nextcord.TextInputStyle.paragraph,
                default_value=self.config.guild_captcha_embed_description
            )

            self.add_item(self.description)

        async def callback(self, interaction: nextcord.Interaction):
            logger = self.cog.bot.get_guild_logger(interaction.guild.id)

            new_description = self.description.value

            logger.info(f"User {interaction.user.name} changed the description to \"{new_description}\"")

            self.config.guild_captcha_embed_description = new_description

            await self.cog.send_captcha_message(interaction.guild.get_channel(self.config.guild_captcha_channel),
                                            delete_old=True)

            await interaction.response.send_message(
                embed=nextcord.Embed(
                    title="Captcha Embed Settings",
                    description=f"Successfully changed description to: \n\n{new_description}",
                    color=nextcord.Color.green()
                ),
                ephemeral=True
            )

    @edit_embed.subcommand(
        name="description",
        description="Allows you to set the embed description for the captcha welcome message"
    )
    async def edit_embed_description(self, interaction: nextcord.Interaction):
        logger = self.bot.get_guild_logger(interaction.guild)

        if not await self.bot.has_perms(interaction.guild.get_member(interaction.user.id), interaction):
            return

        await interaction.response.send_modal(self.CaptchaEmbedDescriptionEditor(self, interaction.guild.id))

    @captcha_command.subcommand(
        name="edit",
        description="Allows you to edit the captcha"
    )
    async def edit_captcha(self, interaction: nextcord.Interaction):
        pass

    class CaptchaEditBackgroundColor(nextcord.ui.Modal):
        def __init__(self, cog: CaptchaCommand, guild_id: int):
            super().__init__(title="Edit the background color")

            self.cog = cog

            self.config = DBGuildConfig.from_guild_id(self.cog.bot.db, guild_id)

            raw = DBGuildConfig._convert_color_back_(self.config.guild_captcha_background_color)

            self.description = nextcord.ui.TextInput(
                label="Edit the background captcha color",
                style=nextcord.TextInputStyle.short,
                default_value=raw
            )

            self.add_item(self.description)

        async def callback(self, interaction: nextcord.Interaction):
            logger = self.cog.bot.get_guild_logger(interaction.guild.id)

            value = self.description.value

            try:
                new_value = DBGuildConfig._convert_color_(value)
            except ValueError:
                await interaction.response.send_message(
                    embed=nextcord.Embed(
                        title="Captcha Embed Settings",
                        description="Failed to set captcha background. Please use the proper format: red_value, green_value, blue_value",
                        color=nextcord.Color.red()
                    ),
                    ephemeral=True
                )
                return

            self.config.guild_captcha_background_color = new_value

            logger.info(
                f"User {interaction.user.name} changed the captcha background color to {value}")

            await interaction.response.send_message(
                embed=nextcord.Embed(
                    title="Captcha Settings",
                    description=f"Successfully changed the color to {new_value}",
                    color=nextcord.Color.from_rgb(new_value[0], new_value[1], new_value[2])
                ),
                ephemeral=True
            )

    @edit_captcha.subcommand(
        name="background_color",
        description="Allows you to edit the captcha background color"
    )
    async def edit_embed_background_color(self, interaction: nextcord.Interaction):
        logger = self.bot.get_guild_logger(interaction.guild)

        if not await self.bot.has_perms(interaction.guild.get_member(interaction.user.id), interaction):
            return

        await interaction.response.send_modal(self.CaptchaEditBackgroundColor(self, interaction.guild.id))

    class CaptchaEditTextColor(nextcord.ui.Modal):
        def __init__(self, cog: CaptchaCommand, guild_id: int):
            super().__init__(title="Edit the text color")

            self.cog = cog

            self.config = DBGuildConfig.from_guild_id(self.cog.bot.db, guild_id)

            raw = DBGuildConfig._convert_color_back_(self.config.guild_captcha_text_color)

            self.description = nextcord.ui.TextInput(
                label="Edit the captcha text color",
                style=nextcord.TextInputStyle.short,
                default_value=raw
            )

            self.add_item(self.description)

        async def callback(self, interaction: nextcord.Interaction):
            logger = self.cog.bot.get_guild_logger(interaction.guild.id)

            value = self.description.value

            try:
                new_value = DBGuildConfig._convert_color_(value)
            except ValueError:
                await interaction.response.send_message(
                    embed=nextcord.Embed(
                        title="Captcha Settings",
                        description="Failed to set captcha text color. Please use the proper format: red_value, green_value, blue_value",
                        color=nextcord.Color.red()
                    ),
                    ephemeral=True
                )
                return

            self.config.guild_captcha_background_color = new_value

            logger.info(
                f"User {interaction.user.name} changed the captcha text color to {value}")

            await interaction.response.send_message(
                embed=nextcord.Embed(
                    title="Captcha Settings",
                    description=f"Successfully changed the color to {new_value}",
                    color=nextcord.Color.from_rgb(new_value[0], new_value[1], new_value[2])
                ),
                ephemeral=True
            )

    @edit_captcha.subcommand(
        name="text_color",
        description="Allows you to edit the captcha text color"
    )
    async def edit_captcha_text_color(self, interaction: nextcord.Interaction):
        logger = self.bot.get_guild_logger(interaction.guild)

        if not await self.bot.has_perms(interaction.guild.get_member(interaction.user.id), interaction):
            return

        await interaction.response.send_modal(self.CaptchaEditTextColor(self, interaction.guild.id))

    @edit_captcha.subcommand(
        name="timeout",
        description="Users will get kicked if they don't complete the captcha in the timeout window"
    )
    async def edit_captcha_timeout(self, interaction: nextcord.Interaction, new_timeout: int):
        if not await self.bot.has_perms(interaction.user, interaction):
            return

        logger = self.bot.get_guild_logger(interaction.guild.id)

        config = DBGuildConfig.from_guild_id(self.bot.db, interaction.guild.id)

        if config is None:
            config = DBGuildConfig.create(self.bot.db, interaction.guild.id)

        config.guild_captcha_timeout = new_timeout
        logger.info(f"User {interaction.user.name} changed the captcha timeout to {new_timeout} minutes")

        await interaction.response.send_message(
            embed=nextcord.Embed(
                title="Captcha Settings",
                description=f"Successfully set the timeout to {new_timeout}"
            ),
            ephemeral=True
        )


async def setup(bot: discord_bot.Bot):
    bot.add_cog(CaptchaCommand(bot))
