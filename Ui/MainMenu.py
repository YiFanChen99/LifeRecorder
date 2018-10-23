#!/usr/bin/env python
# -*- coding: utf-8 -*-
from Ui.Utility.Widget import HBoxMenu, QWidget

from Model.TableViewModel import *


class MainMenu(QWidget):
    # noinspection PyProtectedMember
    CONFIG = {
        'menu': {
            'Record': {
                'callback': lambda obj: obj._changing_level_2_menu('Record'),
                'shortcut': 'F1',
                'menu': {
                    'Records': {
                        'shortcut': 'Ctrl+1',
                        'callback': lambda obj: obj._changing_source_model(RecordTableModel()),
                    },
                    'RecordGroup': {
                        'shortcut': 'Ctrl+2',
                        'callback': lambda obj: obj._changing_source_model(RecordGroupTableModel()),
                    },
                    'GroupRelation': {
                        'shortcut': 'Ctrl+3',
                        'callback': lambda obj: obj._changing_source_model(GroupRelationTableModel()),
                    },
                },
                'default_selection': 'Records',
            },
            'Sleep': {
                'callback': lambda obj: obj._changing_level_2_menu('Sleep'),
                'shortcut': 'F2',
                'menu': {
                    'SleepDateView': {
                        'shortcut': 'Ctrl+1',
                        'callback': lambda obj: obj._changing_source_model(SleepDurationTableModel()),
                    },
                    'Sleep': {
                        'shortcut': 'Ctrl+2',
                        'callback': lambda obj: obj._changing_source_model(SleepTableModel()),
                    },
                },
                'default_selection': 'SleepDateView',
            },
            'Flesh': {
                'callback': lambda obj: obj._changing_level_2_menu('Flesh'),
                'shortcut': 'F3',
                'menu': {
                    'Flesh': {
                        'shortcut': 'Ctrl+1',
                        'callback': lambda obj: obj._changing_source_model(FleshTableModel()),
                    },
                },
                'default_selection': 'Flesh',
            },
        },
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

    def trigger_default(self):
        self.level_1_menu.trigger_default()

    def _changing_level_2_menu(self, menu_name):
        if self.current_level_2_menu:
            self.current_level_2_menu.hide()

        level_2_menu = self.level_2_menus[menu_name]
        level_2_menu.show()
        level_2_menu.trigger_default()

    @property
    def current_level_2_menu(self):
        try:
            return self.level_2_menus[self.level_1_menu.last_action.text()]
        except AttributeError:
            return None

    def _changing_source_model(self, source_model):
        self.owner.main_panel.table_model.setSourceModel(source_model)
