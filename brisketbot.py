import datetime
import os
import re
from typing import Generator, List
import discord  
from discord import Guild, Member
from discord.ext import commands
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
DEBUG_GUILD_ID = int(os.getenv('DEBUG_GUILD'))
BRISKET_GUILD_ID = int(os.getenv('BRISKET_GUILD'))
CMD_FLAG = '>>'
DB_FILE = 'brisket.db'

## Brisket Brethren Role IDs
allowed_roles = {
    'governor' : 894808140837691433,
    'consul'   : 894806976016572477,
    'officer'  : 894807444230914068,
    'settler'  : 894807523654238229
}

## Restrict slash commands to users with Dev role
allowed_slash_roles = []
brisket_perms = {BRISKET_GUILD_ID : [create_permission(898814200040812585, SlashCommandPermissionType.ROLE, True)]}
allow_me = {DEBUG_GUILD_ID : [create_permission(406849788303114241, SlashCommandPermissionType.USER,True)]}
all_perms = {**brisket_perms, **allow_me}

## Instantiating Bot and slash objects
intents = discord.Intents.default()
intents.members = True
bot = commands.Bot(command_prefix=CMD_FLAG, intents=intents)
slash = SlashCommand(bot, sync_commands=True)

## Initializing database
brisket_db = BrisketDB(DB_FILE)

## Bot Events ###################################################
@bot.event
async def on_ready():
    print("Ready!")  
    
    # Get Brisket Brethren guild object
    # If found, populate members table 
    brisket_guild = bot.get_guild(BRISKET_GUILD_ID)
    print(brisket_guild)
    allowed_role_obj = [brisket_guild.get_role(rid) for rid in allowed_roles.values()]
    
    member_ids = []
    member_names = []
    for rid in allowed_roles.values():
        role = brisket_guild.get_role(rid)
        for m in role.members:
            if m.id not in member_ids:
                member_ids.append(m.id)
                member_names.append(m.display_name)   
    
    MemberTable.upsertMembers(brisket_db, member_name=member_names, discord_ids=member_ids)
    for r in brisket_db[MemberTable.TABLE_NAME].rows:
        print(r)

@bot.event
async def on_error(event:str, *args, **kwargs):
    print("Error Event!")
    await bot.close()
###################################################################

## Test Slash Commands ############################################
@slash.slash(name="ping",
    description="A test slash command",
    default_permission=False,
    permissions=all_perms,
)
async def ping(ctx: SlashContext):
    await ctx.send("pong")

@slash.slash(name='closebot',
    default_permission=False,
    description="Close bot")
async def _close_bot(ctx:SlashContext):
    await bot.close()
##########################################################################

## Bank Slash Commands ###################################################
@slash.subcommand(base='bank',
    name='add',
    description="Record donation to company bank",
    base_default_permission=False,
    base_permissions=brisket_perms,
    options=[
        create_option(name="amount",
            description="Donation amount",
            required=True,
            option_type=SlashCommandOptionType.FLOAT
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
async def _bank_add(ctx:SlashContext,amount:float,note:str=None,date:str=None):
    if date != None:
        try:
            date = datetime.date.fromisoformat(date)
        except ValueError as err:
            new_err = str(err) + '. Require date format YYYY-MM-DD.'
            await ctx.send(new_err)
            return

    id = ctx.author_id
    BankTable.insertBankLog(brisket_db, member_id=id, amount=amount, note=note, date=date)
    

@slash.subcommand(base='bank',
    name='delete',
    description="Delete company bank donation",
    base_default_permission=False,
    options=[
        create_option(name="xactid",
            description="Transaction ID",
            required=True,
            option_type=SlashCommandOptionType.INTEGER
        )
    ]
)
async def _bank_delete(ctx:SlashContext,xactid:int):
    # Check if record exists
    try:
        xaction = brisket_db[BankTable.TABLE_NAME].get(xactid)
    except NotFoundError:
        await ctx.send(f"Transaction #{xactid} does not exist.")
        return
    
    # Check that caller created record to delete
    caller_id = ctx.author_id
    record_id = xaction[BankTable.MEMBERID_COL] 
    if record_id != caller_id:
        record_name = ctx.guild.get_member(record_id).display_name
        await ctx.send(f"You do not have permission to modify this record by {record_name}.")
        return
    else:
        BankTable.deleteBankLog(brisket_db, xactid)

@slash.subcommand(base='bank',
    name='edit',
    description="Edit an existing record.",
    base_default_permission=False,
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
async def _bank_edit(ctx: SlashContext, xactid:int, amount:str=None, date:str=None, note:str=None):
    # Check if record exists
    try:
        xaction = brisket_db[BankTable.TABLE_NAME].get(xactid)
    except NotFoundError:
        await ctx.send(f"Transaction #{xactid} does not exist.")
        return
    
    # Check that caller created record to delete
    caller_id = ctx.author_id
    record_id = xaction[BankTable.MEMBERID_COL] 
    if record_id != caller_id:
        record_name = ctx.guild.get_member(record_id).display_name
        await ctx.send(f"You do not have permission to modify this record by {record_name}.")
        return
    else:
        amount = float(amount) // 0.01 / 100
        BankTable.updateBankLog(brisket_db, xactid, amount, date, note)

@slash.subcommand(base='bank',
    name='view',
    description='Show donation logs',
    base_default_permission=False,
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
async def _bank_print(ctx:SlashContext, user:discord.Member=None, lastn:int=5):   
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

    member_names = [ctx.guild.get_member(id).display_name if id != None else None for id in dictList[BankTable.MEMBERID_COL]]
    
    new_dict = dictList
    del new_dict[BankTable.MEMBERID_COL]
    new_dict["Member"] = member_names
        
    string = bu.formatTable(new_dict)
    await ctx.send(string)

@slash.subcommand(base='bank',
    subcommand_group='balance',
    name='get',
    description='Show current company bank balance',
    base_default_permission=False,
)
async def _bank_get_balance(ctx:SlashContext):
    results = brisket_db.query(f"SELECT {BankTable.AMNT_COL} FROM {BankTable.TABLE_NAME} ORDER BY {BankTable.XACTID_COL} ASC")
    bal = 0
    for r in results:
        bal = bal + r[BankTable.AMNT_COL]
    await ctx.send(f"Current Company Bank Balance: {bal // 0.01 / 100}")

@slash.subcommand(base='bank',
    subcommand_group='balance',
    name='setinit',
    description='Set initial bank balance. All logged donations will be summed into this value',
    base_default_permission=False,
    options=[
        create_option(name='initbal',
            description='Initial balance',
            required= True,
            option_type=SlashCommandOptionType.STRING
        )
    ]
)
async def _bank_set_balance(ctx:SlashContext, initbal:str):
    initbal = float(initbal) // 0.01 / 100 # truncate to two decimal places
    BankTable.updateBankLog(brisket_db, 0, initbal, date=datetime.date.today(), note="Initial Balance")
#################################################################

## Skill Table Slash Commands ###################################
skill_slash_choices = [create_choice(name=skill.name,value=skill.value) for skill in SkillDB.Skills]

@slash.subcommand(base="skilllvls",
    name="add",
    description="Log a life skill level",
    base_default_permission=False,
    base_permissions=all_perms,
    options=[
        create_option(name="skill",
            description="Trade Skill",
            required=True,
            option_type=SlashCommandOptionType.INTEGER,
            choices=skill_slash_choices
        ),
        create_option(name="lvl",
            description="New skill level",
            required=True,
            option_type=SlashCommandOptionType.INTEGER
        ),
        create_option(name="date",
            description="Day of level up",
            required=False,
            option_type=SlashCommandOptionType.STRING
        )
    ]
)
async def _skill_add(ctx:SlashContext,skill:int,lvl:int,date:str=None):
    if date != None:
        try:
            date = datetime.date.fromisoformat(date)
        except ValueError as err:
            new_err = str(err) + '. Require date format YYYY-MM-DD.'
            await ctx.send(new_err)
            return

    member_id = ctx.author_id
    SkillDB.SkillLogTable.insertSkillLog(brisket_db, member_id=member_id,lvl=lvl,skill_id=skill, date=date)

@slash.subcommand(base="skilllvls",
    name="edit",
    description="Log a life skill level",
    base_default_permission=False,
    options=[
        create_option(name="log_id",
            description="ID of skill log to edit",
            required=True,
            option_type=SlashCommandOptionType.INTEGER
        ),
        create_option(name="skill",
            description="Trade skill",
            required=False,
            option_type=SlashCommandOptionType.INTEGER,
            choices=skill_slash_choices
        ),
        create_option(name="lvl",
            description="New level",
            required=False,
            option_type=SlashCommandOptionType.INTEGER
        ),
        create_option(name="date",
            description="New date",
            required=False,
            option_type=SlashCommandOptionType.STRING
        )
    ]
)
async def _skill_edit(ctx:SlashContext, log_id:int, skill:int=None,lvl:int=None,date:str=None):
    # Check if record exists
    try:
        skilllog = brisket_db[SkillDB.SkillLogTable.TABLE_NAME].get(log_id)
    except NotFoundError:
        await ctx.send(f"Transaction #{log_id} does not exist.")
        return

    # Get Skill ID
    skill_id = None
    if skill != None:
        try:
            row = brisket_db[SkillDB.SkillTable.TABLE_NAME].rows_where(f"{SkillDB.SkillTable.NAME_COL} = {skill}", limit=1)
            skill_id = next(row)[SkillDB.SkillTable.SKILLID_COL]
        except:
            await ctx.send(f"Could not find skill ID for {skill}.")

    # Check that caller created record to delete
    caller_id = ctx.author_id
    record_id = skilllog[SkillDB.SkillLogTable.MEMBERID_COL] 
    if record_id != caller_id:
        record_name = ctx.guild.get_member(record_id).display_name
        await ctx.send(f"You do not have permission to modify this record by {record_name}.")
        return
    else:
        SkillDB.SkillLogTable.updateSkillLog(brisket_db, log_id, skill, lvl, date)

@slash.subcommand(base="skilllvls",
    name="delete",
    description="Delete a trade skill level",
    base_default_permission=False,
    options=[
        create_option(name="log_id",
            description="ID of skill update to delete",
            required=True,
            option_type=SlashCommandOptionType.INTEGER
        )
    ]
)
async def _skill_delete(ctx:SlashContext, log_id:int):
    # Check if record exists
    try:
        skilllog = brisket_db[SkillDB.SkillLogTable.TABLE_NAME].get(log_id)
    except NotFoundError:
        await ctx.send(f"Transaction #{log_id} does not exist.")
        return

    # Check that caller created record to delete
    caller_id = ctx.author_id
    record_id = skilllog[SkillDB.SkillLogTable.MEMBERID_COL] 
    if record_id != caller_id:
        record_name = ctx.guild.get_member(record_id).display_name
        await ctx.send(f"You do not have permission to modify this record by {record_name}.")
        return
    else:
        SkillDB.SkillLogTable.deleteSkillLog(brisket_db, log_id)

@slash.subcommand(base="skilllvls",
    name="view",
    description="Display skill logs",
    base_default_permission=False,
    options=[
        create_option(name='user',
            option_type=SlashCommandOptionType.USER,
            description="View user's skill. Default shows users current skill levels",
            required=False,
        ),
        create_option(name='skill',
            description="Skill to show",
            option_type=SlashCommandOptionType.INTEGER,
            choices=skill_slash_choices,
            required=False
        ),
        create_option(name='lastn',
            description="Display the last N skill logs",
            required=False,
            option_type=SlashCommandOptionType.INTEGER
        ),
        create_option(name='best',
            description="""Return best users in skill or users highest level in all skill""",
            required=False,
            option_type=SlashCommandOptionType.BOOLEAN
        )
    ]
)
async def _skill_show(ctx:SlashContext, user:Member=None, skill:int=None, lastn:int=5, best:bool=False):
    member_id = None

    # Get specified user and skill IDs
    if user != None:
        member_id = user.id

    # If no parameters passed, show last N entries
    if member_id == None and skill == None:
        query_str = f"""SELECT * 
            FROM {SkillDB.SkillLogTable.TABLE_NAME}
            ORDER BY {SkillDB.SkillLogTable.DATE_COL} DESC
            LIMIT {lastn}"""
    
    # Else if both user and skill provided show last N entries of users entries for specified skill
    elif member_id != None and skill != None:
        query_str = f"""SELECT *
        FROM {SkillDB.SkillLogTable.TABLE_NAME}
        WHERE {SkillDB.SkillLogTable.SKILLID_COL} = {skill} 
            AND {SkillDB.SkillLogTable.MEMBERID_COL} = {member_id}
        ORDER BY {SkillDB.SkillLogTable.DATE_COL} DESC
        LIMIT {lastn}
        """
    
    ## If this point reached, then either member_id or skill is None, but not both ##

    # Else if no user provided but skill provided, show last N entries for specified skill.
    # If best specified, return lastn players with highest level in that skill
    elif skill != None: 
        if best:
            query_str = f"""SELECT t1.*
                FROM {SkillDB.SkillLogTable.TABLE_NAME} t1
                INNER JOIN (SELECT {SkillDB.SkillLogTable.MEMBERID_COL}, {SkillDB.SkillLogTable.SKILLID_COL}, MAX({SkillDB.SkillLogTable.LEVEL_COL}) max_lvl
                    FROM {SkillDB.SkillLogTable.TABLE_NAME}
                    GROUP BY {SkillDB.SkillLogTable.MEMBERID_COL}, {SkillDB.SkillLogTable.SKILLID_COL}
                    HAVING {SkillDB.SkillLogTable.SKILLID_COL} = {skill}) t2
                ON t1.{SkillDB.SkillLogTable.MEMBERID_COL} = t2.{SkillDB.SkillLogTable.MEMBERID_COL} 
                AND t1.{SkillDB.SkillLogTable.LEVEL_COL} = t2.max_lvl
                AND t1.{SkillDB.SkillLogTable.SKILLID_COL} = t2.{SkillDB.SkillLogTable.SKILLID_COL}
                ORDER BY {SkillDB.SkillLogTable.LEVEL_COL} DESC
                LIMIT {lastn}
                """
        else:
            query_str = f"""SELECT *
            FROM {SkillDB.SkillLogTable.TABLE_NAME}
            WHERE {SkillDB.SkillLogTable.SKILLID_COL} = {skill}
            ORDER BY {SkillDB.SkillLogTable.DATE_COL} ASC
            LIMIT {lastn}
            """
            
    # Else if no skill provided but user provided, show user's most recent entry for each skill
    # If best specified, return user's highest level in each skill
    elif member_id != None:
        query_str = f"""SELECT t1.*
                FROM {SkillDB.SkillLogTable.TABLE_NAME} t1
                INNER JOIN (SELECT {SkillDB.SkillLogTable.MEMBERID_COL}, {SkillDB.SkillLogTable.SKILLID_COL}, MAX({SkillDB.SkillLogTable.LEVEL_COL}) max_lvl
                    FROM {SkillDB.SkillLogTable.TABLE_NAME}
                    GROUP BY {SkillDB.SkillLogTable.MEMBERID_COL}, {SkillDB.SkillLogTable.SKILLID_COL}
                    HAVING {SkillDB.SkillLogTable.MEMBERID_COL} = {member_id}) t2
                ON t1.{SkillDB.SkillLogTable.MEMBERID_COL} = t2.{SkillDB.SkillLogTable.MEMBERID_COL} 
                AND t1.{SkillDB.SkillLogTable.LEVEL_COL} = t2.max_lvl
                AND t1.{SkillDB.SkillLogTable.SKILLID_COL} = t2.{SkillDB.SkillLogTable.SKILLID_COL}
                ORDER BY {SkillDB.SkillLogTable.LEVEL_COL} DESC
                """

    results = brisket_db.query(query_str)
    table_str = bu.formatTable(bu.listDictToDictList(list(results)))
    await ctx.send(table_str)
#################################################################
        
## Weapon Table Slash Commands ##################################
weapon_slash_choices = [create_choice(name=weap.name, value=weap.value) for weap in WeaponDB.Weapons]


#################################################################


    
bot.run(TOKEN)