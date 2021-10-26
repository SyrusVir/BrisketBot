import sqlite3 as sql
from sqlite_utils import Database
from typing import List, Union

class MemberTable():
    TABLE_NAME = "members"
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

    def upsertMembers(db:Database, member_name:Union[str,List[str]], discord_ids:Union[int, List[int]]):
        if type(member_name) == list and type(discord_ids) == list:
            if len(member_name) != len(discord_ids):
                raise ValueError("List of members and IDs not of identical lengths")

            table_data = [{MemberTable.DISCORDID_COL : id, MemberTable.NAME_COL : name} for id, name in zip(discord_ids, member_name)]     
        elif type(member_name) == str and type(discord_ids) == int:
            table_data = [{MemberTable.DISCORDID_COL:discord_ids, MemberTable.NAME_COL:member_name}]
        else:
            raise TypeError("Member names and IDs must be either a string and int or a list of strings and a list of ints")

        db[MemberTable.TABLE_NAME].upsert_all(table_data,pk=MemberTable.DISCORDID_COL)

    def deleteMember(db:Database,discord_id:int):
        db[MemberTable.TABLE_NAME].delete(discord_id)

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