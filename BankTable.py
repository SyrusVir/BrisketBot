import sqlite3 as sql
from sqlite_utils import Database
from sqlite_utils.db import NotFoundError
from MemberTable import MemberTable
import datetime

class BankTable():
    TABLE_NAME = "bank_logs"
    XACTID_COL = "XactID"
    DATE_COL = "Date"
    MEMBERID_COL = "MemberID"
    AMNT_COL = "Amount"
    NOTE_COL = "Note"

    def initBankLogTable(db:Database, init_bal=0):
        bank_log_table = db[BankTable.TABLE_NAME]
        
        # Creating bank table and initializing to initial bank balance
        try:
            bank_log_table.create({
                BankTable.XACTID_COL : int,
                BankTable.DATE_COL : str,
                BankTable.MEMBERID_COL : int,
                BankTable.AMNT_COL : float,
                BankTable.NOTE_COL : str
            }, pk=BankTable.XACTID_COL, foreign_keys=[(BankTable.MEMBERID_COL,MemberTable.TABLE_NAME)])

            bank_log_table.insert({
                BankTable.XACTID_COL: 0,
                BankTable.AMNT_COL : init_bal,
                BankTable.NOTE_COL : "Initial Bank Balance",
                BankTable.DATE_COL : datetime.datetime.now().date()
            })
        except sql.OperationalError as err:
            if 'already exists' in str(err):
                pass
            else:
                raise err

    def insertBankLog(db:Database, member_id:int, amount:float, date:datetime.date=None,note:str=None):
        if date == None:
            date = datetime.date.today()
        
        db[BankTable.TABLE_NAME].insert({
            BankTable.MEMBERID_COL : member_id,
            BankTable.AMNT_COL : amount,
            BankTable.DATE_COL : date,
            BankTable.NOTE_COL : note
        })


    def updateBankLog(db:Database,xact_id:int, amount:float=None, date:datetime.date=None, note:str=None):
        bank_log_table = db[BankTable.TABLE_NAME]

        table_data = {}
        if amount != None:
            table_data[BankTable.AMNT_COL] = amount
        if date != None:
            table_data[BankTable.DATE_COL] = date
        if note != None: 
            table_data[BankTable.NOTE_COL] = note

        # Execute update if table data is non-empty
        if table_data:
            bank_log_table.update(xact_id, table_data)

    def deleteBankLog(db:Database,xact_id:int):
        db[BankTable.TABLE_NAME].delete(xact_id)

if __name__ == "__main__":
    pass
