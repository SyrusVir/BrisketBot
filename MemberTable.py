import sqlite3 as sql
from sqlite_utils import Database
from typing import List

class MemberTable():
    TABLE_NAME = "members"
    MEMBERID_COL = "MemberID"
    DISCORDID_COL = "DiscordID"
    NAME_COL = "Name"
    DISCORD_IDX = "idx_discord_id"

    def initMemberTable(db : Database):
        member_table = db[MemberTable.TABLE_NAME]
        try:
            member_table.create({
                MemberTable.DISCORDID_COL : int,
                MemberTable.NAME_COL : str
            }, pk=MemberTable.DISCORDID_COL)
        except sql.OperationalError as err:
            if 'already exists' in str(err):
                pass
            else:
                raise err

    def upsertMembers(db:Database, member_name:str, discord_ids:int):
        table_data = {
            MemberTable.DISCORDID_COL : discord_ids,
            MemberTable.NAME_COL : member_name
        }     

        db[MemberTable.TABLE_NAME].upsert(table_data,pk=MemberTable.DISCORDID_COL)

    def deleteMember(db:Database,discord_id:int):
        member_table = db[MemberTable.TABLE_NAME]
        member_table.delete(discord_id)

if __name__ == "__main__":
    import sqlite3 as sql
    from sqlite_utils import Database
    db = Database('test.db')
    MemberTable.initMemberTable(db)
    MemberTable.upsertMembers(db,['d','vir','Duncan','Idaho'], [0,1,2,33])
    
    for r in db[MemberTable.TABLE_NAME].rows:
        x = r[MemberTable.DISCORDID_COL]
        print(r)

    MemberTable.deleteMember(db,x)
    print("Deleted")

    for r in db[MemberTable.TABLE_NAME].rows:
        x = r[MemberTable.DISCORDID_COL]
        print(r)