from datetime import datetime


class Logger:
    def __init__(self, guild_id: int, bot):
        self.guild_id = guild_id
        self.bot = bot

    def _log_(self, level: str, message: str):
        now = datetime.now()
        formatted = now.strftime("%Y-%m-%d %H:%M:%S")
        print(f"[{formatted}] [{self.guild_id}] [{level}] - {message}")

        sql = "insert into guild_logs (guild_id, log_level, log_date_added, log_content) VALUES (%(id)s, %(level)s, %(date)s, %(content)s)"
        self.bot.db.execute(sql, {"id": self.guild_id, "level": level, "date": formatted, "content": message})

    def info(self, message: str):
        self._log_("info", message)

    def warn(self, message: str):
        self._log_("warning", message)

    def error(self, message: str):
        self._log_("error", message)

    def debug(self, message: str):
        self._log_("debug", message)
