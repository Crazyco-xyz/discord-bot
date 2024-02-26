import pathlib

import sqlite3

root_dir = pathlib.Path(__file__).parent

database_dir_path = pathlib.Path(f"{root_dir}/database")

database_file_path = pathlib.Path(f"{database_dir_path}/database.db")


def create_db():
    if not database_dir_path.exists():
        database_dir_path.mkdir()

    if not database_file_path.exists():
        db = sqlite3.connect(f"{database_file_path}")
        cursor = db.cursor()

        query = ("create table config_global ("
                 "bot_token varchar(100),"
                 "admins_global LONGTEXT"
                 ");")

        cursor.execute(query)

        print("Created global config table")

        query = ("create table config_guilds ("
                 "id integer "
                 "  constraint config_guilds_pk"
                 "      primary key autoincrement,"
                 "guild_name varchar(100),"
                 "guild_id integer"
                 ");")

        cursor.execute(query)

        db.commit()
        db.close()


create_db()
