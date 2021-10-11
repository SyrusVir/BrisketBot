import os
import re
import discord
from dotenv import load_dotenv

load_dotenv()

class BrisketBot(discord.Client):
    TOKEN = os.getenv('DISCORD_TOKEN')
    GUILD = os.getenv('DISCORD_GUILD')
    
    cmd_flag = '>>'
    db_file = 'brisket.db'

    def __init__(self, *, loop=None, **options):
        super().__init__(loop=loop, **options)
        """
        TODO: Initialize database tables here
        """

    def isCmd(self,string: str) -> bool:
        """
        Checks if str is a bot command, i.e. starts with the command flag
        """
        pattern = "^{}".format(self.cmd_flag)
        return bool(re.match(string, pattern))


    async def on_ready(self):
        for guild in self.guilds:
            if guild.name == self.GUILD:
                break

        print(
            f'{self.user} is connected to the following guild:\n'
            f'{guild.name}(id: {guild.id})\n'
        )

        members = '\n - '.join([member.name for member in guild.members])
        print(f'Guild Members:\n - {members}')

    async def on_message(self, message: discord.Message):
        # do not react to messages from bot itself
        if message.author == self.user:
            return
        
        # Parse command if message is command
        if self.isCmd(message.content):
            pass

        await message.channel.send(message.content)
        await message.channel.send(message.clean_content)

        print(message.content)
        print(message.clean_content)

bot = BrisketBot()
bot.run(bot.TOKEN)