from __future__ import annotations

import dataclasses

from sql.database import Database


@dataclasses.dataclass
class DBGuildConfig:
    _db: Database
    _id: int = None
    _guild_id: int = None
    _guild_captcha_channel: int = None
    _guild_captcha_role: int = None
    _guild_captcha_last_msg: int = None
    _guild_captcha_background_color: str = None
    _guild_captcha_text_color: str = None
    _guild_captcha_embed_title: str = None
    _guild_captcha_embed_description: str = None
    _guild_captcha_enabled: bool = None
    _guild_captcha_timeout: int = None
    _guild_log_retention: int = None
    _guild_admins: str = None

    @staticmethod
    def _convert_color_(string: str) -> tuple[int, int, int]:
        red, green, blue = string.split(",")
        red = int(red.strip())
        green = int(green.strip())
        blue = int(blue.strip())

        return red, green, blue

    @staticmethod
    def _convert_color_back_(rgb: tuple[int, int, int]):
        red, green, blue = rgb
        return ", ".join([str(red), str(green), str(blue)])

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
    def guild_captcha_last_msg(self):
        return self._guild_captcha_last_msg

    @guild_captcha_last_msg.setter
    def guild_captcha_last_msg(self, value: int):
        self._guild_captcha_last_msg = value
        self._update(guild_captcha_last_msg=value)

    @property
    def guild_captcha_background_color(self) -> tuple[int, int, int] | None:
        """
        :return: The RGB value of the captcha background
        """
        if self._guild_captcha_background_color is None:
            return None

        return DBGuildConfig._convert_color_(self._guild_captcha_background_color)

    @guild_captcha_background_color.setter
    def guild_captcha_background_color(self, value: tuple[int, int, int]):
        db_string = DBGuildConfig._convert_color_back_(value)
        self._guild_captcha_background_color = db_string
        self._update(guild_captcha_background_color=db_string)

    @property
    def guild_captcha_text_color(self):
        if self._guild_captcha_text_color is None:
            return None

        return DBGuildConfig._convert_color_(self._guild_captcha_text_color)

    @guild_captcha_text_color.setter
    def guild_captcha_text_color(self, value: tuple[int, int, int]):
        red, green, blue = value
        db_string = ", ".join([str(red), str(green), str(blue)])
        self._guild_captcha_text_color = db_string
        self._update(guild_captcha_text_color=db_string)

    @property
    def guild_captcha_embed_title(self):
        return self._guild_captcha_embed_title

    @guild_captcha_embed_title.setter
    def guild_captcha_embed_title(self, value: str):
        self._guild_captcha_embed_title = value
        self._update(guild_captcha_embed_title=value)

    @property
    def guild_captcha_embed_description(self):
        return self._guild_captcha_embed_description

    @guild_captcha_embed_description.setter
    def guild_captcha_embed_description(self, value: str):
        self._guild_captcha_embed_description = value
        self._update(guild_captcha_embed_description=value)

    @property
    def guild_captcha_enabled(self):
        return self._guild_captcha_enabled

    @guild_captcha_enabled.setter
    def guild_captcha_enabled(self, value: bool):
        self._guild_captcha_enabled = value
        self._update(guild_captcha_enabled=value)

    @property
    def guild_captcha_timeout(self):
        return self._guild_captcha_timeout

    @guild_captcha_timeout.setter
    def guild_captcha_timeout(self, value: int):
        self._guild_captcha_timeout = value
        self._update(guild_captcha_timeout=value)

    @property
    def guild_log_retention(self):
        return self._guild_log_retention

    @guild_log_retention.setter
    def guild_log_retention(self, value: int):
        self._guild_log_retention = value
        self._update(guild_log_retention=value)

    @property
    def guild_admins(self) -> list[int]:
        admins = []
        if self._guild_admins is None:
            return admins

        for entry in self._guild_admins.split(","):
            entry = entry.strip()
            admins.append(int(entry))

        return admins

    @guild_admins.setter
    def guild_admins(self, value: list[int]):
        db_string = ", ".join([str(i) for i in value])
        self._guild_admins = db_string
        self._update(guild_admins=db_string)

    def _update(
            self,
            guild_captcha_channel: int = None,
            guild_captcha_role: int = None,
            guild_captcha_last_msg: int = None,
            guild_captcha_background_color: str = None,
            guild_captcha_text_color: str = None,
            guild_captcha_embed_title: str = None,
            guild_captcha_embed_description: str = None,
            guild_captcha_enabled: bool = None,
            guild_captcha_timeout: int = None,
            guild_log_retention: int = None,
            guild_admins: str = None
    ):
        variables = {
            "guild_captcha_channel": guild_captcha_channel,
            "guild_captcha_role": guild_captcha_role,
            "guild_captcha_last_msg": guild_captcha_last_msg,
            "guild_captcha_background_color": guild_captcha_background_color,
            "guild_captcha_text_color": guild_captcha_text_color,
            "guild_captcha_embed_title": guild_captcha_embed_title,
            "guild_captcha_embed_description": guild_captcha_embed_description,
            "guild_captcha_enabled": guild_captcha_enabled,
            "guild_captcha_timeout": guild_captcha_timeout,
            "guild_log_retention": guild_log_retention,
            "guild_admins": guild_admins,
        }

        new_vars = {}

        for key, value in variables.items():
            if value is not None:
                new_vars[key] = value

        set_operations = [f"{var}=%({var})s" for var in new_vars.keys()]

        variables["guild_id"] = self.guild_id

        sql = f"update config_guilds set {', '.join(set_operations)} where guild_id=%(guild_id)s"

        print(f"{sql=}, {variables=}")

        self._db.execute(sql, variables)

    @staticmethod
    def create(
            db: Database,
            guild_id: int,
            refetch_data=False
    ):
        config = DBGuildConfig(
            _db=db,
            _guild_id=guild_id
        )

        config._create()
        if not refetch_data:
            return config

        return DBGuildConfig.from_guild_id(db, guild_id)

    def _create(self):
        variables = {
            "guild_id": self._guild_id
        }

        sql = f"insert into config_guilds(guild_id) values (%(guild_id)s)"
        self._db.execute(sql, variables)

    @staticmethod
    def from_guild_id(db: Database, guild_id: int):
        sql = "select * from config_guilds where guild_id=%(id)s"
        result: tuple = db.execute(sql, {"id": guild_id})

        if not result:
            return None

        return DBGuildConfig(
            db,
            *result[0]
        )
