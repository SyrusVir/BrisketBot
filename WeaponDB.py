"""
Defines the look-up tables containing weapons and weapon categories
"""
from sqlite_utils import Database
import sqlite3 as sql
import datetime
from enum import IntEnum, auto
from MemberDB import MemberTable

class WeaponCategs(IntEnum):
        ONEHAND =  1
        TWOHAND = auto()
        RANGE = auto() 
        MAGIC = auto() 

class Weapons(IntEnum):
        RAPIER = 1
        SWORD = auto() 
        HATCHET = auto() 
        WARHAMMER = auto() 
        BATTLEAXE = auto() 
        SPEAR = auto() 
        BOW = auto()
        MUSKET = auto() 
        FIRESTAFF = auto() 
        LIFESTAFF = auto() 
        ICEGAUNTLET = auto() 
        VOIDGAUNTLET = auto()
        BLUNDERBUSS = auto()
        DAGGER = auto()
        ONEHANDCLUB = auto()
        TWOHANDCLUB = auto()
        PISTOL = auto()

class WeaponCategTable():
    TABLE_NAME = "weaponcategories"    
    NAME_COL = "WeaponCategory"
    ID_COL = "WeaponID"
    WEAPONCATID_COL = "WeaponCategID"

    
    def initWeaponCategTable(db:Database):
        table_data = [{
            WeaponCategTable.ID_COL : cat.value,
            WeaponCategTable.NAME_COL: cat.name,
        } for cat in WeaponCategs]

        db[WeaponCategTable.TABLE_NAME].insert_all(table_data,pk=WeaponCategTable.ID_COL,ignore=True)

class WeaponsTable():
    
    TABLE_NAME = "weapons"
    WEAPONID_COL = "WeaponID"
    WEAPONCATEGID_COL = "WeaponCategid"
    NAME_COL = "Weapon"

    ONE_HAND_WEAPONS = [Weapons.RAPIER, Weapons.SWORD, Weapons.HATCHET, Weapons.ONEHANDCLUB, Weapons.DAGGER]
    TWO_HAND_WEAPONS = [Weapons.WARHAMMER, Weapons.BATTLEAXE, Weapons.SPEAR, Weapons.TWOHANDCLUB]
    RANGE_WEAPONS = [Weapons.BOW, Weapons.MUSKET, Weapons.BLUNDERBUSS, Weapons.PISTOL]
    MAGIC_WEAPONS = [Weapons.FIRESTAFF, Weapons.LIFESTAFF, Weapons.ICEGAUNTLET, Weapons.VOIDGAUNTLET]

    def initWeaponTable(db : Database):
        weapon_table = db[WeaponsTable.TABLE_NAME]
        try:
            weapon_table.create({
                WeaponsTable.WEAPONID_COL : int,
                WeaponsTable.WEAPONCATEGID_COL : int,
                WeaponsTable.NAME_COL : str
            },pk=WeaponsTable.WEAPONID_COL, foreign_keys=[(WeaponsTable.WEAPONCATEGID_COL,WeaponCategTable.TABLE_NAME)])
        except sql.OperationalError as err:
            if 'already exists' in str(err):
                pass
            else:
                raise err

        weapon_cat_dict = dict.fromkeys(WeaponsTable.ONE_HAND_WEAPONS,WeaponCategs.ONEHAND)
        weapon_cat_dict.update(dict.fromkeys(WeaponsTable.TWO_HAND_WEAPONS,WeaponCategs.TWOHAND))
        weapon_cat_dict.update(dict.fromkeys(WeaponsTable.RANGE_WEAPONS,WeaponCategs.RANGE))
        weapon_cat_dict.update(dict.fromkeys(WeaponsTable.MAGIC_WEAPONS,WeaponCategs.MAGIC))

        table_data = [{
            WeaponsTable.WEAPONCATEGID_COL : weapon_cat_dict[weapon],
            WeaponsTable.WEAPONID_COL : weapon.value,
            WeaponsTable.NAME_COL: weapon.name,
        } for weapon in Weapons]
        
        weapon_table.insert_all(table_data,pk=WeaponsTable.WEAPONID_COL,ignore=True)
        weapon_table.create_index([WeaponsTable.NAME_COL], unique=True, if_not_exists=True)

    def addWeapon(db: Database, weapon_name:str, weapon_cat_id:int):
        weapon_table = db[WeaponsTable.TABLE_NAME]
        weapon_table.insert({
            WeaponsTable.NAME_COL : weapon_name,
            WeaponsTable.WEAPONCATEGID_COL : weapon_cat_id
        },pk=WeaponsTable.WEAPONID_COL)


class WeaponLogTable():
    TABLE_NAME = "weaponlogs"
    UPDATEID_COL = "UpdateId"
    DATE_COL = "Date"
    MEMBERID_COL = "MemberID"
    WEAPONID_COL = "WeaponID"
    LEVEL_COL = "Level"
            
    def initWeaponLogTable(db: Database):
        weapon_log_table = db[WeaponLogTable.TABLE_NAME]

        try:
            weapon_log_table.create({
                WeaponLogTable.UPDATEID_COL : int,
                WeaponLogTable.DATE_COL: str,
                WeaponLogTable.MEMBERID_COL: int,
                WeaponLogTable.WEAPONID_COL: int,
                WeaponLogTable.LEVEL_COL: int
                },
                pk=WeaponLogTable.UPDATEID_COL,
                foreign_keys=[
                    (WeaponLogTable.WEAPONID_COL, WeaponsTable.TABLE_NAME),
                    (WeaponLogTable.MEMBERID_COL, MemberTable.TABLE_NAME)
                ]
            )
        except sql.OperationalError as err:
            if 'already exists' in str(err):
                pass
            else:
                raise err
    
    def insertWeaponLog(db: Database, member_id:int, weapon_id:int, lvl:int, date:datetime.date=None):
        if date == None:
            date = datetime.date.today()

        table_data = {
            WeaponLogTable.MEMBERID_COL : member_id,
            WeaponLogTable.WEAPONID_COL : weapon_id,
            WeaponLogTable.LEVEL_COL : lvl,
            WeaponLogTable.DATE_COL : date
        }
        db[WeaponLogTable.TABLE_NAME].insert(table_data)

    def updateWeaponLog(db: Database, log_id:int, weapon_id:int=None, lvl:int=None, date:datetime.date=None):
        # Construct new data 
        table_data = {}
        if lvl != None:
            table_data[WeaponLogTable.LEVEL_COL] = lvl
        if weapon_id != None:
            table_data[WeaponLogTable.WEAPONID_COL] = weapon_id
        if date != None:
            table_data[WeaponLogTable.DATE_COL] = date 
        
        # Execute update if table data is non-empty
        if table_data:
            db[WeaponLogTable].update(log_id, table_data)

    def deleteWeaponLog(db: Database, log_id:int):
        db[WeaponsTable.TABLE_NAME].delete(log_id)

if __name__ == "__main__":
    import sqlite3 as sql
    from sqlite_utils import Database

    db = Database('test1.db')
    WeaponsTable.initWeaponTable(db)

    print("Weapons")
    for r in db[Weapons].rows:
        print(r)
    print("Weapons Table")
    for r in db[WeaponsTable.TABLE_NAME].rows:
        print(r)

    print("Weapon Cats")
    for r in db[WeaponCategTable.TABLE_NAME].rows:
        print(r)
