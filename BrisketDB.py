import sqlite_utils
from MemberDB import MemberTable
import WeaponDB
import SkillDB
from BankDB import BankTable
from CharacterDB import CharacTable 
from sqlite_utils import Database


class BrisketDB(sqlite_utils.Database):
    """BrisketDB subclasses sqlite_utils.Database class, adding to constructor initialization of company tables
    """

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        MemberTable.initMemberTable(self)
        MemberTable.upsertMembers(self, ["hello","world","JA","HP","GT","JH"], list(range(6)))
        WeaponDB.WeaponCategTable.initWeaponCategTable(self)
        WeaponDB.WeaponsTable.initWeaponTable(self)
        WeaponDB.WeaponLogTable.initWeaponLogTable(self)
        SkillDB.SkillCategTable.initSkillCategTable(self)
        SkillDB.SkillTable.initSkillTable(self)
        SkillDB.SkillLogTable.initSkillLogTable(self)
        BankTable.initBankLogTable(self,28500.13)
        CharacTable.initCharacLogTable(self)


if __name__ == "__main__":
    db = BrisketDB('test.db')
    print(db.table_names())
    for t_name in db.table_names():
        print(db[t_name].schema)