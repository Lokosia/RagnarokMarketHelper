"""This is item_db functions module.

This module hold functions that works with item database.
"""

import math

def item_db_search(item_db, item_id):
    """
    Find item in items database

    Parameters
    ----------
    item_db : list
        item database itself.
    item_id : int or str
        search item by its id or unique name.

    Returns
    -------
    _i_id : dict
        item_id; unique_name; name; type; npc_price;

    """
    if isinstance(item_id, int):
        for _i_id in item_db:
            if _i_id['item_id'] == item_id:
                return _i_id
    if isinstance(item_id, str):
        for _i_id in item_db:
            if item_id == _i_id['unique_name']:
                return _i_id
    return None
def item_db_merch(item_db, item_id):
    """
    Find selling price of an item to NPC including overprice

    Parameters
    ----------
    item_db : list
        item database itself.
    item_id : int or str
        search item by its id or unique name.

    Returns
    -------
    int
        npc sell price including overprice.

    """
    return math.floor((item_db_search(item_db, item_id)['npc_price']/2)*1.24)
def item_name(item_db, item_id):
    """
    Convert item id to its actual name

    Parameters
    ----------
    item_db : list
        item database itself.
    item_id : int or str
        search item by its id or unique name.

    Returns
    -------
    str
        item name.

    """
    _s_i = item_db_search(item_db, item_id)
    if _s_i['type'] == "IT_WEAPON" or _s_i['type'] == "IT_ARMOR":
        if 'slots' in _s_i:
            return '{name} [{slots}]'.format(name=_s_i['name'], slots=_s_i['slots'])
    return _s_i['name']

