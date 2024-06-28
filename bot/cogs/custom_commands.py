import nextcord
from nextcord.ext import commands

class CustomCommands(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.db = bot.db

    @commands.command(name='addcommand')
    @commands.has_permissions(administrator=True)
    async def add_custom_command(self, ctx, command_name, *, response):
        connection = self.db
        cursor = connection.cursor()
        cursor.execute("INSERT INTO custom_commands (server_id, command_name, response) VALUES (%s, %s, %s)",
                       (ctx.guild.id, command_name, response))
        connection.commit()
        cursor.close()
        await ctx.send(f'Custom command `{command_name}` added.')

    @commands.Cog.listener()
    async def on_message(self, message):
        if message.author.bot:
            return

        connection = self.db
        cursor = connection.cursor(dictionary=True)
        cursor.execute("SELECT command_name, response FROM custom_commands WHERE server_id = %s", (message.guild.id,))
        commands = cursor.fetchall()
        cursor.close()

        for command in commands:
            if message.content.startswith(f'!{command["command_name"]}'):
                await message.channel.send(command["response"])
                break

def setup(bot):
    bot.add_cog(CustomCommands(bot))
