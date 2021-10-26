import datetime
import os
import re
from typing import Generator, List
import discord
from discord import guild
from discord import member
from discord.ext import commands
from discord.member import Member
from discord_slash import SlashCommand, SlashContext
from discord_slash.model import SlashCommandOptionType, SlashCommandPermissionType
from discord_slash.utils.manage_commands import create_choice, create_option, create_permission
from sqlite_utils import Database
from enum import IntEnum
from dotenv import load_dotenv
from sqlite_utils.db import NotFoundError, Table
from BrisketDB import BrisketDB
import brisketutils as bu

# Database imports
from MemberDB import MemberTable
import WeaponDB
import SkillDB
from CharacterDB import CharacTable
from BankDB import BankTable

load_dotenv()
    TOKEN = os.getenv('DISCORD_TOKEN')
GUILD_ID = int(os.getenv('DISCORD_GUILD'))
    CMD_FLAG = '>>'
    DB_FILE = 'brisket.db'

intents = discord.Intents.default()
intents.members = True
bot = commands.Bot(command_prefix=CMD_FLAG, intents=intents)
slash = SlashCommand(bot, sync_commands=True)


## Initializing database
brisket_db = BrisketDB('brisket4.db')

@slash.slash(name="ping",
    description="A test slash command",
    guild_ids=[GUILD_ID],
    options=[
        create_option(
                 name="optone",
                 description="This is the first option we have.",
                 option_type=SlashCommandOptionType.USER,
                 required=False
        )
    ])
async def ping(ctxt: SlashContext, optone):
    print(optone)
    print(type(optone))
    await ctxt.send("pong")

## Bank Slash Commands ###################################################
@slash.subcommand(base='bank',
    name='add',
    description="Record donation to company bank",
    options=[
        create_option(name="amount",
            description="Donation amount",
            required=True,
            option_type=SlashCommandOptionType.STRING
        ),
        create_option(name="note",
            description="Add a comment to donation",
            required=False,
            option_type=SlashCommandOptionType.STRING
        ),
        create_option(name="date",
            description="Donation date as YYYY-MM-DD. Leave empty to default to today.",
            required=False,
            option_type=SlashCommandOptionType.STRING
        )
    ]
)
async def _bank_add(ctxt:SlashContext,amount:str,note:str=None,date:str=None):
    if date != None:
        try:
            date = datetime.date.fromisoformat(date)
        except ValueError as err:
            new_err = str(err) + '. Require date format YYYY-MM-DD.'
            await ctxt.send(new_err)
            return
    try:
        amount = float(amount) // 0.01 / 100
    except:
        await ctxt.send("Could not convert amount from string to float")
        return

    id = ctxt.author_id
    BankTable.insertBankLog(brisket_db, member_id=id, amount=amount, note=note, date=date)

@slash.subcommand(base='bank',
    name='delete',
    description="Delete company bank donation",
    options=[
        create_option(name="xactid",
            description="Transaction ID",
            required=True,
            option_type=SlashCommandOptionType.INTEGER
        )
    ]
)
async def _bank_delete(ctxt:SlashContext,xactid:int):
    # Check if record exists
    try:
        xaction = brisket_db[BankTable.TABLE_NAME].get(xactid)
    except NotFoundError:
        await ctxt.send(f"Transaction #{xactid} does not exist.")
        return
    
    # Check that caller created record to delete
    caller_id = ctxt.author_id
    record_id = xaction[BankTable.MEMBERID_COL] 
    if record_id != caller_id:
        record_name = ctxt.guild.get_member(record_id).display_name
        await ctxt.send(f"You do not have permission to modify this record by {record_name}.")
        return
    else:
        BankTable.deleteBankLog(brisket_db, xactid)

@slash.subcommand(base='bank',
    name='edit',
    description="Edit an existing record.",
    options= [
        create_option(name="xactid",
            required=True,
            option_type=SlashCommandOptionType.INTEGER,
            description="ID of record to edit"
        ),
        create_option(name="amount",
            required=False,
            option_type=SlashCommandOptionType.STRING,
            description="New amount"
        ),
        create_option(name="note",
            description="New record note",
            required=False,
            option_type=SlashCommandOptionType.STRING
        ),
        create_option(name="date",
            description="New record date",
            required=False,
            option_type=SlashCommandOptionType.STRING
        )
    ])
async def _bank_edit(ctxt: SlashContext, xactid:int, amount:str=None, date:str=None, note:str=None):
    # Check if record exists
    try:
        xaction = brisket_db[BankTable.TABLE_NAME].get(xactid)
    except NotFoundError:
        await ctxt.send(f"Transaction #{xactid} does not exist.")
        return
    
    # Check that caller created record to delete
    caller_id = ctxt.author_id
    record_id = xaction[BankTable.MEMBERID_COL] 
    if record_id != caller_id:
        record_name = ctxt.guild.get_member(record_id).display_name
        await ctxt.send(f"You do not have permission to modify this record by {record_name}.")
        return
    else:
        amount = float(amount) // 0.01 / 100
        BankTable.updateBankLog(brisket_db, xactid, amount, date, note)

@slash.subcommand(base='bank',
    name='view',
    description='Show donation logs',
    options= [
        create_option(name='user',
            option_type=SlashCommandOptionType.USER,
            description="View user's donations",
            required=False
        ),
        create_option(name='lastn',
            description="Display the last N donations",
            required=False,
            option_type=SlashCommandOptionType.INTEGER
        )
    ])
async def _bank_print(ctxt:SlashContext, user:discord.Member=None, lastn:int=5):   
    if user != None:
        member_id = user.id
        results = brisket_db.query(f"""SELECT 
            {BankTable.XACTID_COL},{BankTable.DATE_COL}, {BankTable.MEMBERID_COL}, {BankTable.AMNT_COL}, {BankTable.NOTE_COL}
            FROM {BankTable.TABLE_NAME} 
            WHERE {BankTable.MEMBERID_COL} = {member_id} 
            ORDER BY {BankTable.DATE_COL} DESC 
            LIMIT {lastn}""")
    else:
        results = brisket_db.query(f"""SELECT 
            {BankTable.XACTID_COL},{BankTable.DATE_COL}, {BankTable.MEMBERID_COL}, {BankTable.AMNT_COL}, {BankTable.NOTE_COL}
            FROM {BankTable.TABLE_NAME}  
            ORDER BY {BankTable.DATE_COL} DESC 
            LIMIT {lastn}""")
    
    dictList = bu.listDictToDictList(list(results))

    member_names = [ctxt.guild.get_member(id).display_name if id != None else None for id in dictList[BankTable.MEMBERID_COL]]
    
    new_dict = dictList
    del new_dict[BankTable.MEMBERID_COL]
    new_dict["Member"] = member_names
        
    string = bu.formatTable(new_dict)
    await ctxt.send(string)
    

@slash.subcommand(base='bank',
    subcommand_group='balance',
    name='get',
    description='Show current company bank balance',
)
async def _bank_get_balance(ctxt:SlashContext):
    results = brisket_db.query(f"SELECT {BankTable.AMNT_COL} FROM {BankTable.TABLE_NAME} ORDER BY {BankTable.XACTID_COL} ASC")
    bal = 0
    for r in results:
        bal = bal + r[BankTable.AMNT_COL]
    await ctxt.send(f"Current Company Bank Balance: {bal // 0.01 / 100}")

@slash.subcommand(base='bank',
    subcommand_group='balance',
    name='setinit',
    description='Set initial bank balance. All logged donations will be summed into this value',
    options=[
        create_option(name='initbal',
            description='Initial balance',
            required= True,
            option_type=SlashCommandOptionType.STRING
        )
    ]
)
@slash.permission(guild_id=GUILD_ID,
    permissions=[
        create_permission(894808140837691433,SlashCommandPermissionType.ROLE,True)
    ])
async def _bank_set_balance(ctxt:SlashContext, initbal:str):
    initbal = float(initbal) // 0.01 / 100 # truncate to two decimal places
    BankTable.updateBankLog(brisket_db, 0, initbal, date=datetime.date.today(), note="Initial Balance")
#################################################################

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

@slash.slash(name='closes',
    description="Close bot")
async def _close_bot(ctxt:SlashContext):
    await bot.close()

## Bot Events ###################################################
@bot.event
async def on_ready():
    print("Ready!")  
    guild = bot.get_guild(GUILD_ID)
    channel = guild.get_channel(896038294297649184)

@bot.event
async def on_error():
    print("Error Event!")
    await bot.close()
###################################################################

    
bot.run(TOKEN)