import pathlib
from dotenv import load_dotenv
from sql.database import Database

root_dir = pathlib.Path(__file__).parent


def create_db():
    db = Database()
    sql = (
        "create table config_global ("
        "bot_token varchar(100),"
        "admins_global LONGTEXT"
        ");"
    )

    db.execute(sql)

    print("Created global config table")

    sql = """create table config_guilds
        (
            id                    int auto_increment,
            guild_id               BIGINT    null,
            guild_captcha_channel  BIGINT    null,
            guild_captcha_role     BIGINT    null,
            guild_last_captcha_msg BIGINT    null,
            constraint config_guilds_pk
                primary key (id)
        );
    """

    db.execute(sql)

    db.commit()

    print("Created guild config table")

    bot_token = input("Bot token please: ")

    sql = "insert into config_global (bot_token, admins_global) values (%(token)s, %(admins)s)"

    db.execute(sql, {"token": bot_token, "admins": ""})

    db.close()


if __name__ == "__main__":
    load_dotenv()
    create_db()
