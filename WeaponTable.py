"""
Defines the look-up tables containing weapons and weapon categories
"""
from sqlite_utils import Database
import sqlite3 as sql
from datetime import datetime
from MemberTable import MemberTable

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
    MAGIC_WEAPONS = [FIRESTAFF, LIFESTAFF, ICEGAUNTLET]

    def initWeaponTable(db : Database):
        weapon_table = db[NWWeapons.TABLE_NAME]

        # Manually construct weapon table
        try:
            weapon_table.create({
                NWWeapons.WEAPONID_COL : int,
                NWWeapons.WEAPONCATEGID_COL : int,
                NWWeapons.NAME_COL : str
            },
            pk=NWWeapons.WEAPONID_COL)
        except sql.OperationalError as err:
            if 'already exists' in str(err):
                pass
            else:
                raise err
        
        # Construct dictionary of weapon names and category names
        weapon_cat_dict = dict.fromkeys(NWWeapons.ONE_HAND_WEAPONS,NWWeaponCategs.ONEHAND)
        weapon_cat_dict.update(dict.fromkeys(NWWeapons.TWO_HAND_WEAPONS,NWWeaponCategs.TWOHAND))
        weapon_cat_dict.update(dict.fromkeys(NWWeapons.RANGE_WEAPONS,NWWeaponCategs.RANGE))
        weapon_cat_dict.update(dict.fromkeys(NWWeapons.MAGIC_WEAPONS,NWWeaponCategs.MAGIC))

        table_data = [{
            NWWeapons.NAME_COL : name,
            NWWeapons.WEAPONCATEGID_COL : cat_name,
        } for name,cat_name in weapon_cat_dict.items()]

        # Insert into weapon table; Extract category names to new look-up table
        weapon_table.insert_all(table_data,pk=NWWeapons.WEAPONID_COL,
            ignore=True, extracts={NWWeapons.WEAPONCATEGID_COL:NWWeaponCategs.TABLE_NAME})
        
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
    PLAYERID_COL = "PlayerID"
    WEAPONID_COL = "WeaponID"
    LEVEL_COL = "Level"
            
    def initWeaponLogTable(db: Database):
        weapon_log_table = db[WeaponLogTable.TABLE_NAME]

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
                    (WeaponLogTable.PLAYERID_COL, MemberTable.TABLE_NAME),
                    (WeaponLogTable.WEAPONID_COL, NWWeapons.TABLE_NAME)
                ])
        except sql.OperationalError as err:
            #TODO: If table exists, ignore excpetion. Continue raise otherwise
            pass
    
    def upsertWeaponLog(db: Database, player_id, weapon_id, date:str=None, log_id=None):
        """
        Add a weapon level update entry. If entry with primary key log_id already exists, update that entry
        """
        weapon_table = db[WeaponLogTable.TABLE_NAME]
        
        if date == None:
            date = datetime.now().date()
        
        table_data = {
            WeaponLogTable.PLAYERID_COL: player_id,
            WeaponLogTable.WEAPONID_COL: weapon_id,
            WeaponLogTable.DATE_COL: date
        }

        # If a log ID specified, add to dictionary
        if log_id != None:
            table_data[WeaponLogTable.UPDATEID_COL] = log_id
        
        weapon_table.upsert(table_data,pk=WeaponLogTable.UPDATEID_COL)

    def deleteWeaponLog(db: Database, log_id:int):
        weapon_table = db[NWWeapons.TABLE_NAME]
        weapon_table.delete(log_id)

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
