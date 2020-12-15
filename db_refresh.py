"""This is database module.

This module load and updates databases if needed.
"""

import glob
import os
import json
import datetime
import requests as rq
import compress_json

db_folder_path = 'databases\\'

def convert_time(timedelta, value):
    """hours timedate.delta converter
    """
    _diff = now - timedelta
    #days
    _diff_d = _diff.days
    #seconds
    _diff_s = _diff.seconds

    #hours
    _diff_h = _diff_s // 3600
    #minutes
    _diff_m = _diff_s // 60
    #return all hours
    if value == 'h':
        return (_diff_d * 24) + _diff_h
    if value == 'm':
        return (_diff_d * 1440) + _diff_m
    return None
def get_vend_data(db_file, vend_array_to_fill, buy_array_to_fill):
    """
    Take db -FILE- and fill 2 arrays with its data
    Parameters
    ----------
    db_file : filepath
        db file itself.
    vend_array_to_fill : list
        array that will hold value for "V" shops.
    buy_array_to_fill : list
        array that will hold value for "B" shops.

    Returns
    -------
    None.

    """
    #открываем файл с сжатой базой

    _shop = compress_json.local_load(db_file)
    if not isinstance(_shop, dict):
        #конвертируем в дикт
        _shop = json.loads(_shop)
    _shop = _shop['shops']
    #with open(db_file, encoding="utf8") as vend_data_file:
        #делаем из него массив только с шопами
    #    _shop = np.array(json.load(vend_data_file)['shops'])
    for _i in _shop:
        #закидываем всю эту ебалу друг за другом
        _t = {"owner": _i["owner"],
              "location": _i["location"]["map"],
              "creation_date": datetime.datetime.strptime(_i["creation_date"],
                                                          "%Y-%m-%dT%H:%M:%SZ"),
              "items": _i["items"]}
        if _i['type'] == 'V':
            vend_array_to_fill.append(_t)
        else:
            buy_array_to_fill.append(_t)
def add_id(demand_array, old_iter, new_iter):
    """
    Add new item to demand
    Parameters
    ----------
    demand_array : TYPE
        DESCRIPTION.
    old_iter : TYPE
        DESCRIPTION.
    new_iter : TYPE
        DESCRIPTION.

    Returns
    -------
    None.

    """
    #функция для первоначального добавления айдишника
    #используется в тех случаях, когда зафиксирована продажа,
    #но конкретно такого предмета еще нет в demand
    #adding item ID
    demand_array.append({"item_id": old_iter['item_id']})
    #ярлык для наполнения массива дополнительными свойствами, если они есть
    def search(value):
        nonlocal old_iter
        nonlocal demand_array
        if value in old_iter:
            demand_array[len(demand_array)-1].update({value: old_iter[value]})
    search('refine')
    search('cards')
    search('star_crumbs')
    search('element')
    search('beloved')
    #adding price:sold amount info
    if isinstance(new_iter, bool):
        _position = demand_array[len(demand_array)-1]
        _position[old_iter['price']] = old_iter['amount']
    else:
        _position = demand_array[len(demand_array)-1]
        _position[old_iter['price']] = old_iter['amount'] - new_iter['amount']
def add_data(demand_array, old_iter, new_iter):
    """
    Parameters
    ----------
    demand_array : list
        array from demand db.
    old_iter : dict
        iteration of old db shop items.
    new_iter : dict or False
        iteration of new db shop items.
        if False, we don't need to count changing amount

    Returns
    -------
    bool
        DESCRIPTION.

    """
    #Функция для добавления данных в массив (у нас это всегда demand)
    #Распределяет, куда в demand нужно добавить предмет
    #используется в тех случаях, когда зафиксирована продажа предмета
    #Функция для поиска соответствия предметов в деманде
    def sameability(demand_item, new_item):
        def search(value, s_demand_item, s_new_item):
            #Автоматизируем поиск
            #суть в том, чтобы протекать несколько раз через такую проверку
            #сравнить предмет из деманда, и тот который мы хотим впилить
            #и если встретится хоть один False, значит похожего не найдено в деманде
            #и следует завести новую пару к айдишнику
            #сравнив само наличие значения
            _newval = False
            _demval = False
            if value in s_new_item:
                _newval = True
            if value in s_demand_item:
                _demval = True
            #если с одной стороны значение есть, а с другой нет,
            #то в любом случае нужно добавить новое значение в деманд
            if (_newval and not _demval) or (_demval and not _newval):
                return False
            #если у нас уже есть запись с таким значением
            if _newval and _demval:
                #нужно проверить соответствие значений
                #если они соответствуют, то просто увеличить количетсво
                #если нет, то завести новую позицию
                if s_new_item[value] == s_demand_item[value]:
                    return True
            return None
        #функция поиска соответствующего предмета в demand
        if demand_item['item_id'] == new_item['item_id']:
            if False in [search('refine', demand_item, new_item),
                         search('cards', demand_item, new_item),
                         search('star_crumbs', demand_item, new_item),
                         search('element', demand_item, new_item),
                         search('beloved', demand_item, new_item)]:
                return False
            return True
        return False
    #Проверяем пустой ли массив, тк если пустой, то просто закинуть айдишник как есть
    if len(demand_array) > 0:
        #сканим существующий массив на соответствия
        for position in demand_array:
            #если есть такой айдишник
            if sameability(position, old_iter):
                #Нужно пройти по второстепенным данным предмета, и
                #искать соответствие именно там, где все второстепенные данные совпадут
                #помечаем что айдишник найден и добавлят заного далее не потребуется
                #проверяем, были ли продажи по такой цене
                #если были, то просто увеличить количество, если нет, то добавить инфу
                if old_iter['price'] in position:
                    if isinstance(new_iter, bool):
                        position[old_iter['price']] += old_iter['amount']
                    else:
                        position[old_iter['price']] += old_iter['amount'] - new_iter['amount']
                else:
                    if isinstance(new_iter, bool):
                        position[old_iter['price']] = old_iter['amount']
                    else:
                        position[old_iter['price']] = old_iter['amount'] - new_iter['amount']
                #отловили все что надо, дальше можно не работать
                return
        #если соответствий не нашли - завести айдишник
        add_id(demand_array, old_iter, new_iter)
    else:
        add_id(demand_array, old_iter, new_iter)
def compare_data(old_vend_data, new_vend_data):
    """
    Compare new and old database and store difference in demand file
    """
    def find_diff(oldshop, newshop):
        diffs = []
        _counter_a = 0
        _counter_b = 0
        #идем по каждому предмету старого списка
        while _counter_a < len(oldshop):
            #если мы не на последнем элементе (даже просто если мы раньше последнего элемента)
            #раньше или = поскольку мы знаем что 2 лист меньше первого
            if _counter_a <= len(newshop) and _counter_b < len(newshop):
                #сверяем, если находим несоответствие
                #то понимаем, что нашли сдвиг листа
                #и итерацию нового шопа следует продолжить с того же места
                if oldshop[_counter_a] != newshop[_counter_b]:
                    diffs.append(oldshop[_counter_a])
                    _counter_b -= 1
            else:
                #оказываемся в месте, где старый шоп больше нового по количеству предметов
                #значит, поскольку верно двигали второй каунтер, все что осталось вне листа
                #можно добавлять в трейд
                diffs.append(oldshop[_counter_a])
            _counter_a += 1
            _counter_b += 1
        return diffs
    #Сравниватель новой и старой базы
    #Сравниваются именно те магазины, которые остались открытыми на момент сравнения
    #Если в таком магазине найдены отличия - заносим их в demand, используя add_data
    #load demand
    ddb = get_demand_data()
    #сравниваем магазины 2 баз
    for new in new_vend_data:
        for old in old_vend_data:
            #если мы находим соответствие в имени создателя магазина
            if new["owner"] == old["owner"]:
                #и во времени создания
                if new['creation_date'] == old['creation_date']:
                    #проверка, что предмет полностью выкуплен
                    #видим, что количество предметов не совпадает
                    if len(new['items']) != len(old['items']):
                        #ищем различия в базах, и заносим тот самый лот из старой базы
                        for k in find_diff(old['items'], new['items']):
                            add_data(ddb, k, False)
                    #начинаем идти по каждому предмету
                    for _m in new['items']:
                        #обоих магазинов
                        for _n in old['items']:
                            #находим соответствие айдишников
                            if _m['item_id'] == _n['item_id']:
                                #проверяем, уменьшилось ли количество предметов
                                if _m['amount'] < _n['amount']:
                                    #записать, сколько и по какой цене было продано
                                    add_data(ddb, _n, _m)
                    break
    def my_func(_e):
        return _e['item_id']
    ddb.sort(key=my_func)
    #сохраняем новую деманд дату
    with open("{}DEMAND.txt".format(db_folder_path), "w", encoding="utf8") as demand_file:
        demand_file.write(str(ddb))
def compare_db(compressed=True):
    """
    Iterate through all available databases
    and compare them one by one
    """
    #wipe demand file
    with open("{}DEMAND.txt".format(db_folder_path), "w", encoding="utf8") as demand_file:
        demand_file.write(str([]))
    #взять все файлы, которые есть в папке с дб,
    #и всем сделать compare_data, по их порядку создания
    if compressed:
        _db_files = sorted(glob.iglob('{}\\jsons\\DB_*.json.gz'.format(db_folder_path)), key=os.path.getctime)
    else:
        _db_files = sorted(glob.iglob('{}\\jsons\\DB_*.json'.format(db_folder_path)), key=os.path.getctime)
    #create temporary lists, that will hold db data
    _older_vend_data = []
    _newer_vend_data = []
    #
    _older_buy_data = []
    _newer_buy_data = []
    #iterate through all dbs
    for _n in range(len(_db_files)-1):
        print('comparing {} and {} db out of {}'.format(_n+1, _n+2, len(_db_files)))

        #get data from dbs
        if _older_vend_data == [] and _older_buy_data == []:
            #take older file
            get_vend_data(_db_files[_n], _older_vend_data, _older_buy_data)
        #compare it with newer file (+1)
        get_vend_data(_db_files[_n+1], _newer_vend_data, _newer_buy_data)
        #compare 2 datas and fill demand file
        compare_data(_older_vend_data, _newer_vend_data)
        compare_data(_older_buy_data, _newer_buy_data)
        #saving data that is already compared, and making it count as old one
        _older_vend_data = _newer_vend_data
        _older_buy_data = _newer_buy_data
        #wipe new data for next cycle
        _newer_vend_data = []
        _newer_buy_data = []
def compress_all_db():
    """
    Iterate through all available databases
    and compress them one by one
    """
    #взять все файлы, которые есть в папке с дб,
    #и всем сделать compress_data, по их порядку создания
    _db_files = sorted(glob.iglob('{}\\jsons\\DB_*.json'.format(db_folder_path)), key=os.path.getctime)
    #iterate through all dbs
    for _n in range(len(_db_files)):
        print('compressing {} db out of {}'.format(_n+1, len(_db_files)))
        #берем файл, достаем из него инфу и компрессим ее в новый файл
        with open(_db_files[_n], encoding="utf8") as json_file:
            compress_json.dump(json.load(json_file), "{}.gz".format(_db_files[_n]))
def get_demand_data():
    """
    function to get demand data from file
    """
    with open("{}DEMAND.txt".format(db_folder_path), "r", encoding="utf8") as demand_file:
        return eval(demand_file.read(), {'__builtins__':None}, {})
def last_db_time_get():
    latest_file = max(glob.glob('{}\\jsons\\DB_*.json.gz'.format(db_folder_path)), key=os.path.getctime)
    #выгружаем ее в переменную
    db_file = compress_json.local_load(latest_file)
    #если оказалось, что база выгружена текстом, а не диктом
    if not isinstance(db_file, dict):
        #конвертируем в дикт
        db_file = json.loads(db_file)
    #конвертируем ее время создания
    db_time = db_file["generation_timestamp"]
    db_conv_time = datetime.datetime.strptime(db_time, "%Y-%m-%dT%H:%M:%S.%fZ")
    return db_conv_time
def api_db_load(vend, buy, db_compare=False, compressed=True):
    """
    Make api call, save new db, compare new db with old one and save demand
    Parameters
    ----------
    vend : list
        list that will store vend data.
    buy : list
        list that will store vend data.
    db_compare : TYPE, optional
        if we want to compare all available dbs. The default is False.

    Returns
    -------
    None.

    """
    #находим последнюю сжатую базу
    if compressed:
        db_conv_time = last_db_time_get()
        if not db_compare:
            if convert_time(db_conv_time, 'm') > 9: #9
                print("Old database...")
                #собираем ссылку
                link = 'https://api.originsro.org/api/v1/market/list?api_key='
                api_key = 'r3bkd0q8umxhuj75ahtvwpgkd3yzi3rm'
                #делаем вызов и сохраняем получаемое в переменной
                response = rq.get('{}{}'.format(link, api_key))
                #создаем путь/имя для нашей новой базы
                latest_file = '{}\\jsons\\DB_{}.json.gz'.format(db_folder_path, now.strftime("%d-%m-%Y_%H-%M-%S"))
                #сохраняем нашу новую базу
                compress_json.dump(response.text, latest_file)
                print('compressed db saved')
                #и сразу же загружаем
                #actual_db = compress_json.local_load(latest_file)
                #находим 2 по старости дб (то есть ту, которая была перед нашей только что выкачанной)
                previous_db = sorted(glob.iglob('{}\\jsons\\DB_*.json.gz'.format(db_folder_path)), key=os.path.getctime)[-2]
                #распаковываем его
                #previous_db_uncompressed = compress_json.local_load(previous_db)
                #создаем временные листы с данными
                #из прошлой бд
                pre_vendor_shops = []
                pre_buy_shops = []
                get_vend_data(previous_db, pre_vendor_shops, pre_buy_shops)
                #из новой бд
                print(latest_file)
                get_vend_data(latest_file, vend, buy)
                #fill demand file
                compare_data(pre_vendor_shops, vend)
                compare_data(pre_buy_shops, buy)
                print('demand refreshed')
            else:
                print('Database ok...')
                latest_file = max(glob.glob('{}\\jsons\\DB_*.json.gz'.format(db_folder_path)), key=os.path.getctime)
                get_vend_data(latest_file, vend, buy)
        else:
            compare_db()
    else:
        #находим самую свежую базу из имеющихся
        latest_file = max(glob.glob('{}\\jsons\\DB_*.json'.format(db_folder_path)), key=os.path.getctime)
        #Загрузка БД и ее обновление
        with open(latest_file, encoding="utf8") as json_file:
            #делаем удобное обозначение той же базы
            api_db = json.load(json_file)['generation_timestamp']
            db_time = datetime.datetime.strptime(api_db, "%Y-%m-%dT%H:%M:%S.%fZ")
            if not db_compare:
                #если базе больше 10 минут, надо обновить
                if convert_time(db_time, 'm') > 10: #9
                    print("Old database...")
                    link = 'https://api.originsro.org/api/v1/market/list?api_key='
                    api_key = 'r3bkd0q8umxhuj75ahtvwpgkd3yzi3rm'
                    response = rq.get('{}{}'.format(link, api_key))
                    latest_file = '{}\\jsons\\DB_{}.json'.format(db_folder_path, now.strftime("%d-%m-%Y_%H-%M-%S"))
                    #создаем новую бд с названием из latest_file
                    with open(latest_file, "w+", encoding="utf8") as new_file:
                        new_file.write(response.text)
                    #создаем новую, сжатую, бд
                    #compress_json.dump(response.text, latest_file)
                    #находим второй по новости файл, то есть прошлую бд
                    previous_db = sorted(glob.iglob('{}\\jsons\\DB_*.json'.format(db_folder_path)), key=os.path.getctime)[-2]
                    #создаем временные листы с данными
                    #из прошлой бд
                    pre_vendor_shops = []
                    pre_buy_shops = []
                    get_vend_data(previous_db, pre_vendor_shops, pre_buy_shops)
                    #из новой бд
                    get_vend_data(latest_file, vend, buy)
                    #fill demand file
                    compare_data(pre_vendor_shops, vend)
                    compare_data(pre_buy_shops, buy)
                else:
                    print('Database ok...')
                    get_vend_data(latest_file, vend, buy)
            else:
                compare_db()
def item_db_load(items_database):
    """
    Load items database

    Parameters
    ----------
    items_database : list
        empty list that will store database data.

    Returns
    -------
    None.

    """
    #Подгружаем базу предметов
    with open('{}ITEMS.json'.format(db_folder_path), encoding="utf8") as items_file:
        items = json.load(items_file)
        for i in items['items']:
            items_database.append(i)
        """
        for _di in items['items']:
            _item_id = _di['item_id']
            _unique_name = _di['unique_name']
            _name = _di['name']
            _type = _di['type']
            if 'subtype' in _di:
                _subtype = _di['subtype']
            else:
                _subtype = None
            _npc_price = _di['npc_price']
            if 'slots' in _di:
                _slots = _di['slots']
            else:
                _slots = 0
            _app_data = {'item_id': _item_id,
                         'unique_name': _unique_name,
                         'name': _name,
                         'type': _type,
                         'subtype': _subtype,
                         'npc_price': _npc_price,
                         'slots': _slots}
            items_database.append(_app_data)
        """

def monster_db_load():
    #подгрузка базы монстров
    with open('{}monster_db.json'.format(db_folder_path), 'r', encoding="utf8") as monster_db_file:
        return json.loads(monster_db_file.read())


#create lists
vend_db, buy_db, demand_db, item_db, monster_db = [], [], [], [], []
#fill monsters
monster_db = monster_db_load()
#fill items
item_db_load(item_db)

if True:
    now = datetime.datetime.utcnow()
    #fill vend and buy
    api_db_load(vend_db, buy_db)
    #fill demand
    demand_db = get_demand_data()
    db_time = last_db_time_get()