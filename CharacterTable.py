import datetime
import sqlite3 as sql
from sqlite_utils import Database
from sqlite_utils.db import Table
from MemberTable import MemberTable
from WeaponTable import NWWeapons

class CharacTable():
    TABLE_NAME = "characterlevellog"
    LOGID_COL = "CharacLogID"
    DATE_COL = "Date"
    MEMBERID_COL = "MemberID"
    LEVEL_COL = "CharacterLevel"

    def initCharacLogTable(db:Database):
        char_table = db[CharacTable.TABLE_NAME]
        char_table.create({
            CharacTable.LOGID_COL : int,
            CharacTable.DATE_COL : str,
            CharacTable.MEMBERID_COL : int,
            CharacTable.LEVEL_COL : int
        },
        pk=CharacTable.LOGID_COL,
        foreign_keys=[(CharacTable.MEMBERID_COL, MemberTable.TABLE_NAME)])

    def upsertCharacLog(db:Database, member_id:int, lvl:int, date:datetime.date=None, id=None):
        char_table = db[CharacTable.TABLE_NAME]

        if date == None:
            date = datetime.date.today()

        table_data = {
            CharacTable.MEMBERID_COL : member_id,
            CharacTable.LEVEL_COL : lvl,
            CharacTable.DATE_COL : date
        }

        if id != None:
            table_data[CharacTable.LOGID_COL] = id

        char_table.upsert(table_data)

    def deleteCharacLog(db:Database, id:int):
        db[CharacTable.TABLE_NAME].delete(id)

    
    if __name__ == "__main__":
        pass