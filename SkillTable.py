"""
Contains classes defining three database tables for tracking member trade skills

1.  NWSkillCategs - lookup table to get trade skill category (e.g., refining) for a skill.
                    The lookup table is NOT built explicitly. The 'extracts' feature of sqlite_utils is used.
                    Use the lookup() method of sqlite_utils to interact with this table

2. NWSkills - Lookup table that contains current New World weapons; contains foreign key referencing NWSkillCategs

3. SkillLogTable - Table containing dates of when a member achieved a trade skill level

For each table, three methods are defined
"""
from sqlite_utils import Database
import sqlite3 as sql
from datetime import datetime
from MemberTable import MemberTable

class NWSkillCategs():
    TABLE_NAME = 'skill_categories'
    REFINING = 'refining'
    GATHERING = 'gathering'
    CRAFTING = 'crafting'

class NWSkills():    
    TABLE_NAME = 'skills'
    SKILLID_COL = 'SkillID'
    SKILLCATID_COL = 'SkillCategID'
    NAME_COL = 'Skill'

    WEAPONSMITH = 'weaponsmithing'
    ARMORING = 'armoring'
    ENGINEERING = 'engineering'
    JEWEL = 'jewelcrafting'
    ARCANA = 'arcana'
    COOKING = 'cooking'
    FURNISH = 'furnishing'
    SMELT = 'smelting'
    WOODWORK = 'woodworking'
    LEATHERWORK = 'leatherworking'
    WEAVING = 'weaving'
    STONECUT = 'stonecutting'
    LOGGING = 'logging'
    MINING = 'mining'
    FISHING = 'fishing'
    HARVEST = 'harvesting'
    TRACK = 'tracking'

    CRAFT_SKILLS = [WEAPONSMITH,ARMORING,ENGINEERING,JEWEL,ARCANA,COOKING,FURNISH]
    REFINE_SKILLS = [SMELT,WOODWORK,LEATHERWORK,WEAVING,STONECUT]
    GATHER_SKILLS = [LOGGING,MINING,FISHING,HARVEST,TRACK]

    def initSkillTable(db:Database):
        skill_table = db[NWSkills.TABLE_NAME]

        # Build dictionary relating skills to skill categories
        skill_cat_dict = dict.fromkeys(NWSkills.REFINE_SKILLS,NWSkillCategs.REFINING)
        skill_cat_dict.update(dict.fromkeys(NWSkills.CRAFT_SKILLS,NWSkillCategs.CRAFTING))
        skill_cat_dict.update(dict.fromkeys(NWSkills.GATHER_SKILLS,NWSkillCategs.GATHERING))

        # Build list of dictionaries of row data by iterating over dict relating skills and skill categories
        table_data = [{
            NWSkills.NAME_COL : name,
            NWSkills.SKILLCATID_COL : cat_name,
        } for name,cat_name in skill_cat_dict.items()]

        # Insert into weapon table; Extract category names to new look-up table
        skill_table.insert_all(table_data,pk=NWSkills.SKILLID_COL,
            ignore=True, extracts={NWSkills.SKILLCATID_COL:NWSkillCategs.TABLE_NAME})
        
        skill_table.create_index([NWSkills.NAME_COL], unique=True, if_not_exists=True)

class SkillLogTable():
    TABLE_NAME = "skilllogs"
    UPDATEID_COL = "UpdateID"
    DATE_COL = "Date"
    MEMBERID_COL = "MemberID"
    SKILLID_COL = "SKillID"
    LEVEL_COL = "Level"
            
    def initSkillLogTable(db: Database):
        """If not pre-existing, create the skill log table in database <db>

        :param db: A connection to an existing database file
        :type db: sqlite_utils.Database
        :raises err: Ignores sqlite3.OperationalError if error results from attempting to create a pre-existing table
        """
        skill_log_table = db[SkillLogTable.TABLE_NAME]

        try:
            skill_log_table.create({
                SkillLogTable.UPDATEID_COL : int,
                SkillLogTable.DATE_COL: str,
                SkillLogTable.MEMBERID_COL: int,
                SkillLogTable.SKILLID_COL: int,
                SkillLogTable.LEVEL_COL: int
            },
                pk=SkillLogTable.UPDATEID_COL,
                foreign_keys=[
                    (SkillLogTable.MEMBERID_COL, MemberTable.TABLE_NAME),
                    (SkillLogTable.SKILLID_COL, NWSkills.TABLE_NAME)
                ])
        except sql.OperationalError as err:
            if 'already exists' in str(err):
                pass
            else:
                raise err
    
    def upsertSkillLog(db: Database, player_id, skill_id, date:str=None, log_id=None):
        """Insert an entry into the skill log table. 
        If <log_id> is provided and refers to an existing entry, that entry will be updated with the provided values

        :param db: [description]
        :type db: sqlite3.Database
        :param player_id: [description]
        :type player_id: [type]
        :param skill_id: [description]
        :type skill_id: [type]
        :param date: [description], defaults to None
        :type date: str, optional
        :param log_id: [description], defaults to None
        :type log_id: [type], optional
        """
        skill_log_table = db[SkillLogTable.TABLE_NAME]
        
        if date == None:
            date = datetime.now().date()
        
        table_data = {
            SkillLogTable.MEMBERID_COL: player_id,
            SkillLogTable.SKILLID_COL: skill_id,
            SkillLogTable.DATE_COL: date
        }

        # If a log ID specified, add to dictionary
        if log_id != None:
            table_data[SkillLogTable.UPDATEID_COL] = log_id
        
        skill_log_table.upsert(table_data,pk=SkillLogTable.UPDATEID_COL)

    def deleteSkillLog(db: Database, log_id:int):
        skill_log_table = db[NWSkills.TABLE_NAME]
        skill_log_table.delete(log_id)


if __name__ == "__main__":
    from sqlite_utils import Database
    db = Database('skill.db')
    MemberTable.initMemberTable(db)
    NWSkills.initSkillTable(db)
    SkillLogTable.initSkillLogTable(db)


    SkillLogTable.upsertSkillLog(db,1,1)
    for r in db[SkillLogTable.TABLE_NAME].rows:
        print(r)

    print()