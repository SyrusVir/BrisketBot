"""
Contains classes defining three database tables for tracking member trade skills

1.  NWSkillCategs - lookup table to get trade skill category (e.g., refining) for a skill.
                    The lookup table is NOT built explicitly. The 'extracts' feature of sqlite_utils is used.
                    Use the lookup() method of sqlite_utils to interact with this table

2. NWSkills - Lookup table that contains current New World weapons; contains foreign key referencing NWSkillCategs

3. SkillLogTable - Table containing dates of when a member achieved a trade skill level

For each table, three methods are defined
"""
from os import name
import random
from sqlite_utils import Database
import sqlite3 as sql
import datetime
from MemberDB import MemberTable
from enum import Enum, IntEnum, auto
import brisketutils

class SkillCategs(IntEnum):
    REFINING = 1
    GATHERING = auto()
    CRAFTING = auto()

class Skills(IntEnum):
    WEAPONSMITH = 1
    ARMORING = auto()
    ENGINEERING = auto()
    JEWEL = auto()
    ARCANA = auto()
    COOKING = auto()
    FURNISH = auto()
    SMELT = auto()
    WOODWORK = auto()
    LEATHERWORK = auto()
    WEAVING = auto()
    STONECUT = auto()
    LOGGING = auto()
    MINING = auto()
    FISHING = auto()
    HARVEST = auto()
    TRACK = auto()

class SkillCategTable():

    TABLE_NAME = 'skillcategories'
    CATEGID_COL = 'SkillCategID'
    NAME_COL = 'SkillCategory'

    def initSkillCategTable(db:Database):
        table_data = [{
            SkillCategTable.CATEGID_COL : cat.value,
            SkillCategTable.NAME_COL : cat.name.lower()
        } for cat in SkillCategs]

        db[SkillCategTable.TABLE_NAME].insert_all(table_data,pk=SkillCategTable.CATEGID_COL,ignore=True)

class SkillTable():    
    TABLE_NAME = 'skills'
    SKILLID_COL = 'SkillID'
    SKILLCATID_COL = 'SkillCategID'
    NAME_COL = 'Skill'
    

    CRAFT_SKILLS = [Skills.WEAPONSMITH,Skills.ARMORING,Skills.ENGINEERING,Skills.JEWEL,Skills.ARCANA,Skills.COOKING,Skills.FURNISH]
    REFINE_SKILLS = [Skills.SMELT,Skills.WOODWORK,Skills.LEATHERWORK,Skills.WEAVING,Skills.STONECUT]
    GATHER_SKILLS = [Skills.LOGGING,Skills.MINING,Skills.FISHING,Skills.HARVEST,Skills.TRACK]

    def initSkillTable(db:Database):
        skill_table = db[SkillTable.TABLE_NAME]

        # Build dictionary relating skills to skill categories
        skill_cat_dict = dict.fromkeys(SkillTable.REFINE_SKILLS,SkillCategs.REFINING)
        skill_cat_dict.update(dict.fromkeys(SkillTable.CRAFT_SKILLS,SkillCategs.CRAFTING))
        skill_cat_dict.update(dict.fromkeys(SkillTable.GATHER_SKILLS,SkillCategs.GATHERING))

        # Build list of dictionaries of row data by iterating over dict relating skills and skill categories
        table_data = [{
            SkillTable.SKILLID_COL:skill_enum.value,
            SkillTable.NAME_COL : skill_enum.name.lower(),
            SkillTable.SKILLCATID_COL : cat_enum.value,
        } for skill_enum,cat_enum in skill_cat_dict.items()]

        # Insert into weapon table; Extract category names to new look-up table
        skill_table.insert_all(table_data,pk=SkillTable.SKILLID_COL,ignore=True)
        skill_table.create_index([SkillTable.NAME_COL], unique=True, if_not_exists=True)

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
                    (SkillLogTable.SKILLID_COL, SkillTable.TABLE_NAME)
                ])
        except sql.OperationalError as err:
            if 'already exists' in str(err):
                pass
            else:
                raise err
    
    def insertSkillLog(db: Database, member_id:int, skill_id:int, lvl:int, date:datetime.date=None):
        """Insert an entry into the skill log table. 

        :param db: [description]
        :type db: sqlite3.Database
        :param member_id: [description]
        :type member_id: [type]
        :param skill_id: [description]
        :type skill_id: [type]
        :param date: [description], defaults to None
        :type date: str, optional
        :param log_id: [description], defaults to None
        :type log_id: [type], optional
        """     
        if date == None:
            date = datetime.date.today()
        
        table_data = {
            SkillLogTable.MEMBERID_COL: member_id,
            SkillLogTable.SKILLID_COL: skill_id,
            SkillLogTable.DATE_COL: date,
            SkillLogTable.LEVEL_COL: lvl
        }
        
        db[SkillLogTable.TABLE_NAME].insert(table_data)

    def updateSkillLog(db:Database, log_id:int, skill_id:int=None, lvl:int=None, date:datetime.date=None):
        new_data = {}
        if skill_id != None:
            new_data[SkillLogTable.SKILLID_COL] = skill_id
        if lvl != None:
            new_data[SkillLogTable.LEVEL_COL] = lvl
        if date != None:
            new_data[SkillLogTable.DATE_COL] = date
        
        # Execute if non-empty dict
        if new_data:
            db[SkillLogTable.TABLE_NAME].update(log_id, new_data)


    def deleteSkillLog(db: Database, log_id:int):
        db[SkillTable.TABLE_NAME].delete(log_id)

    def getUserSkills(db : Database, member_id:int):
        """Retrieves the specified users' most recent entries in the SkillLogTable for each skill

        :param db: A database containing a SkillLogTable table
        :type db: Database
        :param member_id: Discord ID of the user 
        :type member_id: int
        """
        results = db.query(f"""SELECT t1.*
        FROM {SkillLogTable.TABLE_NAME} t1 
        INNER JOIN (SELECT {SkillLogTable.SKILLID_COL}, MAX({SkillLogTable.LEVEL_COL}) {SkillLogTable.LEVEL_COL}
            FROM {SkillLogTable.TABLE_NAME}
            GROUP BY {SkillLogTable.SKILLID_COL}
            HAVING {SkillLogTable.MEMBERID_COL} = {member_id}) t2
        ON t1.{SkillLogTable.SKILLID_COL} = t2.{SkillLogTable.SKILLID_COL} AND t1.{SkillLogTable.LEVEL_COL} = t2.{SkillLogTable.LEVEL_COL}
        """)

        return results

    def getTopNSkill(db:Database, skill_id:Skills, n:int=5):
        """Retrieve the N users with the highest level in the specified skill

        :param db: A sqlite-utils database object
        :type db: Database
        :param skill: A value from the Skills enum
        :type skill: Skills
        :param n: Number of users to retrieve , defaults to 5
        :type n: int, optional
        """
        return db.query(f"""SELECT * 
        FROM {SkillLogTable.TABLE_NAME} t1
        INNER JOIN (SELECT {SkillLogTable.MEMBERID_COL}, MAX({SkillLogTable.LEVEL_COL}) {SkillLogTable.LEVEL_COL}
            FROM {SkillLogTable.TABLE_NAME}
            GROUP BY {SkillLogTable.MEMBERID_COL}
            HAVING {SkillLogTable.SKILLID_COL} = {skill_id}) t2
        ON t1.{SkillLogTable.MEMBERID_COL} = t2.{SkillLogTable.MEMBERID_COL} AND t1.{SkillLogTable.LEVEL_COL} = t2.{SkillLogTable.LEVEL_COL}
        ORDER BY {SkillLogTable.LEVEL_COL} DESC
        LIMIT {n}""")

if __name__ == "__main__":
    from random import randint
    from sqlite_utils import Database
    db = Database('skill2.db')
    MemberTable.initMemberTable(db)
    SkillCategTable.initSkillCategTable(db)
    SkillTable.initSkillTable(db)
    SkillLogTable.initSkillLogTable(db)

    # Print all tables in DB
    # for t_name in db.table_names():
    #     print(t_name)
    #     for r in db[t_name].rows:
    #         print(r)

    # Initialize random members
    names = ['a','b','c','d']
    id = list(range(len(names)))
    MemberTable.upsertMembers(db, names, id)

    # Randomly generate table data 
    # for i in range(7):
    #     id = randint(0,len(names)-1)
    #     skill_id = randint(1,5)
    #     lvl = randint(1, 50)
    #     SkillLogTable.insertSkillLog(db, id, skill_id, lvl)
    # SkillLogTable.insertSkillLog(db,0,12,55)
    print("Skill Logs")
    brisketutils.printTable(db[SkillLogTable.TABLE_NAME])
    
    # print("User Query Results:")

    # for r in SkillLogTable.getUserSkills(db, 0):
    #     print(r)

    print("Top N Results:")
    results = db.query(f"""SELECT {SkillLogTable.MEMBERID_COL}, {SkillLogTable.SKILLID_COL}, MAX({SkillLogTable.LEVEL_COL}) {SkillLogTable.LEVEL_COL}
            FROM {SkillLogTable.TABLE_NAME}
            GROUP BY {SkillLogTable.SKILLID_COL}
            --HAVING {SkillLogTable.MEMBERID_COL} = {1}
        """) #SkillLogTable.getTopNSkill(db, 2, 10)
    
    for r in results:
        print(r)