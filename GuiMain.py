#!/usr/bin/env python
# -*- coding: utf-8 -*-
import sys
from collections import OrderedDict

from Ui.MainPanel import *
from Ui.Utility.Window import *
from Ui.Utility.Panel import *
from Model.DataAccessor.Configure import config


class MainWindow(BaseMainWindow, BaseConfigLoader):
    def __init__(self, parent=None):
        super().__init__(parent)
        self._init_window(config['window'])

    def _create_main_panel(self):
        return MainPanel(self)


class MainPanel(BaseVBoxPanel, HBoxMenuable, PanelChangeable):
    MENU_CONFIG = {
        'menu': OrderedDict((
            ('Timeline', {
                'callback': lambda obj: obj.change_panel(0),
                'shortcut': 'F1',
            }),
            ('DataView', {
                'callback': lambda obj: obj.change_panel(1),
                'shortcut': 'F2',
            }),
        )),
        'default_selection': 0,
    }

    def _init_layout(self):
        self._init_menu(self.MENU_CONFIG)
        self._init_panels()

    def _create_panels(self):
        return (
            TimelinePanel(self),
            DataViewPanel(self),
        )


class TimelinePanel(BaseVBoxPanel, HBoxMenuable, PanelChangeable):
    MENU_CONFIG = {
        'menu': OrderedDict((
            ('Record', {
                'callback': lambda obj: obj.change_panel(0),
                'shortcut': 'Ctrl+1',
            }),
            ('Sleep', {
                'callback': lambda obj: obj.change_panel(1),
                'shortcut': 'Ctrl+2',
            }),
        )),
        'default_selection': 0,
    }

    def _init_layout(self):
        self._init_menu(self.MENU_CONFIG)
        self._init_panels()

    def _create_panels(self):
        return (
            RecordDurationTablePanel(self),
            SleepDurationTablePanel(self),
        )


class DataViewPanel(BaseVBoxPanel, HBoxMenuable, PanelChangeable):
    MENU_CONFIG = {
        'menu': OrderedDict((
            ('RecordGroup', {
                'callback': lambda obj: obj.change_panel(0),
                'shortcut': 'Ctrl+1',
            }),
            ('Sleep', {
                'callback': lambda obj: obj.change_panel(1),
                'shortcut': 'Ctrl+2',
            }),
        )),
        'default_selection': 0,
    }

    def _init_layout(self):
        self._init_menu(self.MENU_CONFIG)
        self._init_panels()

    def _create_panels(self):
        return (
            RecordGroupTablePanel(self),
            SleepTablePanel(self),
        )


if __name__ == "__main__":
    app = QApplication(sys.argv)

    window = MainWindow()
    window.show()

    app.exec_()
