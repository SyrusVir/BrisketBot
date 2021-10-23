"""
Defines the look-up tables containing weapons and weapon categories
"""
from sqlite_utils import Database
import sqlite3 as sql
import datetime
# from MemberTable import MemberTable

class NWWeaponCategs():
    TABLE_NAME = "weaponcategories"
    NAME_COL = "WeaponCategory"

    ONEHAND = 'onehanded'
    TWOHAND = "twohanded"
    RANGE = "ranged"
    MAGIC = "magic"

class NWWeapons():
    
    TABLE_NAME = "weapons"
    WEAPONID_COL = "weaponid"
    WEAPONCATEGID_COL = "WeaponCategid"
    NAME_COL = "weapon"

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

    ONE_HAND_WEAPONS = [RAPIER, SWORD, HATCHET]
    TWO_HAND_WEAPONS = [WARHAMMER, BATTLEAXE, SPEAR]
    RANGE_WEAPONS = [BOW, MUSKET]
    MAGIC_WEAPONS = [FIRESTAFF, LIFESTAFF, ICEGAUNTLET, "new"]

    def initWeaponTable(db : Database):
        weapon_table = db[NWWeapons.TABLE_NAME]
        weapon_cat_table = db[NWWeaponCategs.TABLE_NAME]

        weapon_cat_dict = dict.fromkeys(NWWeapons.ONE_HAND_WEAPONS,NWWeaponCategs.ONEHAND)
        weapon_cat_dict.update(dict.fromkeys(NWWeapons.TWO_HAND_WEAPONS,NWWeaponCategs.TWOHAND))
        weapon_cat_dict.update(dict.fromkeys(NWWeapons.RANGE_WEAPONS,NWWeaponCategs.RANGE))
        weapon_cat_dict.update(dict.fromkeys(NWWeapons.MAGIC_WEAPONS,NWWeaponCategs.MAGIC))

        # Add weapon category names to a lookup table
        for categ_name in [NWWeaponCategs.ONEHAND,NWWeaponCategs.TWOHAND,NWWeaponCategs.RANGE,NWWeaponCategs.MAGIC]:
            weapon_cat_table.lookup({NWWeaponCategs.NAME_COL:categ_name})

        # Add weapon names to a lookup table
        for weapon_name in NWWeapons.ONE_HAND_WEAPONS + NWWeapons.TWO_HAND_WEAPONS + NWWeapons.RANGE_WEAPONS + NWWeapons.MAGIC_WEAPONS:
            weapon_table.lookup({NWWeapons.NAME_COL:weapon_name})

        # Iterate over weapon names in lookup table. Use weapon-category dictionary to retrieve category ID from weapon cat lookup table
        # Insert ID data using alter=True to automatically add columns and set references
        for r in weapon_table.rows:
            weapon_id = r["id"]
            weapon_name = r[NWWeapons.NAME_COL]
            weapon_cat_name = weapon_cat_dict[weapon_name]
            weapon_cat_id = weapon_cat_table.lookup({NWWeaponCategs.NAME_COL:weapon_cat_name})
            weapon_table.upsert({"id": weapon_id,NWWeapons.WEAPONCATEGID_COL:weapon_cat_id},
                pk="id",
                alter=True,
                foreign_keys=[(NWWeapons.WEAPONCATEGID_COL,NWWeaponCategs.TABLE_NAME)])
            
        weapon_table.create_index([NWWeapons.NAME_COL], unique=True, if_not_exists=True)

    def addWeapon(db: Database, weapon_name:str, weapon_cat_id:int):
        weapon_table = db[NWWeapons.TABLE_NAME]
        weapon_table.insert({
            NWWeapons.NAME_COL : weapon_name,
            NWWeapons.WEAPONCATEGID_COL : weapon_cat_id
        },pk=NWWeapons.WEAPONID_COL)


class WeaponLogTable():
    TABLE_NAME = "WeaponLog"
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
                    (WeaponLogTable.WEAPONID_COL, NWWeapons.TABLE_NAME)
                ])
        except sql.OperationalError as err:
            #TODO: If table exists, ignore excpetion. Continue raise otherwise
            pass
    
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
        db[NWWeapons.TABLE_NAME].delete(log_id)

if __name__ == "__main__":
    import sqlite3 as sql
    from sqlite_utils import Database

    db = Database('test1.db')
    NWWeapons.initWeaponTable(db)

    print("Weapons Table")
    for r in db[NWWeapons.TABLE_NAME].rows:
        print(r)

    print("Weapon Cats")
    for r in db[NWWeaponCategs.TABLE_NAME].rows:
        print(r)
