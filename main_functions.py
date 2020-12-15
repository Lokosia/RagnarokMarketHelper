#imported libraries
from operator import itemgetter
import math
from tabulate import tabulate
from statistics import median
import os
import json

#my functions
from item_db_functions import item_name, item_db_search, item_db_merch
from market_system_functions import find_market_id, vend_score, find_market_price, shop_item_name, market_average, kwargs_constructor
import db_refresh as db
item_db = db.item_db
buy_db = db.buy_db
vend_db = db.vend_db
db_folder_path = db.db_folder_path
db_time = db.db_time

def benefits_buy_founder():
    state = None
    filepath = '{}benefits.txt'.format(db_folder_path)
    #проверям, что файл не пустой
    if os.stat(filepath).st_size == 0:
        state = 'save'
    if state is None:
        with open (filepath, 'r') as benefits_file:
            #запоминаем дату
            loaded_file = json.load(benefits_file)
            if 'creation_date' in loaded_file:
                benefits_creation_date = loaded_file['creation_date']
            else:
                state = 'save'
    if state is None:
        #если дата не соответствует новой бд
        if benefits_creation_date != str(db_time):
            state = 'save'
        else:
            #загрузить данные из файла и вернуть их в нужном формает
            with open(filepath, 'r') as benefits_file:
                return json.load(benefits_file)['data']
    if state == 'save':
        buy_benefits = []
        npc_benefits = []
        #идем по базе продаваемого и по базе покупаемого
        #если цена предмета продаваемого < цена покупаемого
        #добавит в лист значение @navshop имя торговца - локация - название предмета - венд цена
        #идем по каждому магазину
        for s in vend_db:
            #идем по каждому предмету магазина
            for _it in s['items']:
                to_buy = False
                to_NPC = False
                #==========================================================BUY
                #если нам удается найти соответствие ID в бай шопе
                _fmi = find_market_id(buy_db, _it['item_id'])
                if len(_fmi) > 0:
                    #нужно сравнить цены, и если цена покупки на венде меньше, чем цена продажи в бае - занести в список
                    _s_fmi = sorted(_fmi, key=itemgetter('price'), reverse=True)
                    if _it['price'] < _s_fmi[0]['price']:
                        _vendor_name = s['owner']
                        _vendor_location = s['location']
                        
                        _vendor_item_name = item_name(item_db, _s_fmi[0]['item_id'])
                        _vendor_item_price = _it['price']
                        _vendor_item_amount = _it['amount']
                        
                        _buyer_name = _s_fmi[0]['owner']
                        _buyer_location = _s_fmi[0]['location']
                        _buyer_item_price = _s_fmi[0]['price']
                        _buyer_item_amount = _s_fmi[0]['amount']
                        #item amount check
                        if _vendor_item_amount > _buyer_item_amount:
                            _am = _buyer_item_amount
                        else:
                            _am = _vendor_item_amount
                            
                        _buy_profit = (_am*_buyer_item_price)-(_am*_vendor_item_price)
                        if _buy_profit >= 5000:
                            to_buy = True
                #==========================================================NPC
                for npc in item_db:
                    if npc['item_id'] == _it['item_id']:
                        if math.floor((npc['npc_price']/2)*1.24) > _it['price']:
                            _trader_name = s['owner']
                            _location = s['location']
                            _item_name = npc['name']
                            _vend_price = _it['price']
                            _sell_price = math.floor((npc['npc_price']/2)*1.24)
                            _item_amount = _it['amount']
                            _npc_profit = (_it['amount']*_sell_price)-(_item_amount*_vend_price)
                            if _npc_profit >= 5000:
                                to_NPC = True
                        break
                #if both, add ti kist where profit is higher
                if to_buy and to_NPC:
                    if _buy_profit > _npc_profit:
                        buy_benefits.append([_vendor_name, _vendor_location, _buyer_name, _buyer_location, _vendor_item_name, _am, _buy_profit])
                    else:
                        npc_benefits.append([_trader_name, _location, _item_name, _vend_price, _sell_price, _npc_profit])
                if to_buy:
                    buy_benefits.append([_vendor_name, _vendor_location, _buyer_name, _buyer_location, _vendor_item_name, _am, _buy_profit])
                if to_NPC:
                    npc_benefits.append([_trader_name, _location, _item_name, _vend_price, _sell_price, _npc_profit])
        if len(buy_benefits) > 0:
            buy_benefits = sorted(buy_benefits, key=lambda x: x[6], reverse = True)
        if len(npc_benefits) > 0:
            npc_benefits = sorted(npc_benefits, key=lambda x: x[1])
        redict = {'buy': buy_benefits, 'npc': npc_benefits}
        redict = {'creation_date': str(db_time), 'data': redict}
        with open(filepath, 'w') as benefits_file:
            #срохраняем файл
            json.dump(redict, benefits_file)
        return redict['data']
        
def market_stonks(zeny = 2000000000):
    #проверить время в файле
    #если совпадает, то вытянуть инфу из файла и вернуть ее
    #если нет, то провести всю функцию, в конце сохранить файл и вернуть новые значения
    state = None
    filepath = '{}stonks.txt'.format(db_folder_path)
    #проверям, что файл не пустой
    if os.stat(filepath).st_size == 0:
        state = 'save'
    if state is None:
        with open (filepath, 'r') as stonks_file:
            #запоминаем дату
            loaded_file = json.load(stonks_file)
            if 'creation_date' in loaded_file:
                stonks_creation_date = loaded_file['creation_date']
            else:
                state = 'save'
    if state is None:
        #если дата не соответствует новой бд
        if stonks_creation_date != str(db_time):
            state = 'save'
        else:
            #загрузить данные из файла и вернуть их в нужном формает
            with open(filepath, 'r') as stonks_file:
                return json.load(stonks_file)['data']
    if state == 'save':
        def market_viability(owner, price, m_price, item_id, **kwargs):
            global vend_db
            market_now = find_market_id(vend_db, item_id, **kwargs)
            #идем по каждому предложению в данный момент
            for m in market_now:
                #если это не тот же магазин
                if m['owner'] != owner:
                    #если находится цена еще ниже взятой, то сразу отбой
                    if m['price'] < i['price']:
                        return False
                    #если просто есть другой чел, у которого цена тоже пошла бы в профит по алгоритму
                    if m['price'] < m_price:
                        return False
            return True
                        
        stonks25 = []
        stonks50 = []
        #print('Checking stonks...')
        for s in vend_db:
            #если магазину менее 6 часов
            if db.convert_time(s['creation_date'], 'h') < 6:
                #идем по каждому предмету
                for i in s['items']:
                    #если это ваще стоящий для продажи предмет
                    if vend_score(i['item_id']) <= 425:
                        #сразу проверяем время шопа, потому что исследовать дерьмо мамонта нет смысла и очень затратно по питону
                        _kwargs = {}
                        kwargs_constructor(i, _kwargs, 'refine')
                        kwargs_constructor(i, _kwargs, 'cards')
                        kwargs_constructor(i, _kwargs, 'star_crumbs')
                        kwargs_constructor(i, _kwargs, 'element')
                        _ma = find_market_price(i['item_id'], i['amount'], **_kwargs)
                        if (type(_ma) != str) and (type(_ma) != list) and i['price'] < zeny:
                            if _ma > i['price']:
                                #проверка, что нет других таких же челиков с низкой ценой
                                if market_viability(s['owner'], i['price'], _ma, i['item_id'], **_kwargs):
                                    #if not "no such item in demand"
                                    _profit = (_ma - i['price']) * i['amount']
                                    if _profit > 50000:
                                        if _ma - (_ma*0.50) > i['price']:
                                            #stonks50.append(i)
                                            stonks50.append([s['owner'], s['location'], shop_item_name(i), i['amount'], i['price'], _ma, _profit])
                                        elif _ma - (_ma*0.25) > i['price']:
                                            #stonks25.append(i)
                                            stonks25.append([s['owner'], s['location'], shop_item_name(i), i['amount'], i['price'], _ma, _profit])
        if len(stonks50) > 0:
            stonks50 = sorted(stonks50, key=lambda x: x[-1], reverse = True)
        if len(stonks25) > 0:
            stonks25 = sorted(stonks25, key=lambda x: x[-1], reverse = True)
        redict = {'Uber stonks': stonks50, 'OK stonks': stonks25}
        redict = {'creation_date': str(db_time), 'data': redict}
        with open(filepath, 'w') as stonks_file:
            #срохраняем файл
            json.dump(redict, stonks_file)
        return redict['data']
        
#Основной скрипт нахождения цен
#нужно прогнать предмет с его количеством по find market price
#если цена не равно "vend to shop", то умножить ее на вероятность продажи
#и закинуть в массив в формате [{item_name: %%, vend_price: %%, profit: %%}]
#отсортировать массив по профиту и выдать список
def estimate_storage(storage_nf):
    #лист, оцененный на продажу на венде
    _vend = []
    #лист, оцененный на продажу нпц или холд
    _npc = []
    #лист для байеров
    _buyers = []
    #идем по листу склада
    for i in storage_nf:
        _kwargs = {}
        kwargs_constructor(i, _kwargs, 'refine')
        kwargs_constructor(i, _kwargs, 'cards')
        kwargs_constructor(i, _kwargs, 'star_crumbs')
        kwargs_constructor(i, _kwargs, 'element')
        
        _stor_result = find_market_price(i['item_id'], i['amount'], **_kwargs)
        
        #NPC
        if _stor_result == 'NPC' or _stor_result == -1:
            _profit = math.floor((item_db_search(item_db, i['item_id'])['npc_price']/2)*1.24) * i['amount']
            if _profit > 1:
                _npc.append([shop_item_name(i), _profit])
        #BUYERS
        elif type(_stor_result) == list:
            _profit = i['amount'] * _stor_result[3]
            if _profit > 10000:
                _buyers.append([_stor_result[0], shop_item_name(i), _stor_result[2], _profit])
        #VEND
        else:
            _profit = _stor_result * i['amount']
            if _profit > 10000:
                _vend_score = vend_score(i['item_id'], **_kwargs)
                _vend.append([shop_item_name(i), _stor_result, _profit, _vend_score])
    #NPC
    #count overall profit
    #=========================
    npc_sum = 0
    for b in range(len(_npc)):
        npc_sum += _npc[b][1]
    #=========================
    if npc_sum > 20:
        _npc = sorted(_npc, key=lambda x: x[1], reverse=True)
        _npc.append(['Overall', npc_sum])   
    #BUY
    buy_sum = 0
    for b in range(len(_buyers)):
        buy_sum += _buyers[b][3]
    if buy_sum > 10000:
        _buyers = sorted(_buyers, key=lambda x: x[3], reverse=True)
        _buyers.append(['', '', 'Overall', buy_sum])
    #VEND
    _vend = sorted(_vend, key=lambda x: x[3])
    total = {'npc': _npc, 'buy': _buyers, 'vend': _vend}
    return total



def gift_box_value():
    #взять предмет из коробки, прикинуть его цену, сохранить ее в листе, весь лист смедианить и вернуть
    def gbv_convert(item_id):
        fmp = find_market_price(item_id)
        if type(fmp) == list:
            return fmp[3]
        elif type(fmp) == str:
            return item_db_merch(item_id)
        else:
            return fmp
    gbv = []
    gbv.append(gbv_convert(1558))
    gbv.append(gbv_convert(4005))
    gbv.append(gbv_convert(603))
    gbv.append(gbv_convert(617))
    gbv.append(gbv_convert(644))
    gbv.append(gbv_convert(501))
    gbv.append(gbv_convert(502))
    gbv.append(gbv_convert(503))
    gbv.append(gbv_convert(504))
    gbv.append(gbv_convert(505))
    gbv.append(gbv_convert(506))
    gbv.append(gbv_convert(526))
    gbv.append(gbv_convert(529))
    gbv.append(gbv_convert(530))
    gbv.append(gbv_convert(537))
    gbv.append(gbv_convert(538))
    gbv.append(gbv_convert(539))
    gbv.append(gbv_convert(706))
    gbv.append(gbv_convert(714))
    gbv.append(gbv_convert(718))
    gbv.append(gbv_convert(719))
    gbv.append(gbv_convert(720))
    gbv.append(gbv_convert(721))
    gbv.append(gbv_convert(722))
    gbv.append(gbv_convert(723))
    gbv.append(gbv_convert(724))
    gbv.append(gbv_convert(725))
    gbv.append(gbv_convert(726))
    gbv.append(gbv_convert(727))
    gbv.append(gbv_convert(728))
    gbv.append(gbv_convert(729))
    gbv.append(gbv_convert(730))
    gbv.append(gbv_convert(731))
    gbv.append(gbv_convert(732))
    gbv.append(gbv_convert(733))
    gbv.append(gbv_convert(734))
    gbv.append(gbv_convert(735))
    gbv.append(gbv_convert(736))
    gbv.append(gbv_convert(737))
    gbv.append(gbv_convert(738))
    gbv.append(gbv_convert(739))
    gbv.append(gbv_convert(740))
    gbv.append(gbv_convert(741))
    gbv.append(gbv_convert(742))
    gbv.append(gbv_convert(743))
    gbv.append(gbv_convert(744))
    gbv.append(gbv_convert(745))
    gbv.append(gbv_convert(746))
    gbv.append(gbv_convert(747))
    gbv.append(gbv_convert(748))
    gbv.append(gbv_convert(749))
    gbv.append(gbv_convert(750))
    gbv.append(gbv_convert(751))
    gbv.append(gbv_convert(752))
    gbv.append(gbv_convert(753))
    gbv.append(gbv_convert(754))
    gbv.append(gbv_convert(756))
    gbv.append(gbv_convert(757))
    gbv.append(gbv_convert(969))
    gbv.append(gbv_convert(975))
    gbv.append(gbv_convert(976))
    gbv.append(gbv_convert(978))
    gbv.append(gbv_convert(979))
    gbv.append(gbv_convert(980))
    gbv.append(gbv_convert(981))
    gbv.append(gbv_convert(982))
    gbv.append(gbv_convert(983))
    gbv.append(gbv_convert(984))
    gbv.append(gbv_convert(985))
    gbv.append(gbv_convert(994))
    gbv.append(gbv_convert(995))
    gbv.append(gbv_convert(996))
    gbv.append(gbv_convert(997))
    gbv.append(gbv_convert(999))
    gbv.append(gbv_convert(1000))
    gbv.append(gbv_convert(7034))
    #print(gbv)
    return median(gbv)

#Скрипт слежки за ценой - покажет у кого сейчас можно купить предмет и стоит ли покупать по этой цене
def sentry(item_id, **kwargs):
    #собираем всех торговцев, которые сейчас продают указанный предмет
    market_list = find_market_id(vend_db, item_id, **kwargs)
    #Если кого-то поймали, то ищем самую низкую цену
    if len(market_list) > 0:
        saved_price = 2000000000
        saved_location = ''
        #поиск магазина с самой низкой ценой
        for shop in market_list:
            if shop['price'] < saved_price:
                saved_price = shop['price']
                saved_owner = shop['owner']
                saved_location = shop['location']
        #тут у нас в saved_price хранится текущая цена не венде
        #сравним ее с известными данными по продажам
        maverage_price = market_average(item_id, **kwargs)
        _kw_worker = kwargs
        _kw_worker['item_id'] = item_id
        _item_name = shop_item_name(_kw_worker)
        #если средняя рыночная выше продаваемой сейчас, то хорошо
        if maverage_price != False:
            if maverage_price > saved_price:
                #getting coeff
                _difference = maverage_price / saved_price
                _difference = round(100 - (100 / _difference))
                return [saved_owner, _item_name, saved_location, saved_price, maverage_price, '-' + str(_difference) + '%']
            #если средняя рыночная ниже продаваемой, то плохо
            if maverage_price < saved_price:
                #getting coeff
                _difference = maverage_price/ saved_price
                _difference = round((100 / _difference) - 100)
                return [saved_owner, _item_name, saved_location, saved_price, maverage_price, '+' + str(_difference) + '%']
            #цена такая-же, что в общем то и норм
            else:
                return [saved_owner, _item_name, saved_location, saved_price, maverage_price, '0%']
        else:
            #цены на такой предмет в деманде нет, но его продают сейчас
            return [saved_owner, _item_name, saved_location, saved_price, maverage_price, '!!']
    return None

def sentry_list():
    #составляет список торговцев по существующему сентри листу
    def non(slist, sentry):
        if sentry != None:
            slist.append(sentry)
    #собрать все хотелки в один лист и распечатать, отсортировав по цене продажи сейчас (вначале дешевые)
    saved_slist = sentry_load()
    
    result_slist = []
    for s in saved_slist:
        found_s = item_db_search(item_db, s['item_id'])
        if found_s['type'] == 'IT_ARMOR' or found_s['type'] == 'IT_WEAPON':
            #если это шмотка, то надо основательно пройтись и проверить
            #каждый комплексный вариант заточки + раздельно шмотку с заточкой + раздельно карты
            #отдельно предмет
            for r in range(11):
                if r != 0:
                    non(result_slist, sentry(s['item_id'], refine=r))
                else:
                    non(result_slist, sentry(s['item_id']))
            
            #проверяем, надо ли искать карты
            if 'cards' in s and 'cards' != []:
                #отдельно карты
                for c in s['cards']:
                    non(result_slist, sentry(c))
                
                #вместе предмет и карты
                for r in range(11):
                    if r != 0:
                        non(result_slist, sentry(s['item_id'], cards=s['cards'], refine=r))
                    else:
                        non(result_slist, sentry(s['item_id'], cards=s['cards']))
        else:
            #если это лут
            non(result_slist, sentry(s['item_id']))
    return result_slist

def sentry_add(_sentry_list, item_dict):
    #проверить, что такого айдишника еще нет в списке
    #если вкинута карта, проверить, не тречится ли она уже в связке со шмоткой
    #если тречится, то не добавлять
    _buffer = True
    #идем по каждому предмету в сентре
    counter = 0
    for s in _sentry_list:
        #если находим соответствие айдишников
        if s['item_id'] == item_dict['item_id']:
            #проверяем, полностью ли предмет соответствует его параметрам
            if s == item_dict:
                #если это тот же предмет, то не добавляем его
                _buffer = False
                break
            else:
                #если это тот же предмет, но с другими параметрами
                #то заменяем предмет в списке на новый
                _sentry_list[counter] = item_dict
                _buffer = False
                break
        #если в искомом предмете есть параметр карт
        #нужно пройтись по всем картам и проверить, не тот же ли это айдишник
        if 'cards' in s:
            for c in s['cards']:
                if c == item_dict['item_id']:
                    _buffer = False
                    break
        counter += 1
    
    if _buffer:
        _sentry_list.append(item_dict)
        return True
    else:
        print('item not added to a shopping list: already in a list')
        return False
    return None
    

def sentry_delete(_sentry_list, item_id):
    for i in range(len(_sentry_list)):
        if _sentry_list[i]['item_id'] == item_id:
            del _sentry_list[i]
            sentry_save(_sentry_list)
            return

def sentry_save(sentry_list):
    filepath = '{}{}.txt'.format(db_folder_path, 'sentry_list')
    with open (filepath, 'w') as sentry_file:
        json.dump(sentry_list, sentry_file)

def sentry_load():
    filepath = '{}{}.txt'.format(db_folder_path, 'sentry_list')
    if os.stat(filepath).st_size != 0:
        with open (filepath.format(db_folder_path), 'r') as sentry_file:
            return json.load(sentry_file)
    else:
        return []

def refine_calculator(item_id, refinement, weapon_level=0):
    _0_item_price = market_average(item_id)
    
    if item_db_search(item_db, item_id)['type'] == 'IT_ARMOR':
        success_table = [60, 24, 9.6, 1.92, 0.384, 0.03456]
        if refinement <= 4:
            attemps = refinement
        if refinement == 5:
            attemps = round(100 / success_table[0])
        if refinement == 6:
            attemps = round(100 / success_table[1])
        if refinement == 7:
            attemps = round(100 / success_table[2])
        if refinement == 8:
            attemps = round(100 / success_table[3])
        if refinement == 9:
            attemps = round(100 / success_table[4])
        if refinement == 10:
            attemps = round(100 / success_table[5])
        npc_comission= 2000
        ref_item = market_average(985)
    
    if item_db_search(item_db, item_id)['type'] == 'IT_WEAPON':
        if weapon_level == 0:
            print('weapon level missing')
            return
        if weapon_level == 1:
            success_table = [100, 100, 100, 60, 24, 4.56]
        if weapon_level == 2:
            success_table = [100, 100, 60, 24, 4.8, 0.912]
        if weapon_level == 3:
            success_table = [100, 60, 30, 6, 1.2, 0.228]
        if weapon_level == 4:
            success_table = [60, 24, 9.6, 1.92, 0.384, 0.03456]
        if refinement <= 4:
            attemps = refinement
        if refinement == 5:
            attemps = round(100 / success_table[0])
        if refinement == 6:
            attemps = round(100 / success_table[1])
        if refinement == 7:
            attemps = round(100 / success_table[2])
        if refinement == 8:
            attemps = round(100 / success_table[3])
        if refinement == 9:
            attemps = round(100 / success_table[4])
        if refinement == 10:
            attemps = round(100 / success_table[5])
        npc_comission = 5000
        ref_item = market_average(984)
    
    h1 = _0_item_price * attemps
    h2 = npc_comission * attemps
    h3 = ref_item * (attemps * refinement)
    print(_0_item_price)
    print(attemps)
    print(ref_item)
    return round(h1 + h2 + h3)