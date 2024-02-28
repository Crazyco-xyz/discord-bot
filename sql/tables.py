import dataclasses
from bot import discord_bot


@dataclasses.dataclass
class DBGuildConfig:
    _bot: discord_bot.Bot
    _id: int = None
    _guild_id: int = None
    _guild_captcha_channel: int = None
    _guild_captcha_role: int = None
    _guild_last_captcha_msg: int = None
    _guild_log_retention: int = 30

    @property
    def guild_id(self):
        return self._guild_id

    @property
    def guild_captcha_role(self):
        return self._guild_captcha_role

    @guild_captcha_role.setter
    def guild_captcha_role(self, value: int):
        self._guild_captcha_role = value
        self._update(guild_captcha_role=value)

    @property
    def guild_captcha_channel(self):
        return self._guild_captcha_channel

    @guild_captcha_channel.setter
    def guild_captcha_channel(self, value: int):
        self._guild_captcha_channel = value
        self._update(guild_captcha_channel=value)

    @property
    def guild_last_captcha_msg(self):
        return self._guild_last_captcha_msg

    @guild_last_captcha_msg.setter
    def guild_last_captcha_msg(self, value: int):
        self._guild_last_captcha_msg = value
        self._update(guild_last_captcha_msg=value)

    @property
    def guild_log_retention(self):
        return self._guild_log_retention

    @guild_log_retention.setter
    def guild_log_retention(self, value: int):
        self._guild_log_retention = value
        self._update(guild_log_retention=value)

    def _update(
            self,
            guild_captcha_channel: int = None,
            guild_captcha_role: int = None,
            guild_last_captcha_msg: int = None,
            guild_log_retention: int = None
    ):
        variables = {}

        if guild_captcha_channel:
            variables["guild_captcha_channel"] = guild_captcha_channel

        if guild_captcha_role:
            variables["guild_captcha_role"] = guild_captcha_role

        if guild_last_captcha_msg:
            variables["guild_last_captcha_msg"] = guild_last_captcha_msg

        if guild_log_retention:
            variables["guild_log_retention"] = guild_log_retention

        set_operations = [f"{key}=%({key})s" for key in variables.keys()]

        variables["guild_id"] = self.guild_id

        sql = f"update config_guilds set {', '.join(set_operations)} where guild_id=%(guild_id)s"
        self._bot.db.execute(sql, variables)

    @staticmethod
    def create(
            bot,
            guild_id: int
    ):
        config = DBGuildConfig(
            _bot=bot,
            _guild_id=guild_id
        )

        config._create()

        return DBGuildConfig

    def _create(self):
        variables = {
            "guild_id": self._guild_id
        }

        sql = f"insert into config_guilds(guild_id) values (%(guild_id)s)"
        self._bot.db.execute(sql, variables)

    @staticmethod
    def from_guild_id(bot, guild_id: int):
        sql = "select * from config_guilds where guild_id=%(id)s"
        result = bot.db.execute(sql, {"id": guild_id})

        if result is None:
            return DBGuildConfig(_bot=bot)

        id, guild_id, guild_captcha_channel, guild_captcha_role, guild_last_captcha_msg, guild_log_retention = result[0]

        return DBGuildConfig(
            _bot=bot,
            _id=id,
            _guild_id=guild_id,
            _guild_captcha_channel=guild_captcha_channel,
            _guild_captcha_role=guild_captcha_role,
            _guild_last_captcha_msg=guild_last_captcha_msg,
            _guild_log_retention=guild_log_retention
        )
