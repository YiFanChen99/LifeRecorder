#!/usr/bin/env python
# -*- coding: utf-8 -*-
from collections import OrderedDict

from Ui.Utility.Widget import HBoxMenu, QWidget
from Model.TableViewModel import *


class MainMenu(QWidget):
    # noinspection PyProtectedMember
    CONFIG = {
        'menu': OrderedDict((
            ('Record', {
                'callback': lambda obj: obj._changing_level_2_menu('Record'),
                'shortcut': 'F1',
                'menu': OrderedDict((
                    ('Records', dict({
                        'shortcut': 'Ctrl+1',
                        'callback': lambda obj: obj._changing_source_model(RecordTableModel()),
                    })),
                    ('RecordGroup', {
                        'shortcut': 'Ctrl+2',
                        'callback': lambda obj: obj._changing_source_model(RecordGroupTableModel()),
                    }),
                    ('GroupRelation', {
                        'shortcut': 'Ctrl+3',
                        'callback': lambda obj: obj._changing_source_model(GroupRelationTableModel()),
                    }),
                    ('NewView', dict({
                        'callback': lambda obj: obj.owner._show_new_window(),
                        'shortcut': 'Ctrl+4',
                    })),
                )),
                'default_selection': 'Records',
            }),
        )),
        'default_selection': 'Record',
    }

    def __init__(self, owner):
        super(MainMenu, self).__init__()
        self.owner = owner

        self.level_1_menu = HBoxMenu(self, self.CONFIG)
        self.level_2_menus = {}
        for name, detail in self.CONFIG['menu'].items():
            self.level_2_menus[name] = HBoxMenu(self, detail)
            self.level_2_menus[name].hide()
        self.last_level_2_menu = None

    def trigger_default(self):
        self.level_1_menu.trigger()

    def _changing_level_2_menu(self, menu_name):
        if self.last_level_2_menu:
            self.last_level_2_menu.hide()

        self.last_level_2_menu = self.level_2_menus[menu_name]
        self.last_level_2_menu.show()
        self.last_level_2_menu.trigger()

    def _changing_source_model(self, source_model):
        self.owner.main_panel.table_model.setSourceModel(source_model)
