#imported libraries
from tabulate import tabulate
from statistics import median
import math
import random
from operator import itemgetter
import json
import os

#my functions
from item_db_functions import item_name, item_db_search, item_db_merch
import db_refresh as db
demand_db = db.demand_db
vend_db = db.vend_db
buy_db = db.buy_db
item_db = db.item_db
monster_db = db.monster_db
now = db.now
db_time = db.db_time
db_folder_path = db.db_folder_path

def shop_item_name(shop_item):
    """Convert shop item to beautiful name
    """
    _item_name = ''
    if 'star_crumbs' in shop_item and shop_item['star_crumbs'] != 0:
        _item_name += ' ' + ('V'*shop_item['star_crumbs']) + 'S'
    
    if 'element' in shop_item and shop_item['element'] != None:
        _item_name += ' ' + (shop_item['element'])
    
    if 'refine' in shop_item and shop_item['refine'] != 0:
        _item_name += (' +' + str(shop_item['refine']))
    
    _item_name += ' ' + item_name(item_db, shop_item['item_id'])
    
    if 'cards' in shop_item and shop_item['cards'] != []:
        _item_name += ' ['
        for c in shop_item['cards']:
            _item_name += item_name(item_db, c) + ', '
        _item_name = _item_name[:-2]
        _item_name += ']'
    
    if 'star_crumbs' in shop_item and shop_item['star_crumbs'] != 0:
        if item_db_search(item_db, shop_item['item_id'])['slots'] > 0:
            _item_name = _item_name[:-4]
    
    return _item_name

#поиск предмета по конкретным параметрам, например, именно пустой композит +10
#указывать в месте с списком предметов (например деманд)
def ex_item_searcher(_id, items_array, **kwargs):
    _checks = {}
    _unchecks = []
    
    def c_uc_fill(keyword):
        if keyword in kwargs:
            _checks[keyword] = kwargs[keyword]
        else:
            _unchecks.append(keyword)
			
    c_uc_fill('refine')
    c_uc_fill('cards')
    c_uc_fill('star_crumbs')
    c_uc_fill('element')
    
    found_items = []
    for item in items_array:
        if item['item_id'] == _id:
            #если у нас в проверках что-то есть
            if len(_checks) > 0:
                #check if needed keys are in item
                _ck = False
                for c in _checks:
                    _ck = False
                    if c in item:
                        #print(c)
                        #print(item)
                        if item[c] == _checks[c]:
                            #print('item[c]: {}'.format(item[c]))
                            _ck = True
                    if _ck == False:
                        break
                _uck = False
                if _ck:
                    #check if not needed keys are not in item
                    for u in _unchecks:
                        _uck = False
                        if u not in item:
                            _uck = True
                        else:
                            _uck = False
                            #at least one element is not correct, no need to check further
                            break
                #print('_ck: {}'.format(_ck))
                #print('_uck: {}'.format(_uck))
                if _ck and _uck:
                    found_items.append(item)
            else:
                #если в проверках ничего нет
                if ('refine' not in item) and ('cards' not in item) and ('star_crumbs' not in item) and ('element' not in item):
                    found_items.append(item)
    if found_items != []:
        return found_items
    #not found
    return False

def find_market_id(db_list, item_id, **kwargs):
    #возвращает всех торговцев, которые сейчас продают/скупают указанный item_id
    _list_to_store = []
    #if there is no additional parameters at all
    for itemshop in db_list:
        _pol = ex_item_searcher(item_id, itemshop['items'], **kwargs)
        if _pol != False:
            #собираем строку
            for j in _pol:
                _tyi = dict(j)
                _tyi['owner'] = itemshop['owner']
                _tyi['creation_date'] = itemshop['creation_date']
                _tyi['location'] = itemshop['location']
                _list_to_store.append(_tyi)
    return _list_to_store

def indenter(for_iter):
    _indent = 1
    if 'refine' in for_iter:
        _indent += 1
    if 'cards' in for_iter:
        _indent += 1
    if 'star_crumbs' in for_iter:
        _indent += 1
    if 'element' in for_iter:
        _indent += 1
    if 'beloved' in for_iter:
        _indent += 1
    return _indent

#Топ самых продаваемых предметов (уже проданных) по количеству
def top_popular(top_ten = False, tab_return = True):
    _top_popular = []
    #Идем по списку проданного
    for popular in demand_db:
        _indent = indenter(popular)
        #_top_popular.append({'item_id': popular['item_id'], 
        #                         'amount': sum(list(popular.values())[_indent:])})
        if tab_return:
            _top_popular.append([shop_item_name(popular), sum(list(popular.values())[_indent:])])
        else:
            _collector = {}
            _collector['item_id'] = popular['item_id']
            _collector['score'] = sum(list(popular.values())[_indent:])
            _collector['progression'] = '~'
            kwargs_constructor(popular, _collector, 'refine')
            kwargs_constructor(popular, _collector, 'cards')
            kwargs_constructor(popular, _collector, 'star_crumbs')
            kwargs_constructor(popular, _collector, 'element')
            _top_popular.append(_collector)

    if tab_return:
        _top_popular = sorted(_top_popular, key=lambda x: x[-1], reverse = True)
    else:
        _top_popular = sorted(_top_popular, key=itemgetter('score'), reverse = True)
    #beauty number
    #for alo in _top_popular:
    #    alo['score'] = f"{alo['score']:,}"
    #making top 50
    if top_ten != False:
        _top_popular = _top_popular[:top_ten]
    #numeration
    _ct = 0
    for n in _top_popular:
        _ct += 1
        n['place'] = _ct
        #_top_popular[n] = [n+1] + _top_popular[n]
    #_top_popular = sorted(_top_popular, key=itemgetter('amount'), reverse=True)
    if tab_return:
        return tabulate(_top_popular, headers = ['', 'Item', 'Amount'], tablefmt='orgtbl')
    else:
        return _top_popular

#Топ предметов, на которых больше всего заработали
def top_valuable(top_ten = False, tab_return = True):
    #взять каждый предмет деманда, перемножить позиции, эти позиции суммировать и сохранить
    _top_value = []
    #Идем по списку проданного
    for val in demand_db:
        _indent = indenter(val)
        #_top_value.append({'item_id': val['item_id'],
        #                   'value': sum(k*v for k,v in list(val.items())[1:])
        #                    })
        b = sum(k*v for k,v in list(val.items())[_indent:])
        #_top_value.append([item_name(val['item_id']), b])
        if tab_return:
            _top_value.append([shop_item_name(val), b])
        else:
            _kwargs = {}
            kwargs_constructor(val, _kwargs, 'refine')
            kwargs_constructor(val, _kwargs, 'cards')
            kwargs_constructor(val, _kwargs, 'star_crumb')
            kwargs_constructor(val, _kwargs, 'element')
            _top_value.append({'item_id': val['item_id'], **_kwargs, 'score': b, 'progression': '='})
        
    if tab_return:
        _top_value = sorted(_top_value, key=lambda x: x[1], reverse=True)
    else:
        _top_value = sorted(_top_value, key=itemgetter('score'), reverse=True)
    #making top 50
    if top_ten != False:
        _top_value = _top_value[:top_ten]
    #numeration
    _num = 0
    for n in _top_value:
        if tab_return:
            _top_value[n] = [n+1] + _top_value[n]
        else:
            _num += 1
            n['place'] = _num
    
    if tab_return:
        return tabulate(_top_value, headers = ['', 'Item', 'Amount'], tablefmt='orgtbl')
    else:
        return _top_value

#вычисляем медиану по МЕСТУ В ТОПЕ предмета, это и будут очки предмета
#листы нужно создать заранее, иначе получится пиздец по времени обработки
def vend_score(item_id, **kwargs):
    _p = ex_item_searcher(item_id, top_pop, **kwargs)
    if _p != False:
        _p = _p[0]['place']
    else:
        _p= 9999
        
    _v = ex_item_searcher(item_id, top_val, **kwargs)
    if _v != False:
        _v = _v[0]['place']
    else:
        _v = 9999
    
    #если конкретно такого предмета не нашли на трейде
    #то попробовать составить медиану из составных частей предмета
    if _p == 9999 and _v == 9999:
        for p in top_pop:
            if item_id == p['item_id']:
                _p = p['place']
        for v in top_val:
            if item_id == v['item_id']:
                _v = v['place']
    return median([_p, _v])


def top_scoreble(top_ten=False, tab_return=True):
    #целый топ предметов отсортированный по очкам продажи
    _top_score = []
    for score in demand_db:
        _kwarg = {}
        kwargs_constructor(score, _kwarg, 'refine')
        kwargs_constructor(score, _kwarg, 'cards')
        kwargs_constructor(score, _kwarg, 'star_crumbs')
        kwargs_constructor(score, _kwarg, 'element')
        _ovrl = {'item_id': score['item_id'], 
                 **_kwarg, 
                 'score': vend_score(score['item_id'], **_kwarg), 
                 'progression': '='}                                                      
        _top_score.append(_ovrl)
    #_top_score = sorted(_top_score, key=lambda x: x[1])
    _top_score = sorted(_top_score, key=itemgetter('score'))
    #making top 50
    if top_ten != False:
        _top_score = _top_score[:top_ten]
    #numeration
    _pl = 0
    for n in _top_score:
        _pl += 1
        n['place'] = _pl
    if tab_return:
        return tabulate(_top_score, headers = ['Item', 'Score'], tablefmt='orgtbl')
    else:
        return _top_score

def top_score_place(item_id):
    for a in top_score:
        if a['item_id'] == item_id:
            return a['place']
    #если ниче не находим, вернуть тупую цифру
    return 9999
        
#найти среднюю цену предмета только по деманду
def market_average(_id, **kwargs):
    #сделать отличие, когда брать медиану, а когда комбинацию, которая заработала больше бобла
    
    #cards converter
    if 'cards' in kwargs:
        if not isinstance(kwargs['cards'], list):
            kwargs['cards'] = [kwargs['cards']]
    
    def ident(_it):
        if (type(_it) is not str) and (_it is not False):
            #create list, that will hold all valies to count median
            c = []
            #iterate through available elements
            for jh in _it:
                #make an indent, so we can actually count every sale
                _indent = indenter(jh)
                #for every price
                for ol in list(jh)[_indent:]:
                    #add this price as much as it was sold
                    for jko in range(jh[ol]):
                        c += [ol]
            return round(median(c))
        else:
            return _it
    
    return ident(ex_item_searcher(_id, demand_db, **kwargs))

#найти цену, по которой стоит сейчас выставить предмет на продажу
def find_market_price(item_id, amount=1, **kwargs):
    #создаем переменную, которую будем использовать для итогового значения
    if item_id in banlist:
        return 'NPC'
    #лучшая комбинация цены на продажу
    _demand_result = 0
    #средняя цена по рынку
    _market_result = 0
    #по текущей ситуации на рынке
    _trade_result = 0
    
    #цена продажи нпц
    _npc_result = 0
    #цена скупщика
    _buy_result = 0
    
    #Итоговый результат вычислений
    _overall_result = 0
    
    #====================================Достаем инфу текущего предложения
    
    #создаем таблицу из предметов, которые сейчас в продаже
    #формат owner: location: amount: item_id: price: opened:
    _item = find_market_id(vend_db, item_id, **kwargs)
    #наполняем таблицу по заданному айдишнику, записывая
    #количество, цену, время
    #==============================================================Функции
    #оценка временем
    #поиск самого старого лота
    def latest_trade(trade_array):
        _latest = now
        _id_old = 0
        for old_shop in range(len(trade_array)):
            if _latest >= trade_array[old_shop]['creation_date']:
                _latest = trade_array[old_shop]['creation_date']
                _id_old = old_shop
        return _id_old
    #поиск самого нового лота
    #def newest_trade(trade_array):
    #    _newest = now
    #    _id_new = 0
    #    for new_shop in range(len(trade_array)):
    #        if _newest < trade_array[new_shop]['opened']:
    #            _newest = trade_array[new_shop]['opened']
    #            _id_new = new_shop
    #    return _id_new
    #поиск самого дорогого лота
    def highest_trade_price(trade_array):
        _highest = 0
        _id_high = 0
        for high_shop in range(len(trade_array)):
            if _highest < trade_array[high_shop]['price']:
                _highest = trade_array[high_shop]['price']
                _id_high = high_shop
        return _id_high
    #поиск самого дешевого лота
    
    def least_trade_price(trade_array):
        _least = 0
        _id_low = 0
        for least_shop in range(len(trade_array)):
            if _least == 0:
                _least = trade_array[least_shop]['price']
            elif _least > trade_array[least_shop]['price']:
                _least = trade_array[least_shop]['price']
                _id_low = least_shop
        return _id_low
    #=====================================================================
    
    #================================================Средняя цена по рынку
    _market_result = market_average(item_id, **kwargs)
    #=====================================================================
    
    #нужно запомнить, сколько предложений есть ниже рыночной цены
    #это понадобится в конечном подсчете
    upr_counter = 0
    if len(_item) > 0:
        for upriced in _item:
            if upriced['price'] < _market_result:
                upr_counter += 1
    
    
    #теперь нужно список магазинов почистить от говна (хз пока зачем, но хочется)
    
    #==============================================Чистим магазин он говна
    #проверяем, что на рынке вообще больше одного лота
    if len(_item) > 1:
        #сравниваем старейшее предложение со следующим по времени,
        #и проверяем, не повышена ли цена у более свежего
        #если цена повышена, то это говно, которое не следует учитывать
            
        #найти старейшее, найти второе по старости, сравнить и принять решение
        _al = len(_item)
        _ltp = latest_trade(_item)
        #запускаем луп, который задумывается пройтись по всем предметам в предложении сейчас
        for i in reversed(range(_al)):
            #в процессе проходки наш лист может уменьшиться, поэтому необходимо проверить длину листа
            if (len(_item) > 1):
                #print('comparing {}'.format(_item[_ltp]))
                #print('with {}'.format(_item[_ltp - 1]))
                if _item[_ltp]["price"] < _item[_ltp - 1]['price']:
                    #print('deleting {}'.format(_item[_ltp - 1]))
                    _item.pop(_ltp - 1)
                    _al -= 1
                    #prevent _ltp of becoming 0
                    if _ltp > 1:
                        _ltp -= 1
                else:
                    #prevent _ltp of becoming 0
                    if _ltp > 1:
                        _ltp -= 1
                    else:
                        #_ltp reached it's limit, so we have no point looking further
                        break
            else:
                break
    #=====================================================================
    
    #на этом моменте у нас очищенный оn сверхговна итемлист (или пустой)
    
    #===========================================================Вычисления
    #==============================================Дешевейшая цена продажи
    #если оказалось, что лот всего один - только ему и составляем конкуренцию
    #необходима проверка с прошлыми базами
    #возможно что товар разобрали и цену можно сильно повышать
    if len(_item) == 1:
        _latest = _item[latest_trade(_item)]
        #если давность лота больше 24 часов
        #понижаем цену, по 10% за каждые 12 часов
        if db.convert_time(_latest["creation_date"], 'h') > 24:
            #сбрасыватель цены, по 10% за каждые 12 часов простоя
            _buffer = 0.1  * math.floor(math.log(db.convert_time(_latest["creation_date"], 'h'))/math.log(12))
            #применение сбрасывания цены
            _trade_result = round(_latest["price"] - (_latest["price"] * _buffer))
            
            #проверяем, если средняя цена по рынку ниже, чем цена конкурента
            #значит конкурент сильно завысил цену, да и по ней никто не берет, просто ставим среднюю рыночную
            #цена уже давно висит, поэтому такой метод тут подойдет
            if market_average(item_id, **kwargs) < _trade_result:
                _trade_result = market_average(item_id, **kwargs)
        #если давность лота больше 12 часов
        #рандомим повышение, понижение, или ту же цену
        elif db.convert_time(_latest["creation_date"], 'h') > 12:
            _rand_result = random.randint(0, 2)
            #рандомно повышаем
            if _rand_result == 0:
                _trade_result = round(_latest["price"] +
                                        (_latest["price"] *
                                         random.uniform(0.05, 0.2)))
            #оставляем такой же
            elif _rand_result == 1:
                pass
            #рандомно понижаем
            else:
                _trade_result = round(_latest["price"] -
                                        (_latest["price"] *
                                         random.uniform(0.05, 0.2)))
            
            #если оказывается, что цена ниже рыночной, то поднять ее до рыночной
            if market_average(item_id, **kwargs) > _trade_result:
                _trade_result = market_average(item_id, **kwargs)
        #если давность лота меньше 12 часов - рандомно повышаем цену
        else:
            _trade_result = round(_latest["price"] +
                                    (_latest["price"] *
                                     random.uniform(0.05, 0.2)))
    
    
    
    if len(_item) > 0:
        #находим самый дешевый лот
        _competitor = _item[least_trade_price(_item)]
        _item_type = item_db_search(item_db, item_id)['type']
        if _item_type != 'IT_ARMOR' and _item_type != 'IT_WEAPON':
            #Если это лут, то следует применить оценку долей рынка
            #оценить размер рынка - посмотреть сколько предметов предложено всего
            #сколько предметов у моего конкурента, сравнить размер рынка, при моем входе
            #если мой размер рыночного предложения в 2.5 раза меньше чем у компететера - сбиваем цену
            #если разница в пределах 2.5-1.5, цену оставляем, при меньшем можно повышать
            
            #считаем 1% от доли рынка
            _overall_amount = 0
            for am in _item:
                _overall_amount += am['amount']
            
            _one_percent = (_overall_amount + amount)/100
            #если у чела >150 предметов в эмаунте, то я не готов с ним компететиться и точно буду ставить цену ниже
            if (_competitor['amount'] / _one_percent) > (amount / _one_percent)*2.5:
                _trade_result = round(_competitor['price'] - (_competitor['price'] * 0.1))
            #если у чела не так много предметов, то надо провести анализ, стоит ли повышать цену
            #нужно проверить на сколько товар продаваемый, если он в топе, то смотреть рыночную цену
            elif (_competitor['amount'] / _one_percent) > (amount / _one_percent)*1.5:
                _trade_result = _competitor['price'] - 1
            else:
                _trade_result = round(_competitor['price'] + (_competitor['price'] * 0.1))
        else:
            #если это бронь или оружие, то сделаем оценку временем
            #если самому конкурент висит больше 1 дня - скидываем цену, иначе просто скидываем 1з
            if db.convert_time(_competitor['creation_date'], 'h') > 24:
                _trade_result = round(_competitor['price'] - (_competitor['price'] * 0.1))
            else:
                _trade_result = _competitor['price'] - 1
    #=====================================================================
    
    #========================================================Цена скупщика
    #находим самую дорогую цену, по которой есть скупщик
    _buy_market = find_market_id(buy_db, item_id)
    if len(_buy_market) > 0:
        _buy_check = _buy_market[highest_trade_price(_buy_market)]
        _buy_result = _buy_check['price']
    else:
        _buy_result = 0
    #=====================================================================
    
    #=============================================================Цена НПЦ
    _npc_result = item_db_merch(item_db, item_id)
    #=====================================================================
    

    #================================================Достаем рыночную инфу
    #тут мы найдем лучшую комбинацию цены из уже проданных 
    #(та, которая принесла больше всего бобла)
    #Проверяем, есть ли у нас такой предмет в уже проданных
    demand_market = ex_item_searcher(item_id, demand_db, **kwargs)
    if demand_market != False:
        demand_market = demand_market[0]
        #========================находим _demand_result
        #нам нужна лучшая продаваемая комбинация
        newlist = []
        for k in demand_market.items():
            if type(k[0]) != str:
                newlist.append([k[0], k[1]])
        if len(newlist) > 1:
            _value = 0
            for jo in newlist:
                #маленькая проверка на достоверость цены
                #если зарегестрирована всего 1 продажа по такой цене, то ниче не будем с этим делать
                if jo[1] > 1:
                    _earned = jo[0] * jo[1]
                    if _earned > _value:
                        _value = _earned
                        _demand_result = jo[0]
    #=====================================================================
    #если на трейде такого предмета нет вообще
    if len(_item) == 0:
        if demand_market != False:
            #и у нас уже есть цена предмета
            if len(demand_market) > 0:
                #найти самую дорогую цену и вернуть
                _trade_result = 0
                for hp in demand_market.items():
                    #если это не срань типо cards или refine
                    if type(hp[0]) != str:
                        #если цена выше предыдущей
                        if hp[0] > _trade_result:
                            _trade_result = hp[0]
    #====================================Выводим итоговую цену выставления
    _overall_counter = []
    for oc in range(upr_counter+1):
        _overall_counter.append(_trade_result)
    _overall_counter.append(_demand_result)
    _overall_counter.append(_market_result)
    _overall_result = median(_overall_counter)
    #=====================================================================
    
    #====================================================Принимаем решение
    #коррекция цены в зависимости от вероятности ее продажи, чем вероятность меньше, тем меньше и цена
    price_corr = _overall_result * price_correction_rate(item_id)
    #коррекция цены, в зависимости от составных частей предмета
    _pbp = price_by_parts(item_id, **kwargs)
    #если цена составных частей дешевле, чем получается на выставление
    if _pbp != False:
        if _overall_result > _pbp:
            #то заменяем цену выставления ценой частей + сбрасываем немного, чтобы было выгоднее взять у меня
            _overall_result = _pbp * 0.85
        elif _overall_result < _pbp:
            _overall_result = _pbp
    debug = True
    if debug:
        print('Vending now: trade: {}'.format(_trade_result))
        print('Best demand price: demand: {}'.format(_demand_result))
        print('Average demand: market: {}'.format(_market_result))
        
        print('overall: {}'.format(_overall_result))
        
        print('buy: {}'.format(_buy_result))
        print('npc: {}'.format(_npc_result))
        print('by parts: {}'.format(_pbp))
    
    #Если инфы не набралось, то скидываем нпц
    if _overall_result == 0:
        return "NPC"
    
    #Проверяем, есть ли смысл выставлять на венд
    #Сравниваем со скупщиком
    #Если наша цена - 12.5 оказывается меньше, чем цена скупщика
    if price_corr - (price_corr*0.125) < _buy_result:
        #То смысла ждать венда особо не вижу - проще просто продать ем сразу
        #Но еще проверим, может еще проще будет ваще НПЦ продать
        if _npc_result < _buy_result:
            return [_buy_check['owner'], item_id, _buy_check['location'] ,_buy_result]
        else:
            return 'NPC'
    else:
        if _npc_result > _overall_result:
            return 'NPC'
        else:
            return round(_overall_result) - 1
market_prices_buff = {}
npc_prices_buff = {}
def monster_vend_price(monster_id, market=True, printer=False):
    if market:
        buffer_prices = market_prices_buff
    else:
        buffer_prices = npc_prices_buff
    #идем по каждому монстру
    for a in monster_db:
        #если находим совпадение
        if a['monster_id'] == monster_id:
            _monster_value = 0
            _printer = {}
            #идем по каждому предмету в дропе
            for b in a['drops'].items():
                _item_name = b[0]
                _item_chance = b[1]
                if _item_name not in buffer_prices:
                    _item_id = item_db_search(item_db, _item_name)
                    if _item_id is not None:
                        _item_id = _item_id['item_id']
                    else:
                        break
                    #полученный процент / 100 а результат умножаем на 10к
                    #получается результат, сколько бы мы в среднем получили такого предмета убив 10к мобов
                    _item_amount = int((_item_chance/100)*10000)
                    if market:
                        _solo_price = find_market_price(_item_id)
    
                        #NPC
                        if _solo_price == 'NPC':
                            _profit = item_db_merch(item_db, _item_id) * _item_amount
                        #BUYER
                        if isinstance(_solo_price, list):
                            _profit = _solo_price[-1] * _item_amount
                        #VEND
                        if isinstance(_solo_price, int):
                            _profit = _solo_price * _item_amount
    
                        _printer[_item_name] = _profit
                        _monster_value += _profit
                        buffer_prices[_item_name] = _profit
                    else:
                        _solo_price = item_db_merch(item_db, _item_id)
                        _profit = _solo_price * _item_amount
                        _printer[_item_name] = _profit
                        _monster_value += _profit
                        buffer_prices[_item_name] = _profit
                else:
                    _printer[_item_name] = buffer_prices[_item_name]
                    _monster_value += buffer_prices[_item_name]
            if printer:
                for b in _printer:
                    _printer[b] = _printer[b]/10000
                    print('{}: {}'.format(b, _printer[b]))
                print('Result: {}'.format(_monster_value / 10000))
            return int(math.floor(_monster_value / 10000))

def top_monster_price(market=True, top_ten=False, tab=False, mvp=False):
    top_monster = []
    #пройти по базе монстров
    #оценить каждого монстра и занести в лист
    #отсортировать лист
    for a in monster_db:
        if market:
            top_monster.append({'monster_id': a['monster_id'], 
                                        'name': a['monster_name'],
                                        'price': monster_vend_price(a['monster_id'])})
        else:
            top_monster.append({'monster_id': a['monster_id'], 
                                        'name': a['monster_name'],
                                        'price': monster_vend_price(a['monster_id'], market=False)})
    #top_monster = sorted(top_monster, key=lambda x: x[2], reverse = True)
    top_monster = sorted(top_monster, key=itemgetter('price'), reverse = True)

    if top_ten:
        top_monster = top_monster[:top_ten]
    
    #beauty number
    #for alo in top_monster:
    #    alo[-1] = f"{alo[-1]:,}"

    #numeration
    _num = 0
    for n in top_monster:
        _num += 1
        n['place'] = _num
    
    if tab:
        return tabulate(top_monster, headers=['', 'ID', 'Name', 'Profit'], tablefmt='orgtbl')
    else:
        return top_monster
    

def price_correction_rate(item_id):
    ln = len(top_score)
    tscore = top_score_place(item_id)      
    #режем цену в зависимости от популярности предмета
    if tscore < ln/10:
        return 1
    if tscore < ln/9:
        return 0.9
    if tscore < ln/8:
        return 0.8
    if tscore < ln/7:
        return 0.7
    if tscore < ln/6:
        return 0.6
    if tscore < ln/5:
        return 0.5
    if tscore < ln/4:
        return 0.4
    if tscore < ln/3:
        return 0.3
    if tscore < ln/2:
        return 0.2
    if tscore < ln:
        return 0.1
    #если ниче не нашли, то пока хз че с этим делать, не будем применять коррекцию
    return 1

def price_by_parts(item_id, **kwargs):
    #находим цену предмета, если сейчас на рынке купить все состовляющие
    #Проверяем, что предмет составной
    #если нет, то смысла в этой функции нет
    if kwargs == {} or 'cards' not in kwargs:
        return False
    def find_least_price(item_id, **kwargs):
        #ищем самую низкую цену предмета сейчас на рынке
        #собираем лист из нужных предметов
        if 'refine' in kwargs:
            if kwargs['refine'] <= 4:
                least_list = find_market_id(vend_db, item_id)
            else:
                least_list = find_market_id(vend_db, item_id, refine=kwargs['refine'])
        else:
            least_list = find_market_id(vend_db, item_id)
        #находим среди сейча продающих самую дешевую цену
        _least = 0
        for least_shop in least_list:
            if _least == 0:
                _least = least_shop['price']
            if _least > least_shop['price']:
                _least = least_shop['price']
        #если оказалось, что ниче не продается
        if _least == 0:
            
                
            return False
        return _least
    #ищем минимальную цену предмета на рынке сейчас
    #если сейчас этого не продается, берем средние значения
    #предмет и его заточка
    item_price = find_least_price(item_id, **kwargs)
    #если не удалось найти предмет на трейде, то прекращаем считать
    if item_price == False:
        return False
    cards_price = 0
    for i in kwargs['cards']:
        _jfg = find_least_price(i)
        if _jfg != False:
            cards_price += find_least_price(i)
        else:
            #если не удалось найти хоть одну карту на трейде, то прекращаем считать
            return False
    _b = item_price + cards_price
    return _b

def kwargs_constructor(looper, dictn, keyword):
    if keyword in looper:
        dictn[keyword] = looper[keyword]

def top_loader(value):
    print('loading {}...'.format(value))
    #универсальное сохранение базы в файл
    def save_db(compare=False):
        if value == 'pop':
            top = top_popular(False, False)
        if value == 'val':
            top = top_valuable(False, False)
        if value == 'score':
            top = top_scoreble(False, False)
        if value == 'monster_market':
            top = top_monster_price()
        if value == 'monster_npc':
            top = top_monster_price(market=False)
        if compare:
            top = compare_tops(loaded_file['top'], top)
        
        if value != 'monster_npc':
            with open('{}{}.txt'.format(db_folder_path, value), 'w') as top_file:
                #срохраняем файл
                json.dump({'creation_date': str(db_time), 'top': top}, top_file)
        else:
            with open('{}{}.txt'.format(db_folder_path, value), 'w') as top_file:
                #срохраняем файл
                json.dump(top, top_file)
        return top
    def compare_tops(old_top, new_top):
        #идем по новому топу, потому что могут появиться новые предметы в топе
        for i in new_top:
            #если это база предметов
            if 'item_id' in i:
                _kwargs = {}
                kwargs_constructor(i, _kwargs, 'refine')
                kwargs_constructor(i, _kwargs, 'cards')
                kwargs_constructor(i, _kwargs, 'star_crumb')
                kwargs_constructor(i, _kwargs, 'element')
                
                #ищем соответствие в старом топе
                found_item = ex_item_searcher(i['item_id'], old_top, **_kwargs)
                #если нашли
                if found_item != False:
                    found_item = found_item[0]
                    if i['place'] > found_item['place']:
                        _diff = i['place'] - found_item['place']
                        i['progression'] = '-{}'.format(_diff)
                    
                    if i['place'] < found_item['place']:
                        _diff = found_item['place'] - i['place']
                        i['progression'] = '+{}'.format(_diff)
                    
                    if i['place'] == found_item['place']:
                        i['progression'] = '='
            #если это база монстров
            if 'monster_id' in i:
                #ищем соответствие в старой базе
                for b in old_top:
                    if b['monster_id'] == i['monster_id']:
                        if i['place'] > b['place']:
                            _diff = i['place'] - b['place']
                            i['progression'] = '-{}'.format(_diff)
                        if i['place'] < b['place']:
                            _diff = b['place'] - i['place']
                            i['progression'] = '+{}'.format(_diff)
                        if i['place'] == b['place']:
                            i['progression'] = '='
                        break
        return new_top
    #ставим удобный путь
    filepath = '{}{}.txt'.format(db_folder_path, value)
    #проверям, что файл не пустой
    if os.stat(filepath).st_size == 0:
        return save_db()
    
    #открываем существующий файл
    with open(filepath, 'r') as top_file:
        if value != 'monster_npc':
            #запоминаем дату
            loaded_file = json.load(top_file)
            if 'creation_date' in loaded_file:
                top_creation_date = loaded_file['creation_date']
            else:
                #если даты нет, то просто сохранить в нужном формате
                return save_db()
        else:
            #if monster_npc
            return json.load(top_file)
    #если дата не соответствует новой бд
    if top_creation_date != str(db_time):
        #нужно сделать сравнение баз и зафиксировать изменения +-=
        print('calculating tops progress...')
        return save_db(True)
    else:
        #просто читаем инфу из файла
        with open(filepath, 'r') as top_file:
            return json.load(top_file)['top']

def extract_top(top, value, deep=False):
    #values
    #IT_HEALING: Healing items
    #IT_USABLE: Other usable items
    #IT_ETC: Misc items
    #IT_WEAPON: Weapons
    #IT_ARMOR: Armors
    #IT_CARD: Cards
    #IT_AMMO: Ammunitions
    
    #deep values
    #W_DAGGER: Daggers
    #W_1HSWORD: 1-hand swords
    #W_2HSWORD: 2-hand swords
    #W_1HSPEAR: 1-hand spears
    #W_2HSPEAR: 2-hand spears
    #W_1HAXE: 1-hand axes
    #W_2HAXE: 2-hand axes
    #W_MACE: 1-hand maces
    #W_2HMACE: 2-hand maces
    #W_STAFF: Staves
    #W_2HSTAFF: 2-hand staves
    #W_BOW: Bows
    #W_KNUCKLE: Knuckles
    #W_MUSICAL: Musical instruments
    #W_WHIP: Whips
    #W_BOOK: Books
    #W_KATAR: Katars
    #W_REVOLVER: Pistols
    #W_RIFLE: Rifles
    #W_GATLING: Gatling guns
    #W_SHOTGUN: Shotguns
    #W_GRENADE: Grenades
    #W_HUUMA: Huuma shuriken
    
    #A_ARROW: Arrows
    #A_DAGGER: Throwing daggers
    #A_BULLET: Bullets
    #A_SHELL: Shells
    #A_GRENADE: Grenades
    #A_SHURIKEN: Shuriken
    #A_KUNAI: Kunai
    #A_CANNONBALL: Cannon balls
    #A_THROWWEAPON: Other throwing weapons
    
    top_list = []
    for i in top:
        idb_item = item_db_search(item_db, i['item_id'])
        if idb_item['type'] == value:
            if deep is not False:
                if idb_item['subtype'] == deep:
                    top_list.append(i)
            else:
                top_list.append(i)
    
    return top_list

def monster_search(monster_id):
    for i in monster_db:
        if i['monster_id'] == monster_id:
            return i

def extract_monster(top_array, **kwargs):
    top_list = []
    if 'race' not in kwargs and 'size' not in kwargs and 'boss' not in kwargs and 'element' not in kwargs:
        top_list = top_array
    else:
        #iterate array
        for i in top_array:
            #try to find that monster in mosnter_db
            polotno = monster_search(i['monster_id'])
            #if found
            if polotno != None:
                #we need to check accordance of ALL keys
                lalik = False
                for key in kwargs:
                    #save from number vars
                    if key != 'flee' and key != 'hit':
                        if isinstance(kwargs[key], list):
                            lalik = False
                            for l in kwargs[key]:
                                if polotno[key] == l:
                                    lalik = True
                        else:
                            lalik = False
                            #print('{} in {}'.format(key, kwargs))
                            if key in polotno:
                                #print('{} in {}'.format(key, polotno))
                                if polotno[key] == kwargs.get(key):
                                    #print('{} = {}'.format(polotno[key], kwargs.get(key)))
                                    lalik = True
                                else:
                                    break
                            else:
                                break
                    
                if lalik:
                    top_list.append(i)
    
    if 'flee' not in kwargs:
        f_top_list = top_array
    else:
        f_top_list = []
        for mf in top_array:
            polotno = monster_search(mf['monster_id'])
            if polotno != None:
                if polotno['flee'] <= kwargs['flee']:
                    f_top_list.append(mf)
    
    if 'hit' not in kwargs:
        h_top_list = top_array
    else:
        h_top_list = []
        for mh in top_array:
            polotno = monster_search(mh['monster_id'])
            if polotno != None:
                if polotno['hit'] <= kwargs['hit']:
                    h_top_list.append(mh)
    
    res_list = []
    for fin in top_array:
        if fin in top_list and fin in f_top_list and fin in h_top_list:
            res_list.append(fin)
    
    return res_list

#banlist
banlist = [519]
for ban in item_db:
    if ban['type'] == 'IT_PETARMOR':
        banlist.append(ban['item_id'])
#print(banlist)


#сохранять и читать названия по уник нейму
top_pop = top_loader('pop')
top_val = top_loader('val')
top_score = top_loader('score')
top_monster_market = top_loader('monster_market')
top_monster_npc = top_loader('monster_npc')


#print(top_monster_npc)

#print(find_market_price(7270) * price_correction_rate(7270))
#print(monster_vend_price(1686, True))
#цена, по которой стоит выставить на продажу
#print(find_market_price(1705, refine = 9))
#все торговцы, которые сейчас продают конкретно такой предмет
#print(find_market_id(vend_db, 1705, refine = 9))
#средняя цена предмета по деманду
#print(market_average(1705, refine = 9))
#медиана места в топе

#print(price_by_parts(2504, refine=4, cards=[4102]))

#print(find_market_price(1520, 1, refine=8, cards=[4005, 4005, 4005]))