from datetime import datetime
import os
import re
import discord
import sqlite3 as sql
import sqlite_utils
from sqlite_utils import Database
from enum import Enum
from dotenv import load_dotenv

load_dotenv()

def printDB(db: sqlite_utils.db.Queryable):
    for row in db.rows:
        print(row)

## Bot Implementation #############################################
class BrisketBot(discord.Client):
    TOKEN = os.getenv('DISCORD_TOKEN')
    GUILD = os.getenv('DISCORD_GUILD')
    
    CMD_FLAG = '>>'
    DB_FILE = 'brisket.db'

    def __init__(self, *, loop=None, **options):
        super().__init__(loop=loop, **options)

        # Open reference to database
        self.db = Database(self.DB_FILE)

    ## Player Table Methods ############################################################
    def initPlayerTable(self):
        guild = self.get_guild(self.GUILD_ID)
        if guild == None:
            print("Guild not found")

    ## Asynchronous Methods ==========================================
    async def on_ready(self):
        for guild in self.guilds:
            if guild.name == self.GUILD:
                self.GUILD_ID = guild.id
                break

        print(
            f'{self.user} is connected to the following guild:\n'
            f'{guild.name}(id: {guild.id})\n'
        )

        members = '\n - '.join([f"{member.name},{member.id}" for member in guild.members])
        print(f'Guild Members:\n - {members}')

        await self.close()

    async def on_message(self, message: discord.Message):
        # do not react to messages from bot itself
        if message.author == self.user:
            return
        
        # Check if message is a command
        m = re.match(f"^{self.CMD_FLAG}",message.content)
        if m != None:
            # If match, get string after command flag
            cmd_str = message.content[m.end():]

            # Parse componetns of command string


        await message.channel.send(message.content)
        await message.channel.send(message.clean_content)

        print(message.content)
        print(message.clean_content)

if __name__ == "__main__":
    intents = discord.Intents.default()
    intents.members = True
    bot = BrisketBot(intents = intents)
    bot.run(bot.TOKEN)    
    # bot.db["TestTable"].drop(ignore=True)
    # bot.db["TestTable"].insert_all([{'val':22},{'val':50}], pk='id')
    # for row in bot.db["TestTable"].rows:
    #     print(row)
    