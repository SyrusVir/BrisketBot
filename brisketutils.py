import sqlite_utils
from discord_slash import SlashContext
from typing import List
import matplotlib as plt
from sqlite_utils.db import NotFoundError, Table

def checkRecordPermission(table:sqlite_utils.db.Table, column:str, pk_kwarg:str):
    """When altering records, the ID of the user requesting alteration must match ID in record being altered.

    :param fcn: [description]
    :type fcn: [type]
    :param ctxt: [description]
    :type ctxt: SlashContext
    :param id: [description]
    :type id: int
    :param table: [description]
    :type table: sqlite_utils.db.Table
    :param col: [description]
    :type col: str
    """
    def decorator(func):
        def inner(*args, **kwargs):
            pk = kwargs[pk_kwarg]
            try:
                row = table.get(pk)
            except NotFoundError:
                print()
    table.get(id)

def listDictToDictList(listdict:List[dict]):
    """Converts a list of dictionaries to a dictionary of lists.
       Assumes all dictionaries in the provided last have the same keys.
       

    :param listdict: A list of dictionaries with identical keys
    :type listdict: List[dict]
    :return: dictlist
    :returntype: dict
    """
    if listdict == []:
        return []

    return {k : [d[k] for d in listdict] for k in listdict[0].keys()}

def dictListToListDict(dictlist:dict):
    """Converts a dictionary of lists to a list of dictionaries

    :param dictlist: A dictionary where the values are assumed lists
    :type dictlist: dict
    :return: listdict
    :rtype: List[dict]
    """
    return [dict(zip(dictlist,t)) for t in zip(*dictlist.values())]

def formatTable(dictlist:dict)->str:
    """Provided a dictionary of lists, format contents into a printable table string

    :param dictlist: [description]
    :type dictlist: dict
    :return: [description]
    :rtype: str
    """
    header_str = '|'.join(k.center(10) for k in dictlist.keys())
    header_str = '|'+header_str + '|\n'
    header_str = header_str + len(header_str)*'-'+'\n'
    for row in zip(*dictlist.values()):
        for s in row:
            header_str = header_str + '|' + str(s).center(10)
        header_str = header_str + '|\n'
    return header_str

def printTable(table:Table):
    for r in table.rows:
        print(r)