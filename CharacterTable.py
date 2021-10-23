import datetime
import sqlite3 as sql
from sqlite_utils import Database
# from MemberTable import MemberTable

class CharacTable():
    TABLE_NAME = "characterlevellog"
    LOGID_COL = "CharacLogID"
    DATE_COL = "Date"
    MEMBERID_COL = "MemberID"
    LEVEL_COL = "CharacterLevel"

    def initCharacLogTable(db:Database):
        char_table = db[CharacTable.TABLE_NAME]
        try:
            char_table.create({
                CharacTable.LOGID_COL : int,
                CharacTable.DATE_COL : str,
                CharacTable.MEMBERID_COL : int,
                CharacTable.LEVEL_COL : int
            },
            pk=CharacTable.LOGID_COL)
        except sql.OperationalError as err:
            if 'already exists' in str(err):
                pass
    
    def insertCharacLog(db:Database, member_id:int, lvl:int, date:datetime.date=None):
        table_data = {
            CharacTable.MEMBERID_COL : member_id,
            CharacTable.LEVEL_COL : lvl,
            CharacTable.DATE_COL : date
        }
        db[CharacTable.TABLE_NAME].insert(table_data)
    
    def updateCharacLog(db:Database, log_id:int, lvl:int=None, date:datetime.date=None):
        table_data = {}
        if lvl != None:
            table_data[CharacTable.LEVEL_COL] = lvl
        if date != None:
            table_data[CharacTable.DATE_COL] = date
        
        # Execute update if table data is non-empty
        if table_data:
            db[CharacTable.TABLE_NAME].update(log_id, table_data)

    def deleteCharacLog(db:Database, id:int):
        db[CharacTable.TABLE_NAME].delete(id)

    
    if __name__ == "__main__":
        pass