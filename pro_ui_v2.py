import db_refresh as db
db_time = db.db_time
item_db = db.item_db
now = db.now
import main_functions as mf
import market_system_functions as msf
from item_db_functions import item_db_search, item_name

from PyQt5 import QtWidgets, QtCore, QtGui
from mainui import Ui_MainWindow  # импорт нашего сгенерированного файла
import sys
import datetime #needed for proper db update
import imp
import json
 
 
class mywindow(QtWidgets.QMainWindow):
    #initial var for market tab
    market_tab_init = False
    #initial var for item tab
    item_tab_init = False
    #initial var for monster tab
    monster_tab_init = False
    #vars for initial sentry tab
    sentry_tab_init_offers = False
    sentry_tab_init_shopping_items = False
    sentry_tab_init_shopping_raw = False
    #indicator that will tell if we need to update sentry offers tab
    sentry_tab_update_needed = False
    #list that will hold all of the '+' buttons of item_db
    item_db_button_map = []
    #buffer that will hold result item and throw it in raw sentry when done
    sentry_buffer = {}
    #checkbox cache, that help activate last combobox
    previous_combobox2 = False
    
    
    def __init__(self):
        super(mywindow, self).__init__()
        self.ui = Ui_MainWindow()
        self.ui.setupUi(self)
        self.setWindowFlags(QtCore.Qt.WindowStaysOnTopHint)
        
        main_tab_widget = self.ui.centralwidget.findChild(QtWidgets.QTabWidget, 'main_tab_widget')
        #when tab is changed, call onChange
        main_tab_widget.currentChanged.connect(self.onChange)
        #MARKET TAB
        #call it immediately, to load data
        self.onChange(main_tab_widget.currentIndex())
        
        #ITEM TAB
        cb1 = self.ui.centralwidget.findChild(QtWidgets.QComboBox, 'comboBox_1')
        cb1.currentTextChanged.connect(self.set_item_tab)
        cb2 = self.ui.centralwidget.findChild(QtWidgets.QComboBox, 'comboBox_2')
        cb2.currentTextChanged.connect(self.set_item_tab)
        cb3 = self.ui.centralwidget.findChild(QtWidgets.QComboBox, 'comboBox_3')
        cb3.currentTextChanged.connect(self.set_item_tab)
        
        #STORAGE TAB
        storage_button = self.ui.centralwidget.findChild(QtWidgets.QPushButton, 'storage_button')
        storage_button.clicked.connect(self.set_storage_tab)
        
        #MONSTER TAB
        #Search button
        monster_button = self.ui.centralwidget.findChild(QtWidgets.QPushButton, 'monster_search_button')
        monster_button.clicked.connect(self.set_monster_tab)
        
        #MONSTER RACE CHECKBOXES
        monster_race_formless = self.ui.centralwidget.findChild(QtWidgets.QCheckBox, 'monster_race_formless')
        monster_race_brute = self.ui.centralwidget.findChild(QtWidgets.QCheckBox, 'monster_race_brute')
        monster_race_insect = self.ui.centralwidget.findChild(QtWidgets.QCheckBox, 'monster_race_insect')
        monster_race_demon = self.ui.centralwidget.findChild(QtWidgets.QCheckBox, 'monster_race_demon')
        monster_race_angel = self.ui.centralwidget.findChild(QtWidgets.QCheckBox, 'monster_race_angel')
        monster_race_undead = self.ui.centralwidget.findChild(QtWidgets.QCheckBox, 'monster_race_undead')
        monster_race_plant = self.ui.centralwidget.findChild(QtWidgets.QCheckBox, 'monster_race_plant')
        monster_race_fish = self.ui.centralwidget.findChild(QtWidgets.QCheckBox, 'monster_race_fish')
        monster_race_demihuman = self.ui.centralwidget.findChild(QtWidgets.QCheckBox, 'monster_race_demihuman')
        monster_race_dragon = self.ui.centralwidget.findChild(QtWidgets.QCheckBox, 'monster_race_dragon')
        monster_race_all = self.ui.centralwidget.findChild(QtWidgets.QCheckBox, 'monster_race_all')

        #MONSTER RACE CHECKBOX CONNECTOR
        monster_race_formless.stateChanged.connect(self.monster_race_checkbox_other)
        monster_race_brute.stateChanged.connect(self.monster_race_checkbox_other)
        monster_race_insect.stateChanged.connect(self.monster_race_checkbox_other)
        monster_race_demon.stateChanged.connect(self.monster_race_checkbox_other)
        monster_race_angel.stateChanged.connect(self.monster_race_checkbox_other)
        monster_race_undead.stateChanged.connect(self.monster_race_checkbox_other)
        monster_race_plant.stateChanged.connect(self.monster_race_checkbox_other)
        monster_race_fish.stateChanged.connect(self.monster_race_checkbox_other)
        monster_race_demihuman.stateChanged.connect(self.monster_race_checkbox_other)
        monster_race_dragon.stateChanged.connect(self.monster_race_checkbox_other)
        monster_race_all.stateChanged.connect(self.monster_race_checkbox_all)
        
        #MONSTER ELEMENT CHECKBOXES
        monster_element_neutral = self.ui.centralwidget.findChild(QtWidgets.QCheckBox, 'monster_element_neutral')
        monster_element_fire = self.ui.centralwidget.findChild(QtWidgets.QCheckBox, 'monster_element_fire')
        monster_element_water = self.ui.centralwidget.findChild(QtWidgets.QCheckBox, 'monster_element_water')
        monster_element_earth = self.ui.centralwidget.findChild(QtWidgets.QCheckBox, 'monster_element_earth')
        monster_element_wind = self.ui.centralwidget.findChild(QtWidgets.QCheckBox, 'monster_element_wind')
        monster_element_holy = self.ui.centralwidget.findChild(QtWidgets.QCheckBox, 'monster_element_holy')
        monster_element_ghost = self.ui.centralwidget.findChild(QtWidgets.QCheckBox, 'monster_element_ghost')
        monster_element_poison = self.ui.centralwidget.findChild(QtWidgets.QCheckBox, 'monster_element_poison')
        monster_element_shadow = self.ui.centralwidget.findChild(QtWidgets.QCheckBox, 'monster_element_shadow')
        monster_element_undead = self.ui.centralwidget.findChild(QtWidgets.QCheckBox, 'monster_element_undead')
        monster_element_all = self.ui.centralwidget.findChild(QtWidgets.QCheckBox, 'monster_element_all')
        
        #MONSTER ELEMENT CHECKBOXES CONNECTOR
        monster_element_neutral.stateChanged.connect(self.monster_element_checkbox_other)
        monster_element_fire.stateChanged.connect(self.monster_element_checkbox_other)
        monster_element_water.stateChanged.connect(self.monster_element_checkbox_other)
        monster_element_earth.stateChanged.connect(self.monster_element_checkbox_other)
        monster_element_wind.stateChanged.connect(self.monster_element_checkbox_other)
        monster_element_holy.stateChanged.connect(self.monster_element_checkbox_other)
        monster_element_ghost.stateChanged.connect(self.monster_element_checkbox_other)
        monster_element_poison.stateChanged.connect(self.monster_element_checkbox_other)
        monster_element_shadow.stateChanged.connect(self.monster_element_checkbox_other)
        monster_element_undead.stateChanged.connect(self.monster_element_checkbox_other)
        monster_element_all.stateChanged.connect(self.monster_element_checkbox_all)
        
        #MONSTER SIZE CHECKBOXES
        monster_size_all = self.ui.centralwidget.findChild(QtWidgets.QCheckBox, 'monster_size_all')
        monster_size_large = self.ui.centralwidget.findChild(QtWidgets.QCheckBox, 'monster_size_large')
        monster_size_medium = self.ui.centralwidget.findChild(QtWidgets.QCheckBox, 'monster_size_medium')
        monster_size_small = self.ui.centralwidget.findChild(QtWidgets.QCheckBox, 'monster_size_small')
        
        #MONSTER SIZE CHECKBOXES CONNECTOR
        monster_size_large.stateChanged.connect(self.monster_size_checkbox_other)
        monster_size_medium.stateChanged.connect(self.monster_size_checkbox_other)
        monster_size_small.stateChanged.connect(self.monster_size_checkbox_other)
        monster_size_all.stateChanged.connect(self.monster_size_checkbox_all)
        
        #SENTRY TAB
        #Main Sentry offers table
        all_items_table = self.ui.centralwidget.findChild(QtWidgets.QTabWidget, 'sentry_tab_inner')
        all_items_table.currentChanged.connect(self.sentry_onChange)
        #raw sentry add button
        sentry_result_add_button = self.ui.centralwidget.findChild(QtWidgets.QPushButton, 'sentry_result_add_button')
        sentry_result_add_button.clicked.connect(self.sentry_add_button)
        
        #autoupdate of data
        def mainloop():
            print('Refreshing!')
            
            self.setWindowTitle("RO LT - Database updating...")
            #reloda modules to show actual info
            imp.reload(db)
            imp.reload(mf)
            imp.reload(msf)
            db_time = db.db_time
            now = db.now
            print(db.convert_time(db_time, 'm'))
            print(db.db_time)
            
            tab_widget = self.ui.centralwidget.findChild(QtWidgets.QTabWidget, 'main_tab_widget')
            tab_widget.setEnabled(False)
            #if tab was loaded - reload it with new data
            if self.market_tab_init:
                print('reloading first tab data...')
                self.set_market_tab()
            if self.item_tab_init and main_tab_widget.currentIndex() == 1:
                print('reloading second tab data...')
                self.set_item_tab()
            self.setWindowTitle("RO Lokosia Tools")
            self.update()
            self.sentry_tab_update_needed = True
            tab_widget.setEnabled(True)
        
        #autoupdate of data
        # make QTimer
        self.qTimer = QtCore.QTimer()
        # set interval to 1 s
        self.qTimer.setInterval((1000 * 60) * 2) # 1000 ms = 1 s
        # connect timeout signal to signal handler
        self.qTimer.timeout.connect(mainloop)
        # start timer
        self.qTimer.start()
    
    def copy_button_creator(self, shortcut, item, row, col, trader):
        #we have to make it as func, because otherwise it would always copy last button item, instead of relevant one
        #create button
        _wname = str(item)
        _pybutton = QtWidgets.QPushButton(_wname)
        #make button text align left
        _pybutton.setStyleSheet("Text-align:left")
        #assign it to table cell
        shortcut.setCellWidget(row, col, _pybutton)
        _pybutton.clicked.connect(lambda: self.click_copy(_wname, trader))
       
    def click_copy(self, item, trader):
        if trader:
            QtWidgets.QApplication.clipboard().setText('@navshop ' + item)
        else:
            if item.startswith(" "):
                QtWidgets.QApplication.clipboard().setText(item[1:])
            else:
                QtWidgets.QApplication.clipboard().setText(item)
    
    def sentry_add_button_creator(self, shortcut, row, col, item_id):
        _pybutton = QtWidgets.QPushButton('+')
        #assign it to table cell
        shortcut.setCellWidget(row, col, _pybutton)
        _pybutton.clicked.connect(lambda: self.sentry_item_adder(_pybutton, item_id))
        #save button in a button map
        self.item_db_button_map.append([item_id, _pybutton])
        
    
    def sentry_item_adder(self, button_shortcut, item_id):
        def add():
            _sentry_raw = mf.sentry_load()
            #if it is misc items, just add them immediately
            _b = mf.sentry_add(_sentry_raw, {'item_id': item_id})
            #check if item was really added
            if _b:
                #save new list to file
                mf.sentry_save(_sentry_raw)
                #reload table, so we can see changes
                self.set_sentry_tab_shopping()
                self.sentry_tab_update_needed = True
                button_shortcut.setEnabled(False)
        if item_id == False:
            #add item to raw wsentry
            add()
            #reset buffer
            self.sentry_buffer = {}
            #shortcut for buffer label
            _sc = self.ui.centralwidget.findChild(QtWidgets.QLabel, 'sentry_result_item')
            #reset label
            _sc.setText('None')
        else:
            res_lable = self.ui.centralwidget.findChild(QtWidgets.QWidget, 'sentry_result_item')
            item = item_db_search(item_db, item_id)
            #Item buffer shortcut
            _sc = self.ui.centralwidget.findChild(QtWidgets.QLabel, 'sentry_result_item')
            #if weapon or armor, we need to make complex check for composite string
            if (item['type'] == 'IT_ARMOR' or item['type'] == 'IT_WEAPON') and ('slots' in item):
                print(item)
                #нужно проверить, соответствует ли название тому, что в лейбле?
                #нужно проверить, является ли это кликом по кнопке Add, чтобы закинуть предмет в лист
                
                #change label to item name
                _sc.setText(item_name(item_db, item['item_id']))
                self.sentry_buffer['item_id'] = item['item_id']
            elif (item['type'] == 'IT_CARD') and (_sc.text() != 'None'):
                if 'cards' in self.sentry_buffer:
                    self.sentry_buffer['cards'].append(item['item_id'])
                    _sc.setText(_sc.text()[:-1] + ', ' + item_name(item_db, item['item_id']) + ']')
                else:
                    self.sentry_buffer['cards'] = [item['item_id']]
                    _sc.setText(_sc.text() + ' [' + item_name(item_db, item['item_id']) + ']')
            else:
                add()
    
    def sentry_delete_button_creator(self, data_array, shortcut, row, col, item_id):
        _pybutton = QtWidgets.QPushButton('-')
        #assign it to table cell
        shortcut.setCellWidget(row, col, _pybutton)
        _pybutton.clicked.connect(lambda: self.sentry_item_deleter(data_array, item_id))
        #check if we need to disable button in item_db table
        for i in self.item_db_button_map:
            if i[0] == item_id:
                i[1].setEnabled(False)
                break
    def sentry_add_button(self):
        _sentry_raw = mf.sentry_load()
        _b = mf.sentry_add(_sentry_raw, self.sentry_buffer)
        #check if item was really added
        if _b:
            #save new list to file
            mf.sentry_save(_sentry_raw)
            #reload table, so we can see changes
            self.set_sentry_tab_shopping()
            #indicate that we will need an update at offers table
            self.sentry_tab_update_needed = True
            #reset buffer
            self.sentry_buffer = {}
            #shortcut for buffer label
            _sc = self.ui.centralwidget.findChild(QtWidgets.QLabel, 'sentry_result_item')
            #reset label
            _sc.setText('None')
        
    def sentry_item_deleter(self, data_array, item_id):
        mf.sentry_delete(data_array, item_id)
        #save new list to file
        mf.sentry_save(data_array)
        
        #find needed button in a button map
        _counter = 0
        for i in item_db:
            if i['item_id'] == item_id:
                break
            else:
                _counter += 1
        #Enable button
        self.item_db_button_map[_counter][1].setEnabled(True)
        
        self.sentry_tab_update_needed = True
        self.set_sentry_tab_shopping()
    
    def set_table(self, table_widget_name, content_array, ben_or_stonks):
        #make shortcut for table
        shortcut = self.ui.centralwidget.findChild(QtWidgets.QTableWidget, table_widget_name)
        #make shortcut for whole widget
        def name_converter(_table_widget_name):
            if _table_widget_name[:3] == 'to_':
                return table_widget_name[:-5] + 'groupbox'
            return table_widget_name[:-5] + 'widget'
        outer_widget_name = name_converter(table_widget_name)
        w_shortcut = self.ui.centralwidget.findChild(QtWidgets.QWidget, outer_widget_name)
        #reset table
        shortcut.clearContents()
        _items_num = len(content_array)
        if _items_num > 0:
            _len = len(content_array[0])
        else:
            w_shortcut.setHidden(True)
            return
        #reveal table just in case it was hidden previously
        w_shortcut.setHidden(False)
        #turn off sorting, so we can fill and sort table after correctly
        shortcut.setSortingEnabled(False)
        
        #setting columns and rows
        shortcut.setColumnCount(_len)
        shortcut.setRowCount(_items_num)
        #name headers
        bos_ = shortcut.horizontalHeader()
        if ben_or_stonks == 'ben':
            _hs = ['S> Owner', 'S> Location', 'B> Owner', 'B> Location', 'Item', 'Num', 'Profit']
            bos_.setSectionResizeMode(0, QtWidgets.QHeaderView.ResizeToContents)
            bos_.setSectionResizeMode(1, QtWidgets.QHeaderView.ResizeToContents)
            bos_.setSectionResizeMode(2, QtWidgets.QHeaderView.ResizeToContents)
            bos_.setSectionResizeMode(3, QtWidgets.QHeaderView.ResizeToContents)
            bos_.setSectionResizeMode(4, QtWidgets.QHeaderView.Stretch)
            bos_.setSectionResizeMode(5, QtWidgets.QHeaderView.ResizeToContents)
            bos_.setSectionResizeMode(6, QtWidgets.QHeaderView.ResizeToContents)
        if ben_or_stonks == 'npc':
            _hs = ['Owner', 'Location', 'Item', 'Buy', 'Sell', 'Profit']
            bos_.setSectionResizeMode(0, QtWidgets.QHeaderView.ResizeToContents)
            bos_.setSectionResizeMode(1, QtWidgets.QHeaderView.ResizeToContents)
            bos_.setSectionResizeMode(2, QtWidgets.QHeaderView.Stretch)
            bos_.setSectionResizeMode(3, QtWidgets.QHeaderView.ResizeToContents)
            bos_.setSectionResizeMode(4, QtWidgets.QHeaderView.ResizeToContents)
            bos_.setSectionResizeMode(5, QtWidgets.QHeaderView.ResizeToContents)
        if ben_or_stonks == 'stonks':
            _hs = ['Vendor', 'Location', 'Item', 'Num', 'Price', 'FMI', 'Profit']
            bos_.setSectionResizeMode(0, QtWidgets.QHeaderView.Stretch)
            bos_.setSectionResizeMode(1, QtWidgets.QHeaderView.ResizeToContents)
            bos_.setSectionResizeMode(2, QtWidgets.QHeaderView.Stretch)
            bos_.setSectionResizeMode(3, QtWidgets.QHeaderView.ResizeToContents)
            bos_.setSectionResizeMode(4, QtWidgets.QHeaderView.ResizeToContents)
            bos_.setSectionResizeMode(5, QtWidgets.QHeaderView.ResizeToContents)
            bos_.setSectionResizeMode(6, QtWidgets.QHeaderView.ResizeToContents)
        if ben_or_stonks == 'storage_npc':
            _hs = ['Item', 'Profit']
            bos_.setSectionResizeMode(0, QtWidgets.QHeaderView.Stretch)
            bos_.setSectionResizeMode(1, QtWidgets.QHeaderView.ResizeToContents)
        if ben_or_stonks == 'storage_buy':
            _hs = ['Buyer', 'Item', 'Location', 'Profit']
            bos_.setSectionResizeMode(0, QtWidgets.QHeaderView.Stretch)
            bos_.setSectionResizeMode(1, QtWidgets.QHeaderView.ResizeToContents)
            bos_.setSectionResizeMode(2, QtWidgets.QHeaderView.Stretch)
            bos_.setSectionResizeMode(3, QtWidgets.QHeaderView.Stretch)
        if ben_or_stonks == 'storage_vend':
            _hs = ['Item', 'Price', 'Profit', 'Score']
            bos_.setSectionResizeMode(0, QtWidgets.QHeaderView.Stretch)
            bos_.setSectionResizeMode(1, QtWidgets.QHeaderView.ResizeToContents)
            bos_.setSectionResizeMode(2, QtWidgets.QHeaderView.ResizeToContents)
            bos_.setSectionResizeMode(3, QtWidgets.QHeaderView.ResizeToContents)
        if ben_or_stonks == 'sentry':
            _hs = ['Vendor', 'Item', 'Location', 'Price', 'MPrice', 'Diff']
            bos_.setSectionResizeMode(0, QtWidgets.QHeaderView.ResizeToContents)
            bos_.setSectionResizeMode(1, QtWidgets.QHeaderView.Stretch)
            bos_.setSectionResizeMode(2, QtWidgets.QHeaderView.ResizeToContents)
            bos_.setSectionResizeMode(3, QtWidgets.QHeaderView.ResizeToContents)
            bos_.setSectionResizeMode(4, QtWidgets.QHeaderView.ResizeToContents)
            bos_.setSectionResizeMode(5, QtWidgets.QHeaderView.ResizeToContents)
        #set header names
        shortcut.setHorizontalHeaderLabels(_hs)
        #fix missing bottom line of headers
        shortcut.horizontalHeader().setStyleSheet( "QHeaderView::section{"
                                                        "border-top:0px solid #D8D8D8;"
                                                        "border-left:0px solid #D8D8D8;"
                                                        "border-right:1px solid #D8D8D8;"
                                                        "border-bottom: 1px solid #D8D8D8;"
                                                        "background-color:white;"
                                                        "padding:4px;"
                                                    "}"
                                                    "QTableCornerButton::section{"
                                                        "border-top:0px solid #D8D8D8;"
                                                        "border-left:0px solid #D8D8D8;"
                                                        "border-right:1px solid #D8D8D8;"
                                                        "border-bottom: 1px solid #D8D8D8;"
                                                        "background-color:white;"
                                                    "}" )
        #fill table
        row = 0
        #every item in our array
        for tup in content_array:
            col = 0
            #every element of an item
            for item in tup:
                #shortcut for cell
                cellinfo = QtWidgets.QTableWidgetItem(item)
                #dunno what it is, but it help to show integers
                cellinfo.setData(QtCore.Qt.EditRole, item)
                
                ns_check = (_hs[col] == 'S> Owner' or 
                            _hs[col] == 'B> Owner' or 
                            _hs[col] == 'Buyer' or
                            _hs[col] == 'Vendor' or
                            _hs[col] == 'Owner')
                
                #for item tab
                i_check = (_hs[col] == 'Item' or
                           _hs[col] == 'Price') and (not
                           ben_or_stonks == 'stonks' and not
                           ben_or_stonks == 'npc' and not
                           ben_or_stonks == 'sentry')
                #making navshop button
                if ns_check:
                    self.copy_button_creator(shortcut, item, row, col, True)
                
                if i_check:
                    self.copy_button_creator(shortcut, item, row, col, False)
                
                #Readonly
                cellinfo.setFlags(
                    QtCore.Qt.ItemIsSelectable | QtCore.Qt.ItemIsEnabled
                )
                #set cell
                shortcut.setItem(row, col, cellinfo)
                #align table text to center
                #cellinfo.setTextAlignment(QtCore.Qt.AlignHCenter)
                col += 1
            row += 1
        #if we have empty list, make beautiful headers
        if row == 0:
            col = 0
            for i in _hs:
                shortcut.horizontalHeader().setSectionResizeMode(col, QtWidgets.QHeaderView.Stretch)  
                col += 1
        #changing height of headers, because default take too much space
        _font_size = shortcut.fontInfo().pointSize()
        shortcut.horizontalHeader().setFixedHeight((_font_size*2)+6)
        #and whole table too
        shortcut.resizeColumnsToContents()
        shortcut.resizeRowsToContents()
        #включаем сортировку, обязательно делать ПОСЛЕ наполнения таблицы
        shortcut.setSortingEnabled(True)
    
    def set_item(self, sc1, sc2, sc3):
            #make shortcut
            shortcut = self.ui.centralwidget.findChild(QtWidgets.QTableWidget, 'tops_table')
            shortcut.setSortingEnabled(False)
            #reset table
            shortcut.clearContents()
            shortcut.setRowCount(0)
            shortcut.setColumnCount(4)
            
            #set header names
            _hs = ['Top', 'Item', '', '~']
            #1 COMBOBOX
            if sc1 == 'Popularity':
                top1 = msf.top_pop
                _hs[2] = 'Amount'
            if sc1 == 'Value':
                top1 = msf.top_val
                _hs[2] = 'Spend zeny'
            if sc1 == 'Score':
                top1 = msf.top_score
                _hs[2] = 'Rating'
            shortcut.setHorizontalHeaderLabels(_hs)
            #2-3 COMBOBOX
            if sc2 == 'All':
                pass
            if sc2 == 'Misc':
                top1 = msf.extract_top(top1, "IT_ETC")
            if sc2 == 'Weapon':
                if self.previous_combobox2 != 'Weapon':
                    sc3_list = ['All', 'Dagger', 'Sword: 1H', 'Sword: 2H', 'Spear: 1H', 'Spear: 2H', 'Axe: 1H', 'Axe: 2H', 'Mace: 1H', 'Mace: 2H', 'Staff: 1H', 'Staff: 2H', 'Bow', 'Knuckle', 'Musical instrument', 'Whip', 'Book', 'Katar', 'Revolver', 'Rifle', 'Gatling', 'Shotgun', 'Grenade', 'Huuma']
                    sc3_sc = self.ui.centralwidget.findChild(QtWidgets.QComboBox, 'comboBox_3')
                    sc3_sc.blockSignals(True)
                    sc3_sc.clear()
                    sc3_sc.addItems(sc3_list)
                    sc3_sc.blockSignals(False)
                if sc3 == 'All':
                    top1 = msf.extract_top(top1, "IT_WEAPON")
                if sc3 == 'Dagger':
                    top1 = msf.extract_top(top1, "IT_WEAPON", "W_DAGGER")
                if sc3 == 'Sword: 1H':
                    top1 = msf.extract_top(top1, "IT_WEAPON", "W_1HSWORD")
                if sc3 == 'Sword: 2H':
                    top1 = msf.extract_top(top1, "IT_WEAPON", "W_2HSWORD")
                if sc3 == 'Spear: 1H':
                    top1 = msf.extract_top(top1, "IT_WEAPON", "W_1HSPEAR")
                if sc3 == 'Spear: 2H':
                    top1 = msf.extract_top(top1, "IT_WEAPON", "W_2HSPEAR")
                if sc3 == 'Axe: 1H':
                    top1 = msf.extract_top(top1, "IT_WEAPON", "W_1HAXE")
                if sc3 == 'Axe: 2H':
                    top1 = msf.extract_top(top1, "IT_WEAPON", "W_2HAXE")
                if sc3 == 'Mace: 1H':
                    top1 = msf.extract_top(top1, "IT_WEAPON", "W_MACE")
                if sc3 == 'Mace: 2H':
                    top1 = msf.extract_top(top1, "IT_WEAPON", "W_2HMACE")
                if sc3 == 'Staff: 1H':
                    top1 = msf.extract_top(top1, "IT_WEAPON", "W_STAFF")
                if sc3 == 'Staff: 2H':
                    top1 = msf.extract_top(top1, "IT_WEAPON", "W_2HSTAFF")
                if sc3 == 'Bow':
                    top1 = msf.extract_top(top1, "IT_WEAPON", "W_BOW")
                if sc3 == 'Knuckle':
                    top1 = msf.extract_top(top1, "IT_WEAPON", "W_KNUCKLE")
                if sc3 == 'Musical instrument':
                    top1 = msf.extract_top(top1, "IT_WEAPON", "W_MUSICAL")
                if sc3 == 'Whip':
                    top1 = msf.extract_top(top1, "IT_WEAPON", "W_WHIP")
                if sc3 == 'Book':
                    top1 = msf.extract_top(top1, "IT_WEAPON", "W_BOOK")
                if sc3 == 'Katar':
                    top1 = msf.extract_top(top1, "IT_WEAPON", "W_KATAR")
                if sc3 == 'Revolver':
                    top1 = msf.extract_top(top1, "IT_WEAPON", "W_REVOLVER")
                if sc3 == 'Rifle':
                    top1 = msf.extract_top(top1, "IT_WEAPON", "W_RIFLE")
                if sc3 == 'Gatling':
                    top1 = msf.extract_top(top1, "IT_WEAPON", "W_GATLING")
                if sc3 == 'Shotgun':
                    top1 = msf.extract_top(top1, "IT_WEAPON", "W_SHOTGUN")
                if sc3 == 'Grenade':
                    top1 = msf.extract_top(top1, "IT_WEAPON", "W_GRENADE")
                if sc3 == 'Huuma':
                    top1 = msf.extract_top(top1, "IT_WEAPON", "W_HUUMA")
            if sc2 == 'Armor':
                top1 = msf.extract_top(top1, "IT_ARMOR")
            if sc2 == 'Card':
                top1 = msf.extract_top(top1, "IT_CARD")
            if sc2 == 'Healing':
                top1 = msf.extract_top(top1, "IT_HEALING")
            if sc2 == 'Usable':
                top1 = msf.extract_top(top1, "IT_USABLE")
            if sc2 == 'Ammo':
                if self.previous_combobox2 != 'Ammo':
                    sc3_list = ['All', 'Arrows', 'Throwing daggers', 'Bullets', 'Shells', 'Grenades', 'Shuriken', 'Kunai', 'Cannon balls', 'Other throwing weapons']
                    sc3_sc = self.ui.centralwidget.findChild(QtWidgets.QComboBox, 'comboBox_3')
                    sc3_sc.blockSignals(True)
                    sc3_sc.clear()
                    sc3_sc.addItems(sc3_list)
                    sc3_sc.blockSignals(False)
                if sc3 == 'All':
                    top1 = msf.extract_top(top1, "IT_AMMO")
                if sc3 == 'Arrows':
                    top1 = msf.extract_top(top1, "IT_AMMO", "A_ARROW")
                if sc3 == 'Throwing daggers':
                    top1 = msf.extract_top(top1, "IT_AMMO", "A_DAGGER")
                if sc3 == 'Bullets':
                    top1 = msf.extract_top(top1, "IT_AMMO", "A_BULLET")
                if sc3 == 'Shells':
                    top1 = msf.extract_top(top1, "IT_AMMO", "A_SHELL")
                if sc3 == 'Grenades':
                    top1 = msf.extract_top(top1, "IT_AMMO", "A_GRENADE")
                if sc3 == 'Shuriken':
                    top1 = msf.extract_top(top1, "IT_AMMO", "A_SHURIKEN")
                if sc3 == 'Kunai':
                    top1 = msf.extract_top(top1, "IT_AMMO", "A_KUNAI")
                if sc3 == 'Cannon balls':
                    top1 = msf.extract_top(top1, "IT_AMMO", "A_CANNONBALL")
                if sc3 == 'Other throwing weapons':
                    top1 = msf.extract_top(top1, "IT_AMMO", "A_THROWWEAPON")
                
            shortcut.setRowCount(len(top1))
            
            #fix missing bottom line of headers
            shortcut.horizontalHeader().setStyleSheet( "QHeaderView::section{"
                                                            "border-top:0px solid #D8D8D8;"
                                                            "border-left:0px solid #D8D8D8;"
                                                            "border-right:1px solid #D8D8D8;"
                                                            "border-bottom: 1px solid #D8D8D8;"
                                                            "background-color:white;"
                                                            "padding:4px;"
                                                        "}"
                                                        "QTableCornerButton::section{"
                                                            "border-top:0px solid #D8D8D8;"
                                                            "border-left:0px solid #D8D8D8;"
                                                            "border-right:1px solid #D8D8D8;"
                                                            "border-bottom: 1px solid #D8D8D8;"
                                                            "background-color:white;"
                                                        "}" )
            #fill table
            row = 0
            #every item in our array
            for tup in top1:
                col = 0
                #TOP
                cellinfo = QtWidgets.QTableWidgetItem(tup['place'])
                cellinfo.setData(QtCore.Qt.DisplayRole, tup['place'])
                cellinfo.setFlags(
                        QtCore.Qt.ItemIsSelectable | QtCore.Qt.ItemIsEnabled
                    )
                
                shortcut.setItem(row, col, cellinfo)
                #align table text to center
                cellinfo.setTextAlignment(QtCore.Qt.AlignCenter)
                col += 1
                
                #ITEM
                _in = msf.shop_item_name(tup)
                cellinfo = QtWidgets.QTableWidgetItem(_in)
                cellinfo.setFlags(
                        QtCore.Qt.ItemIsSelectable | QtCore.Qt.ItemIsEnabled
                    )
                
                shortcut.setItem(row, col, cellinfo)
                cellinfo.setTextAlignment(QtCore.Qt.AlignVCenter | QtCore.Qt.AlignLeft)
                col += 1
                
                #SCORE
                cellinfo = QtWidgets.QTableWidgetItem(str(tup['score']))
                cellinfo.setFlags(
                        QtCore.Qt.ItemIsSelectable | QtCore.Qt.ItemIsEnabled
                    )
                
                shortcut.setItem(row, col, cellinfo)
                #align table text to center
                cellinfo.setTextAlignment(QtCore.Qt.AlignCenter)
                col += 1
                
                #TILDA
                cellinfo = QtWidgets.QTableWidgetItem(tup['progression'])
                cellinfo.setFlags(
                        QtCore.Qt.ItemIsSelectable | QtCore.Qt.ItemIsEnabled
                    )
                shortcut.setItem(row, col, cellinfo)
                
                #align table text to center
                cellinfo.setTextAlignment(QtCore.Qt.AlignCenter)
                
                row += 1
            shortcut.horizontalHeader().setSectionResizeMode(0, QtWidgets.QHeaderView.ResizeToContents)
            shortcut.horizontalHeader().setSectionResizeMode(1, QtWidgets.QHeaderView.Stretch)
            shortcut.horizontalHeader().setSectionResizeMode(2, QtWidgets.QHeaderView.Fixed)
            shortcut.horizontalHeader().setSectionResizeMode(3, QtWidgets.QHeaderView.ResizeToContents)
            #and whole table too
            #shortcut.resizeColumnsToContents()
            shortcut.resizeRowsToContents()
            #включаем сортировку, обязательно делать ПОСЛЕ наполнения таблицы
            shortcut.setSortingEnabled(True)
    def set_monster(self, data_array, price):
        #make shortcut
        shortcut = self.ui.centralwidget.findChild(QtWidgets.QTableWidget, 'monster_table')
        shortcut.setSortingEnabled(False)
        #reset table
        shortcut.clearContents()
        shortcut.setRowCount(0)
        
        
        #set header names
        if price == 'market':
            _hs = ['Top', 'ID', 'Monster', 'Price', '~']
        if price == 'npc':
            _hs = ['Top', 'ID', 'Monster', 'Price']
        shortcut.setColumnCount(len(_hs))
        shortcut.setHorizontalHeaderLabels(_hs)
        shortcut.setRowCount(len(data_array))
            
        #fix missing bottom line of headers
        shortcut.horizontalHeader().setStyleSheet( "QHeaderView::section{"
                                                        "border-top:0px solid #D8D8D8;"
                                                        "border-left:0px solid #D8D8D8;"
                                                        "border-right:1px solid #D8D8D8;"
                                                        "border-bottom: 1px solid #D8D8D8;"
                                                        "background-color:white;"
                                                        "padding:4px;"
                                                    "}"
                                                    "QTableCornerButton::section{"
                                                        "border-top:0px solid #D8D8D8;"
                                                        "border-left:0px solid #D8D8D8;"
                                                        "border-right:1px solid #D8D8D8;"
                                                        "border-bottom: 1px solid #D8D8D8;"
                                                        "background-color:white;"
                                                    "}" )
        #fill table
        row = 0
        #every item in our array
        for tup in data_array:
            col = 0
            #TOP
            cellinfo = QtWidgets.QTableWidgetItem(tup['place'])
            cellinfo.setData(QtCore.Qt.DisplayRole, tup['place'])
            cellinfo.setFlags(
                    QtCore.Qt.ItemIsSelectable | QtCore.Qt.ItemIsEnabled
                )
            
            shortcut.setItem(row, col, cellinfo)
            #align table text to center
            cellinfo.setTextAlignment(QtCore.Qt.AlignCenter)
            col += 1
            
            #ID
            cellinfo = QtWidgets.QTableWidgetItem(tup['monster_id'])
            cellinfo.setData(QtCore.Qt.DisplayRole, tup['monster_id'])
            cellinfo.setFlags(
                    QtCore.Qt.ItemIsSelectable | QtCore.Qt.ItemIsEnabled
                )
            
            shortcut.setItem(row, col, cellinfo)
            #align table text to center
            cellinfo.setTextAlignment(QtCore.Qt.AlignCenter)
            col += 1
            
            #MONSTER
            cellinfo = QtWidgets.QTableWidgetItem(tup['name'])
            cellinfo.setFlags(
                    QtCore.Qt.ItemIsSelectable | QtCore.Qt.ItemIsEnabled
                )
            
            shortcut.setItem(row, col, cellinfo)
            cellinfo.setTextAlignment(QtCore.Qt.AlignVCenter | QtCore.Qt.AlignLeft)
            col += 1
            
            #PRICE
            cellinfo = QtWidgets.QTableWidgetItem(str(tup['price']))
            cellinfo.setFlags(
                    QtCore.Qt.ItemIsSelectable | QtCore.Qt.ItemIsEnabled
                )
            
            shortcut.setItem(row, col, cellinfo)
            #align table text to center
            cellinfo.setTextAlignment(QtCore.Qt.AlignCenter)
            col += 1
            
            if price == 'market':
                #TILDA
                cellinfo = QtWidgets.QTableWidgetItem(tup['progression'])
                cellinfo.setFlags(
                        QtCore.Qt.ItemIsSelectable | QtCore.Qt.ItemIsEnabled
                    )
                shortcut.setItem(row, col, cellinfo)
                
                #align table text to center
                cellinfo.setTextAlignment(QtCore.Qt.AlignCenter)
            
            row += 1
        if price == 'market':
            shortcut.horizontalHeader().setSectionResizeMode(0, QtWidgets.QHeaderView.ResizeToContents)
            shortcut.horizontalHeader().setSectionResizeMode(1, QtWidgets.QHeaderView.ResizeToContents)
            shortcut.horizontalHeader().setSectionResizeMode(2, QtWidgets.QHeaderView.Stretch)
            shortcut.horizontalHeader().setSectionResizeMode(3, QtWidgets.QHeaderView.Fixed)
            shortcut.horizontalHeader().setSectionResizeMode(4, QtWidgets.QHeaderView.ResizeToContents)
        if price == 'npc':
            shortcut.horizontalHeader().setSectionResizeMode(0, QtWidgets.QHeaderView.ResizeToContents)
            shortcut.horizontalHeader().setSectionResizeMode(1, QtWidgets.QHeaderView.ResizeToContents)
            shortcut.horizontalHeader().setSectionResizeMode(2, QtWidgets.QHeaderView.Stretch)
            shortcut.horizontalHeader().setSectionResizeMode(3, QtWidgets.QHeaderView.ResizeToContents)
        #changing height of headers, because default take too much space
        _font_size = shortcut.fontInfo().pointSize()
        shortcut.horizontalHeader().setFixedHeight((_font_size*2)+6)
        #and whole table too
        shortcut.resizeColumnsToContents()
        shortcut.resizeRowsToContents()
        #включаем сортировку, обязательно делать ПОСЛЕ наполнения таблицы
        shortcut.setSortingEnabled(True)
    def set_item_db_table(self, data_array, table_widget_name):
        #make shortcut
        shortcut = self.ui.centralwidget.findChild(QtWidgets.QTableWidget, table_widget_name)
        shortcut.setSortingEnabled(False)
        #reset table
        shortcut.clearContents()
        shortcut.setRowCount(0)
        
        
        #set header names
        _hs = ['ID', 'Name', '+']
        shortcut.setColumnCount(len(_hs))
        shortcut.setHorizontalHeaderLabels(_hs)
        shortcut.setRowCount(len(data_array))
            
        #fix missing bottom line of headers
        shortcut.horizontalHeader().setStyleSheet( "QHeaderView::section{"
                                                        "border-top:0px solid #D8D8D8;"
                                                        "border-left:0px solid #D8D8D8;"
                                                        "border-right:1px solid #D8D8D8;"
                                                        "border-bottom: 1px solid #D8D8D8;"
                                                        "background-color:white;"
                                                        "padding:4px;"
                                                    "}"
                                                    "QTableCornerButton::section{"
                                                        "border-top:0px solid #D8D8D8;"
                                                        "border-left:0px solid #D8D8D8;"
                                                        "border-right:1px solid #D8D8D8;"
                                                        "border-bottom: 1px solid #D8D8D8;"
                                                        "background-color:white;"
                                                    "}" )
        #fill table
        row = 0
        #every item in our array
        for tup in data_array:
            col = 0
            #ID
            cellinfo = QtWidgets.QTableWidgetItem(tup['item_id'])
            cellinfo.setData(QtCore.Qt.DisplayRole, tup['item_id'])
            cellinfo.setFlags(
                    QtCore.Qt.ItemIsSelectable | QtCore.Qt.ItemIsEnabled
                )
            
            shortcut.setItem(row, col, cellinfo)
            #align table text to center
            cellinfo.setTextAlignment(QtCore.Qt.AlignCenter)
            col += 1
            
            #Name
            _name = item_name(item_db, tup['item_id'])
            cellinfo = QtWidgets.QTableWidgetItem(_name)
            cellinfo.setData(QtCore.Qt.DisplayRole, _name)
            cellinfo.setFlags(
                    QtCore.Qt.ItemIsSelectable | QtCore.Qt.ItemIsEnabled
                )
            
            shortcut.setItem(row, col, cellinfo)
            #align table text to center
            cellinfo.setTextAlignment(QtCore.Qt.AlignCenter)
            col += 1
            
            #Button
            cellinfo = QtWidgets.QTableWidgetItem('+')
            cellinfo.setFlags(
                    QtCore.Qt.ItemIsSelectable | QtCore.Qt.ItemIsEnabled
                )
            self.sentry_add_button_creator(shortcut, row, col, tup['item_id'])
            shortcut.setItem(row, col, cellinfo)
            cellinfo.setTextAlignment(QtCore.Qt.AlignVCenter | QtCore.Qt.AlignLeft)
            col += 1
            
            row += 1
            
        shortcut.horizontalHeader().setSectionResizeMode(0, QtWidgets.QHeaderView.ResizeToContents)
        shortcut.horizontalHeader().setSectionResizeMode(1, QtWidgets.QHeaderView.Stretch)
        shortcut.horizontalHeader().setSectionResizeMode(2, QtWidgets.QHeaderView.ResizeToContents)
        #changing height of headers, because default take too much space
        _font_size = shortcut.fontInfo().pointSize()
        shortcut.horizontalHeader().setFixedHeight((_font_size*2)+6)
        #and whole table too
        shortcut.resizeColumnsToContents()
        shortcut.resizeRowsToContents()
        #включаем сортировку, обязательно делать ПОСЛЕ наполнения таблицы
        shortcut.setSortingEnabled(True)
    def set_sentry_raw(self, data_array):
        #make shortcut
        shortcut = self.ui.centralwidget.findChild(QtWidgets.QTableWidget, 'sentry_shopping_table')
        shortcut.setSortingEnabled(False)
        #reset table
        shortcut.clearContents()
        shortcut.setRowCount(0)
        
        #set header names
        _hs = ['Name', '-']
        shortcut.setColumnCount(len(_hs))
        shortcut.setHorizontalHeaderLabels(_hs)
        shortcut.setRowCount(len(data_array))
            
        #fix missing bottom line of headers
        shortcut.horizontalHeader().setStyleSheet( "QHeaderView::section{"
                                                        "border-top:0px solid #D8D8D8;"
                                                        "border-left:0px solid #D8D8D8;"
                                                        "border-right:1px solid #D8D8D8;"
                                                        "border-bottom: 1px solid #D8D8D8;"
                                                        "background-color:white;"
                                                        "padding:4px;"
                                                    "}"
                                                    "QTableCornerButton::section{"
                                                        "border-top:0px solid #D8D8D8;"
                                                        "border-left:0px solid #D8D8D8;"
                                                        "border-right:1px solid #D8D8D8;"
                                                        "border-bottom: 1px solid #D8D8D8;"
                                                        "background-color:white;"
                                                    "}" )
        #fill table
        row = 0
        #every item in our array
        for tup in data_array:
            col = 0
            #ID
            name = msf.shop_item_name(tup)
            cellinfo = QtWidgets.QTableWidgetItem(name)
            cellinfo.setData(QtCore.Qt.DisplayRole, name)
            cellinfo.setFlags(
                    QtCore.Qt.ItemIsSelectable | QtCore.Qt.ItemIsEnabled
                )
            
            shortcut.setItem(row, col, cellinfo)
            #align table text to center
            cellinfo.setTextAlignment(QtCore.Qt.AlignCenter)
            col += 1
            
            #ID
            cellinfo = QtWidgets.QTableWidgetItem('-')
            cellinfo.setData(QtCore.Qt.DisplayRole, '-')
            cellinfo.setFlags(
                    QtCore.Qt.ItemIsSelectable | QtCore.Qt.ItemIsEnabled
                )
            self.sentry_delete_button_creator(data_array, shortcut, row, col, tup['item_id'])
            shortcut.setItem(row, col, cellinfo)
            #align table text to center
            cellinfo.setTextAlignment(QtCore.Qt.AlignCenter)
            col += 1
            row += 1
            
        shortcut.horizontalHeader().setSectionResizeMode(0, QtWidgets.QHeaderView.Stretch)
        shortcut.horizontalHeader().setSectionResizeMode(1, QtWidgets.QHeaderView.ResizeToContents)
        #changing height of headers, because default take too much space
        _font_size = shortcut.fontInfo().pointSize()
        shortcut.horizontalHeader().setFixedHeight((_font_size*2)+6)
        #and whole table too
        shortcut.resizeColumnsToContents()
        shortcut.resizeRowsToContents()
        #включаем сортировку, обязательно делать ПОСЛЕ наполнения таблицы
        shortcut.setSortingEnabled(True)
    def set_market_tab(self):
        getben = mf.benefits_buy_founder()
        self.set_table('buy_table', getben['buy'], 'ben')
        self.set_table('npc_table', getben['npc'], 'npc')
        getstonks = mf.market_stonks()
        self.set_table('stonks50_table', getstonks['Uber stonks'], 'stonks')
        self.set_table('stonks25_table', getstonks['OK stonks'], 'stonks')
    def set_item_tab(self):
        shortcut1 = self.ui.centralwidget.findChild(QtWidgets.QComboBox, 'comboBox_1')
        shortcut2 = self.ui.centralwidget.findChild(QtWidgets.QComboBox, 'comboBox_2')
        shortcut3 = self.ui.centralwidget.findChild(QtWidgets.QComboBox, 'comboBox_3')
        
        if shortcut2.currentText() != 'Weapon' and shortcut2.currentText() != 'Ammo':
            shortcut3.setEnabled(False)
            self.set_item(shortcut1.currentText(), shortcut2.currentText(), False)
        else:
            shortcut3.setEnabled(True)
            self.set_item(shortcut1.currentText(), shortcut2.currentText(), shortcut3.currentText())
        self.previous_combobox2 = shortcut2.currentText()
    def monster_race_checkbox_all(self):
        #MONSTER RACE CHECKBOXES
        monster_race_formless = self.ui.centralwidget.findChild(QtWidgets.QCheckBox, 'monster_race_formless')
        monster_race_brute = self.ui.centralwidget.findChild(QtWidgets.QCheckBox, 'monster_race_brute')
        monster_race_insect = self.ui.centralwidget.findChild(QtWidgets.QCheckBox, 'monster_race_insect')
        monster_race_demon = self.ui.centralwidget.findChild(QtWidgets.QCheckBox, 'monster_race_demon')
        monster_race_angel = self.ui.centralwidget.findChild(QtWidgets.QCheckBox, 'monster_race_angel')
        monster_race_undead = self.ui.centralwidget.findChild(QtWidgets.QCheckBox, 'monster_race_undead')
        monster_race_plant = self.ui.centralwidget.findChild(QtWidgets.QCheckBox, 'monster_race_plant')
        monster_race_fish = self.ui.centralwidget.findChild(QtWidgets.QCheckBox, 'monster_race_fish')
        monster_race_demihuman = self.ui.centralwidget.findChild(QtWidgets.QCheckBox, 'monster_race_demihuman')
        monster_race_dragon = self.ui.centralwidget.findChild(QtWidgets.QCheckBox, 'monster_race_dragon')
        monster_race_all = self.ui.centralwidget.findChild(QtWidgets.QCheckBox, 'monster_race_all')
        checker_list = [monster_race_formless, monster_race_brute, monster_race_insect,
                        monster_race_demon, monster_race_angel, monster_race_undead,
                        monster_race_plant, monster_race_fish, monster_race_demihuman,
                        monster_race_dragon]
        #check all other checkboxes
        if monster_race_all.isChecked():
            for c in checker_list:
                c.setChecked(True)
        else:
            #uncheck all other checkboxes
            for c in checker_list:
                c.setChecked(False)
    def monster_element_checkbox_all(self):
        #MONSTER ELEMENT CHECKBOXES
        monster_element_neutral = self.ui.centralwidget.findChild(QtWidgets.QCheckBox, 'monster_element_neutral')
        monster_element_fire = self.ui.centralwidget.findChild(QtWidgets.QCheckBox, 'monster_element_fire')
        monster_element_water = self.ui.centralwidget.findChild(QtWidgets.QCheckBox, 'monster_element_water')
        monster_element_earth = self.ui.centralwidget.findChild(QtWidgets.QCheckBox, 'monster_element_earth')
        monster_element_wind = self.ui.centralwidget.findChild(QtWidgets.QCheckBox, 'monster_element_wind')
        monster_element_holy = self.ui.centralwidget.findChild(QtWidgets.QCheckBox, 'monster_element_holy')
        monster_element_ghost = self.ui.centralwidget.findChild(QtWidgets.QCheckBox, 'monster_element_ghost')
        monster_element_poison = self.ui.centralwidget.findChild(QtWidgets.QCheckBox, 'monster_element_poison')
        monster_element_shadow = self.ui.centralwidget.findChild(QtWidgets.QCheckBox, 'monster_element_shadow')
        monster_element_undead = self.ui.centralwidget.findChild(QtWidgets.QCheckBox, 'monster_element_undead')
        monster_element_all = self.ui.centralwidget.findChild(QtWidgets.QCheckBox, 'monster_element_all')
        checker_list = [monster_element_neutral, monster_element_fire, monster_element_water,
                        monster_element_earth, monster_element_wind, monster_element_holy,
                        monster_element_ghost, monster_element_poison, monster_element_shadow,
                        monster_element_undead]
        #check all other checkboxes
        if monster_element_all.isChecked():
            for c in checker_list:
                c.setChecked(True)
        else:
            #uncheck all other checkboxes
            for c in checker_list:
                c.setChecked(False)
    def monster_size_checkbox_all(self):
        #MONSTER SIZE CHECKBOXES
        monster_size_all = self.ui.centralwidget.findChild(QtWidgets.QCheckBox, 'monster_size_all')
        monster_size_large = self.ui.centralwidget.findChild(QtWidgets.QCheckBox, 'monster_size_large')
        monster_size_medium = self.ui.centralwidget.findChild(QtWidgets.QCheckBox, 'monster_size_medium')
        monster_size_small = self.ui.centralwidget.findChild(QtWidgets.QCheckBox, 'monster_size_small')
        checker_list = [monster_size_large, monster_size_medium, monster_size_small]
        #check all other checkboxes
        if monster_size_all.isChecked():
            for c in checker_list:
                c.setChecked(True)
        else:
            #uncheck all other checkboxes
            for c in checker_list:
                c.setChecked(False)
    def monster_race_checkbox_other(self):
        #MONSTER RACE CHECKBOXES
        monster_race_formless = self.ui.centralwidget.findChild(QtWidgets.QCheckBox, 'monster_race_formless')
        monster_race_brute = self.ui.centralwidget.findChild(QtWidgets.QCheckBox, 'monster_race_brute')
        monster_race_insect = self.ui.centralwidget.findChild(QtWidgets.QCheckBox, 'monster_race_insect')
        monster_race_demon = self.ui.centralwidget.findChild(QtWidgets.QCheckBox, 'monster_race_demon')
        monster_race_angel = self.ui.centralwidget.findChild(QtWidgets.QCheckBox, 'monster_race_angel')
        monster_race_undead = self.ui.centralwidget.findChild(QtWidgets.QCheckBox, 'monster_race_undead')
        monster_race_plant = self.ui.centralwidget.findChild(QtWidgets.QCheckBox, 'monster_race_plant')
        monster_race_fish = self.ui.centralwidget.findChild(QtWidgets.QCheckBox, 'monster_race_fish')
        monster_race_demihuman = self.ui.centralwidget.findChild(QtWidgets.QCheckBox, 'monster_race_demihuman')
        monster_race_dragon = self.ui.centralwidget.findChild(QtWidgets.QCheckBox, 'monster_race_dragon')
        monster_race_all = self.ui.centralwidget.findChild(QtWidgets.QCheckBox, 'monster_race_all')
        checker_list = [monster_race_formless, monster_race_brute, monster_race_insect,
                        monster_race_demon, monster_race_angel, monster_race_undead,
                        monster_race_plant, monster_race_fish, monster_race_demihuman,
                        monster_race_dragon]
        #uncheck 'all' if not all checkboxes setted
        for h in checker_list:
            if h.isChecked():
                monster_race_all.blockSignals(True)
                monster_race_all.setChecked(False)
                monster_race_all.blockSignals(False)
        
        #check 'all' if all checkboxes setted
        c_counter = 0
        for c in checker_list:
            if c.isChecked():
                c_counter += 1
        if c_counter == len(checker_list):
            monster_race_all.setChecked(True)
    def monster_element_checkbox_other(self):
        #MONSTER ELEMENT CHECKBOXES
        monster_element_neutral = self.ui.centralwidget.findChild(QtWidgets.QCheckBox, 'monster_element_neutral')
        monster_element_fire = self.ui.centralwidget.findChild(QtWidgets.QCheckBox, 'monster_element_fire')
        monster_element_water = self.ui.centralwidget.findChild(QtWidgets.QCheckBox, 'monster_element_water')
        monster_element_earth = self.ui.centralwidget.findChild(QtWidgets.QCheckBox, 'monster_element_earth')
        monster_element_wind = self.ui.centralwidget.findChild(QtWidgets.QCheckBox, 'monster_element_wind')
        monster_element_holy = self.ui.centralwidget.findChild(QtWidgets.QCheckBox, 'monster_element_holy')
        monster_element_ghost = self.ui.centralwidget.findChild(QtWidgets.QCheckBox, 'monster_element_ghost')
        monster_element_poison = self.ui.centralwidget.findChild(QtWidgets.QCheckBox, 'monster_element_poison')
        monster_element_shadow = self.ui.centralwidget.findChild(QtWidgets.QCheckBox, 'monster_element_shadow')
        monster_element_undead = self.ui.centralwidget.findChild(QtWidgets.QCheckBox, 'monster_element_undead')
        monster_element_all = self.ui.centralwidget.findChild(QtWidgets.QCheckBox, 'monster_element_all')
        checker_list = [monster_element_neutral, monster_element_fire, monster_element_water,
                        monster_element_earth, monster_element_wind, monster_element_holy,
                        monster_element_ghost, monster_element_poison, monster_element_shadow,
                        monster_element_undead]
        #uncheck 'all' if not all checkboxes setted
        for h in checker_list:
            if h.isChecked():
                monster_element_all.blockSignals(True)
                monster_element_all.setChecked(False)
                monster_element_all.blockSignals(False)
        
        #check 'all' if all checkboxes setted
        c_counter = 0
        for c in checker_list:
            if c.isChecked():
                c_counter += 1
        if c_counter == len(checker_list):
            monster_element_all.setChecked(True)
    def monster_size_checkbox_other(self):
        #MONSTER SIZE CHECKBOXES
        monster_size_all = self.ui.centralwidget.findChild(QtWidgets.QCheckBox, 'monster_size_all')
        monster_size_large = self.ui.centralwidget.findChild(QtWidgets.QCheckBox, 'monster_size_large')
        monster_size_medium = self.ui.centralwidget.findChild(QtWidgets.QCheckBox, 'monster_size_medium')
        monster_size_small = self.ui.centralwidget.findChild(QtWidgets.QCheckBox, 'monster_size_small')
        checker_list = [monster_size_large, monster_size_medium, monster_size_small]
        #uncheck 'all' if not all checkboxes setted
        for h in checker_list:
            if h.isChecked():
                monster_size_all.blockSignals(True)
                monster_size_all.setChecked(False)
                monster_size_all.blockSignals(False)
        
        #check 'all' if all checkboxes setted
        c_counter = 0
        for c in checker_list:
            if c.isChecked():
                c_counter += 1
        if c_counter == len(checker_list):
            monster_size_all.setChecked(True)
    def set_monster_tab(self):
        #
        monster_race_all = self.ui.centralwidget.findChild(QtWidgets.QCheckBox, 'monster_race_all')
        #
        monster_race_formless = self.ui.centralwidget.findChild(QtWidgets.QCheckBox, 'monster_race_formless')
        monster_race_brute = self.ui.centralwidget.findChild(QtWidgets.QCheckBox, 'monster_race_brute')
        monster_race_insect = self.ui.centralwidget.findChild(QtWidgets.QCheckBox, 'monster_race_insect')
        monster_race_demon = self.ui.centralwidget.findChild(QtWidgets.QCheckBox, 'monster_race_demon')
        monster_race_angel = self.ui.centralwidget.findChild(QtWidgets.QCheckBox, 'monster_race_angel')
        monster_race_undead = self.ui.centralwidget.findChild(QtWidgets.QCheckBox, 'monster_race_undead')
        monster_race_plant = self.ui.centralwidget.findChild(QtWidgets.QCheckBox, 'monster_race_plant')
        monster_race_fish = self.ui.centralwidget.findChild(QtWidgets.QCheckBox, 'monster_race_fish')
        monster_race_demihuman = self.ui.centralwidget.findChild(QtWidgets.QCheckBox, 'monster_race_demihuman')
        monster_race_dragon = self.ui.centralwidget.findChild(QtWidgets.QCheckBox, 'monster_race_dragon')
        
        #MONSTER ELEMENT CHECKBOXES
        monster_element_neutral = self.ui.centralwidget.findChild(QtWidgets.QCheckBox, 'monster_element_neutral')
        monster_element_fire = self.ui.centralwidget.findChild(QtWidgets.QCheckBox, 'monster_element_fire')
        monster_element_water = self.ui.centralwidget.findChild(QtWidgets.QCheckBox, 'monster_element_water')
        monster_element_earth = self.ui.centralwidget.findChild(QtWidgets.QCheckBox, 'monster_element_earth')
        monster_element_wind = self.ui.centralwidget.findChild(QtWidgets.QCheckBox, 'monster_element_wind')
        monster_element_holy = self.ui.centralwidget.findChild(QtWidgets.QCheckBox, 'monster_element_holy')
        monster_element_ghost = self.ui.centralwidget.findChild(QtWidgets.QCheckBox, 'monster_element_ghost')
        monster_element_poison = self.ui.centralwidget.findChild(QtWidgets.QCheckBox, 'monster_element_poison')
        monster_element_shadow = self.ui.centralwidget.findChild(QtWidgets.QCheckBox, 'monster_element_shadow')
        monster_element_undead = self.ui.centralwidget.findChild(QtWidgets.QCheckBox, 'monster_element_undead')
        monster_element_all = self.ui.centralwidget.findChild(QtWidgets.QCheckBox, 'monster_element_all')
        
        #MONSTER SIZE CHECKBOXES
        monster_size_all = self.ui.centralwidget.findChild(QtWidgets.QCheckBox, 'monster_size_all')
        monster_size_large = self.ui.centralwidget.findChild(QtWidgets.QCheckBox, 'monster_size_large')
        monster_size_medium = self.ui.centralwidget.findChild(QtWidgets.QCheckBox, 'monster_size_medium')
        monster_size_small = self.ui.centralwidget.findChild(QtWidgets.QCheckBox, 'monster_size_small')
        
        _kwargs = {}
        if monster_race_all.isChecked():
            pass
        else:
            race = []
            
            if monster_race_formless.isChecked():
                race.append('RC_Formless')
            
            if monster_race_brute.isChecked():
                race.append('RC_Brute')
            
            if monster_race_insect.isChecked():
                race.append('RC_Insect')
            
            if monster_race_demon.isChecked():
                race.append('RC_Demon')
            
            if monster_race_angel.isChecked():
                race.append('RC_Angel')
            
            if monster_race_undead.isChecked():
                race.append('RC_Undead')
            
            if monster_race_plant.isChecked():
                race.append('RC_Plant')
            
            if monster_race_fish.isChecked():
                race.append('RC_Fish')
            
            if monster_race_demihuman.isChecked():
                race.append('RC_DemiHuman')
            
            if monster_race_dragon.isChecked():
                race.append('RC_Dragon')
            if len(race) == 1:
                race = race[0]
            if race != []:
                _kwargs['race'] = race
        
        if monster_element_all.isChecked():
            pass
        else:
            element = []
            if monster_element_neutral.isChecked():
                element.append('Ele_Neutral')
            if monster_element_poison.isChecked():
                element.append('Ele_Poison')
            if monster_element_fire.isChecked():
                element.append('Ele_Fire')
            if monster_element_water.isChecked():
                element.append('Ele_Water')
            if monster_element_wind.isChecked():
                element.append('Ele_Wind')
            if monster_element_earth.isChecked():
                element.append('Ele_Earth')
            if monster_element_holy.isChecked():
                element.append('Ele_Holy')
            if monster_element_shadow.isChecked():
                element.append('Ele_Dark')
            if monster_element_ghost.isChecked():
                element.append('Ele_Ghost')
            if monster_element_undead.isChecked():
                element.append('Ele_Undead')
            if len(element) == 1:
                element = element[0]
            if element != []:
                _kwargs['element'] = element
        
        if monster_size_all.isChecked():
            pass
        else:
            size = []
            if monster_size_small.isChecked():
                size.append('Size_Small')
            if monster_size_medium.isChecked():
                size.append('Size_Medium')
            if monster_size_large.isChecked():
                size.append('Size_Large')
            if len(size) == 1:
                size = size[0]
            if size != []:
                _kwargs['size'] = size
        
        boss_combobox = self.ui.centralwidget.findChild(QtWidgets.QComboBox, 'monster_boss_combobox')
        if boss_combobox.currentText() == 'Boss':
            _kwargs['boss'] = True
        if boss_combobox.currentText() == 'Non-Boss':
            _kwargs['boss'] = False
            
        hit_line = self.ui.centralwidget.findChild(QtWidgets.QLineEdit, 'monster_hit_lineedit')
        if hit_line.text() != '':
            _kwargs['hit'] = int(hit_line.text())
        flee_line = self.ui.centralwidget.findChild(QtWidgets.QLineEdit, 'monster_flee_lineedit')
        if flee_line.text() != '':
            _kwargs['flee'] = int(flee_line.text())
        print(_kwargs)
        sh_price = self.ui.centralwidget.findChild(QtWidgets.QComboBox, 'monster_price_combobox')
        if sh_price.currentText() == 'Market price':
            #self.set_monster(msf.top_monster_market, 'market')
            if _kwargs != {}:
                self.set_monster(msf.extract_monster(msf.top_monster_market, **_kwargs), 'market')
            else:
                self.set_monster(msf.top_monster_market, 'market')
        if sh_price.currentText() == 'NPC price':
            if _kwargs != {}:
                self.set_monster(msf.extract_monster(msf.top_monster_npc, **_kwargs), 'npc')
            else:
                self.set_monster(msf.top_monster_npc, 'npc')
            
    def set_storage_tab(self):
        storage_input = self.ui.centralwidget.findChild(QtWidgets.QLineEdit, 'storage_input')
        #take user input and reformat it
        conv_input = '[{}]'.format(storage_input.text())
        #load correctly
        conv_input = json.loads(conv_input)
        market_storage = mf.estimate_storage(conv_input)
        self.set_table('to_npc_table', market_storage['npc'], 'storage_npc')
        self.set_table('to_buy_table', market_storage['buy'], 'storage_buy')
        self.set_table('to_vend_table', market_storage['vend'], 'storage_vend')
        
        
    
    def set_sentry_tab_offers(self):
        sentry_offers_table = self.ui.centralwidget.findChild(QtWidgets.QTableWidget, 'sentry_offers_table')
        #Offers tab
        sentry_final = mf.sentry_list()
        self.set_table('sentry_offers_table', sentry_final, 'sentry')
        print('sentry tab 1')
    
    def set_sentry_tab_item_db(self):
        #Shopping tab/ items
        all_items_table = self.ui.centralwidget.findChild(QtWidgets.QTableWidget, 'all_items_table')
        _sentry_raw = mf.sentry_load()
        self.set_item_db_table(item_db, 'all_items_table')
        print('sentry tab 2')
    
    def set_sentry_tab_shopping(self):
        #Shopping tab/ shopping list
        _sentry_raw = mf.sentry_load()
        self.set_sentry_raw(_sentry_raw)
        print('sentry tab 3')

    #@pyqtSlot()  
    def onChange(self,i):
        #Market tab
        if i == 0:
            #проверить, заполнена ли таблица
            #если не заполнена - заполнить
            if not self.market_tab_init:
                self.set_market_tab()
                self.market_tab_init = True
        #Item tab
        if i == 2:
            if not self.item_tab_init:
                self.set_item_tab()
                self.item_tab_init = True
        #Monster tab
        if i == 3:
            if not self.monster_tab_init:
                self.set_monster_tab()
                self.monster_tab_init = True
        #Sentry tab
        if i == 4:
            if not self.sentry_tab_init_offers:
                self.set_sentry_tab_offers()
                self.sentry_tab_init_offers = True
    def sentry_onChange(self, i):
        #можно допилить проверку для оптимизации
        #если список не изменился, то можно не проикдывать обновление, но нужно ввести проверку
        #Offers tab
        if i == 0:
            #if first tab opening
            if not self.sentry_tab_init_offers:
                self.set_sentry_tab_offers()
            #if tab opened after adding items
            if self.sentry_tab_update_needed:
                self.set_sentry_tab_offers()
                #no longer update needed
                self.sentry_tab_update_needed = False
        if i == 1:
            if not self.sentry_tab_init_shopping_items:
                self.set_sentry_tab_item_db()
                self.sentry_tab_init_shopping_items = True
            if not self.sentry_tab_init_shopping_raw:
                self.set_sentry_tab_shopping()
                self.sentry_tab_init_shopping_raw = True
        
app = QtWidgets.QApplication([])
application = mywindow()
application.show()
application.activateWindow()
 
sys.exit(app.exec())