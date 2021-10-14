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

## Player Table definitin ###################################
class PlayerTable():
    TABLE_NAME = "Players"
    PLAYERID_COL = "PlayerID"
    DISCORDID_COL = "DiscordID"
    NAME_COL = "Name"
    DISCORD_IDX = "idx_discord_id"

## Bank Log Table definition ####################################
class BankTable():
    TABLE_NAME = "bank"
    XACTID_COL = "XactID"
    DATE_COL = "Date"
    PLAYERID_COL = "PlayerID"
    AMNT_COL = "Amount"
    NOTE_COL = "Note"

## Character Level Log Table definition #########################
class CharacTable():
    TABLE_NAME = "CharacterLevelLog"
    DATE_COL = "Date"
    PLAYERID_COL = "PlayerID"
    LEVEL_COL = "Level"

## Weapon Table enumerations ##################################


class NWWeapons():
    class NWWeaponCategs():
        TABLE_NAME = "WeaponCategories"
        ID_COL = "CategID"
        NAME_COL = "WeaponCategory"

        ONEHAND = 'one-handed'
        TWOHAND = "two-handed"
        RANGE = "ranged"
        MAGIC = "magic"
    
    TABLE_NAME = "Weapons"
    WEAPONID_COL = "WeaponID"
    WEAPONCATEGID_COL = "WeaponCategID"
    NAME_COL = "Weapon"

    RAPIER = "rapier"
    SWORD = "sword"
    HATCHET = "hatchet"
    WARHAMMER = "warhammer"
    BATTLEAXE = "battleaxe"
    SPEAR = "spear"
    BOW = "bow"
    MUSKET = "musket"
    FIRESTAFF = "firestaff"
    LIFESTAFF = "lifestaff"
    ICEGAUNTLET = "icegauntlet"

    WEAPON_CAT_DICT ={
        RAPIER : NWWeaponCategs.ONEHAND,
        SWORD : NWWeaponCategs.ONEHAND,
        HATCHET : NWWeaponCategs.ONEHAND, 
        WARHAMMER : NWWeaponCategs.TWOHAND, 
        BATTLEAXE : NWWeaponCategs.TWOHAND, 
        SPEAR : NWWeaponCategs.TWOHAND, 
        BOW : NWWeaponCategs.RANGE, 
        MUSKET : NWWeaponCategs.RANGE, 
        FIRESTAFF : NWWeaponCategs.MAGIC, 
        LIFESTAFF : NWWeaponCategs.MAGIC, 
        ICEGAUNTLET : NWWeaponCategs.MAGIC
        }


class WeaponLogTable():
    TABLE_NAME = "WeaponLog"
    UPDATEID_COL = "UpdateID"
    DATE_COL = "Date"
    PLAYERID_COL = "PlayerID"
    WEAPONID_COL = "WeaponID"
    LEVEL_COL = "Level"

## Trade Skill Table Enumerations ################################


class NWTradeSkills():
    class NWSkillCategs():
        TABLE_NAME = "SkillCategories"
        ID_COL = "CategID"
        NAME_COL = "SkillCategory"

        REFINING = "refining"
        CRAFTING = "crafting"
        GATHERING = "gathering"

    TABLE_NAME = "TradeSkills"
    SKILLID_COL = "SkillID"
    SKILLCATID_COL = "SkillCategID"
    NAME_COL = "Skill"

    WEAPONSMITHING = "weaponsmithing"
    ARMORING = "armoring"
    ENGINEERING = "engineering"
    JEWELCRAFTING = "jewelcrafting"
    ARCANA  = "arcana"
    COOKING = "cooking"
    FURNISHING = "furnishing"
    SMELTING = "smelting"
    WOODWORKING = "woodworking"
    LEATHERWORKING = "leatherworking"
    WEAVING = "weaving"
    STONECUTTING = "stonecutting"
    LOGGING  = "logging"
    MINING = "mining"
    FISHING = "fishing"
    HARVESTING = "harvesting"
    TRACKING = "tracking"

    SKILL_CAT_DICT ={
        WEAPONSMITHING : NWSkillCategs.CRAFTING,
        ARMORING : NWSkillCategs.CRAFTING,
        ENGINEERING : NWSkillCategs.CRAFTING,
        JEWELCRAFTING : NWSkillCategs.CRAFTING,
        ARCANA : NWSkillCategs.CRAFTING,
        COOKING : NWSkillCategs.CRAFTING,
        FURNISHING : NWSkillCategs.CRAFTING,
        SMELTING : NWSkillCategs.REFINING,
        WOODWORKING : NWSkillCategs.REFINING,
        LEATHERWORKING : NWSkillCategs.REFINING,
        WEAVING : NWSkillCategs.REFINING,
        STONECUTTING : NWSkillCategs.REFINING,
        LOGGING : NWSkillCategs.GATHERING,
        MINING : NWSkillCategs.GATHERING,
        FISHING : NWSkillCategs.GATHERING,
        HARVESTING : NWSkillCategs.GATHERING,
        TRACKING : NWSkillCategs.GATHERING
    }

class SkillLogTable():
    TABLE_NAME = "SkillLogs"
    UPDATEID_COL = "UpdateID"
    DATE_COL = "Date"
    PLAYERID_COL = "PlayerID"
    SKILLID_COL = "SkillID"
    LEVEL_COL = "Level"

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

    def isCmd(self,string: str) -> bool:
        """
        Checks if str is a bot command, i.e. starts with the command flag
        """
        pattern = "^{}".format(self.CMD_FLAG)
        return bool(re.match(string, pattern))

    def initPlayerTable(self):
        guild = self.get_guild(self.GUILD_ID)
        if guild == None:
            print("Guild not found")
        else:
            player_table = self.db[PlayerTable.TABLE_NAME]

            # Getting dictionary of guild members and discord IDs
            players = guild.members

            table_data = [{
                PlayerTable.DISCORDID_COL: p.id,
                PlayerTable.NAME_COL: p.nick if p.nick != None else p.name
            } for p in players]

            # Build table implicitly
            player_table.insert_all(table_data,pk=PlayerTable.DISCORDID_COL, replace=False, ignore=True)
            
            #Creating foreign keys on discord user id
            player_table.create_index([PlayerTable.DISCORDID_COL],
                index_name=PlayerTable.DISCORD_IDX,
                unique=True,
                if_not_exists=True)

    def initWeaponTable(self):
        weapon_table = self.db[NWWeapons.TABLE_NAME]

        # Construct table data from dictionary relating 
        # weapons to weapon categories
        table_data = [
            {
            NWWeapons.NAME_COL : wname,
            NWWeapons.WEAPONCATEGID_COL : catname
            } 
            for wname, catname in NWWeapons.WEAPON_CAT_DICT.items()]
        
        # Construct table, extracting the weapon category data to a look up table
        weapon_table.insert_all(table_data, pk=NWWeapons.WEAPONID_COL,
            ignore=True,
            replace=False,
            extracts={NWWeapons.WEAPONCATEGID_COL:NWWeapons.NWWeaponCategs.TABLE_NAME}
        )
    
    def initSkillTable(self):
        skill_table = self.db[NWTradeSkills.TABLE_NAME]

        # Construct table data from dictionary relating 
        # skills to skill categories
        table_data = [
            {
            NWTradeSkills.NAME_COL : sname,
            NWTradeSkills.SKILLCATID_COL : catname
            } 
            for sname, catname in NWTradeSkills.SKILL_CAT_DICT.items()]
        
        # Construct table, extracting the skill category data to a look up table
        skill_table.insert_all(table_data, pk=NWTradeSkills.SKILLID_COL,
            ignore=True,
            replace=False,
            extracts={NWTradeSkills.SKILLCATID_COL:NWTradeSkills.NWSkillCategs.TABLE_NAME}
        )

    def initBankTable(self, init_bal = 0):
        self.init_bal = 0
        bank_table = self.db[BankTable.TABLE_NAME]

        try:
            bank_table.create({
                BankTable.XACTID_COL : int,
                BankTable.DATE_COL: str,
                BankTable.PLAYERID_COL: int,
                BankTable.AMNT_COL: float,
                BankTable.NOTE_COL: str
            },
                pk=BankTable.XACTID_COL,
                foreign_keys=[
                    (BankTable.PLAYERID_COL, PlayerTable.TABLE_NAME),
                ])
        except sql.OperationalError as err:
            #TODO: If table exists, ignore excpetion. Continue raise otherwise
            pass


    def initSkillLogTable(self):
        skill_log_table = self.db[SkillLogTable.TABLE_NAME]

        try:
            skill_log_table.create({
                SkillLogTable.UPDATEID_COL : int,
                SkillLogTable.DATE_COL: str,
                SkillLogTable.PLAYERID_COL: int,
                SkillLogTable.SKILLID_COL: int,
                SkillLogTable.LEVEL_COL: int
            },
                pk=SkillLogTable.UPDATEID_COL,
                foreign_keys=[
                    (SkillLogTable.PLAYERID_COL, PlayerTable.TABLE_NAME),
                    (SkillLogTable.SKILLID_COL, NWTradeSkills.TABLE_NAME)
                ])
        except sql.OperationalError as err:
            #TODO: If table exists, ignore excpetion. Continue raise otherwise
            pass

    def initWeaponLogTable(self):
        weapon_log_table = self.db[WeaponLogTable.TABLE_NAME]

        try:
            weapon_log_table.create({
                WeaponLogTable.UPDATEID_COL : int,
                WeaponLogTable.DATE_COL: str,
                WeaponLogTable.PLAYERID_COL: int,
                WeaponLogTable.WEAPONID_COL: int,
                WeaponLogTable.LEVEL_COL: int
            },
                pk=WeaponLogTable.UPDATEID_COL,
                foreign_keys=[
                    (WeaponLogTable.PLAYERID_COL, PlayerTable.TABLE_NAME),
                    (WeaponLogTable.WEAPONID_COL, NWWeapons.TABLE_NAME)
                ])
        except sql.OperationalError as err:
            #TODO: If table exists, ignore excpetion. Continue raise otherwise
            pass

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

        # Player table initializtion
        self.initPlayerTable()
        self.initWeaponTable()
        self.initSkillTable()
        self.initBankTable()
        self.initSkillLogTable()
        self.initWeaponLogTable()

        for table in self.db.tables:
            print(f"\nShowing table {table.name} schema")
            print(table.schema)

        await self.close()

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

if __name__ == "__main__":
    intents = discord.Intents.default()
    intents.members = True
    bot = BrisketBot(intents = intents)
    bot.run(bot.TOKEN)    
    # bot.db["TestTable"].drop(ignore=True)
    # bot.db["TestTable"].insert_all([{'val':22},{'val':50}], pk='id')
    # for row in bot.db["TestTable"].rows:
    #     print(row)
    