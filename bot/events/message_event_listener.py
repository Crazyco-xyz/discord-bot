import discord


async def on_message(bot: discord.Client, message: discord.Message):
    print(message.content)