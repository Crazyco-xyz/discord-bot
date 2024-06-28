# bot.py
import nextcord
from nextcord.ext import commands
import os
from dotenv import load_dotenv
import mysql.connector

load_dotenv()
TOKEN = os.getenv('DISCORD_TOKEN')
DB_HOST = os.getenv('DB_HOST')
DB_USER = os.getenv('DB_USER')
DB_PASSWORD = os.getenv('DB_PASSWORD')
DB_NAME = os.getenv('DB_NAME')

intents = nextcord.Intents.default()
intents.members = True  # Enable member intents

bot = commands.Bot(command_prefix='!', intents=intents)

# Database connection
def get_db_connection():
    return mysql.connector.connect(
        host=DB_HOST,
        user=DB_USER,
        password=DB_PASSWORD,
        database=DB_NAME
    )

bot.db = get_db_connection()

# Load cogs
initial_extensions = [
    'bot.cogs.on_join', 
    'bot.cogs.custom_commands', 
    'bot.commands.command_guild_settings',
    'bot.commands.command_test',
    'bot.commands.command_captcha',
    'bot.events.on_join_listener'
]

if __name__ == '__main__':
    for extension in initial_extensions:
        bot.load_extension(extension)

bot.run(TOKEN)
