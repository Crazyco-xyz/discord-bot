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
            id                              int auto_increment,
            guild_id                        BIGINT    null,
            guild_captcha_channel           BIGINT    null,
            guild_captcha_role              BIGINT    null,
            guild_last_captcha_msg          BIGINT    null,
            guild_captcha_background_color  varchar(100) default '255, 0, 255' not null,
            guild_captcha_text_color        varchar(100) default '90, 90, 90' not null,
            guild_captcha_embed_title       longtext  null,
            guild_captcha_embed_description longtext  null,
            guild_captcha_enabled           bit default 0 not null,
            guild_log_retention             int default 30 not null,
            
            constraint config_guilds_pk
                primary key (id)
        );
    """

    db.execute(sql)

    print("Created guild config table")

    sql = """
    create table guild_logs (
        id              int auto_increment,
        guild_id        bigint null,
        log_level       varchar(100),
        log_date_added  datetime,
        log_content     longtext,
        
        constraint guild_logs_pk
            primary key (id)
    )
    """

    db.execute(sql)
    print("Created guild logs table")

    bot_token = input("Bot token please: ")

    sql = "insert into config_global (bot_token, admins_global) values (%(token)s, %(admins)s)"

    db.execute(sql, {"token": bot_token, "admins": ""})

    db.close()


if __name__ == "__main__":
    load_dotenv()
    create_db()
