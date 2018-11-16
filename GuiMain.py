#!/usr/bin/env python
# -*- coding: utf-8 -*-
import sys
from collections import OrderedDict

from Ui.RecordWindow import RecordAdderWindow
from Ui.MainMenu import MainMenu
from Ui.MainPanel import *
from Ui.Utility.Panel import *
from Ui.Utility.Window import *
from Model.DataAccessor.Configure import config


class MainWindow(BaseMainWindow):
    def __init__(self):
        super(MainWindow, self).__init__()

        config_w = config['window']
        self.resize(config_w['width'], config_w['height'])
        self.move(config_w['x_axis'] - 15, config_w['y_axis'] - 15)
        self.setWindowTitle(config_w['title'])

        self.new_window = MainWindowV2(self)

    def _init_layout(self):
        self._init_menu()
        self._init_adder()
        self._init_main_panel()
        self._init_footer()

        self.main_menu.trigger_default()

    def _init_menu(self):
        self.main_menu = MainMenu(self)

        self.central_layout.addWidget(self.main_menu.level_1_menu)
        for level_2_menu in self.main_menu.level_2_menus.values():
            self.central_layout.addWidget(level_2_menu)

    def _init_adder(self):
        self.record_adder_box = QGroupBox("Record Adder")
        record_adder_box = self.record_adder_box
        self.central_layout.addWidget(record_adder_box)

        layout = QHBoxLayout()
        record_adder_box.setLayout(layout)

        record_btn = QPushButton("&Record")
        layout.addWidget(record_btn)
        record_btn.setSizePolicy(QSizePolicy.Minimum, QSizePolicy.Minimum)
        record_btn.clicked.connect(RecordAdderWindow(self).show)

    def _create_main_panel(self):
        return MainPanel(self)

    def _init_footer(self):
        self.add_h_line()

        self.footer_box = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)

        footer_box = self.footer_box
        self.central_layout.addWidget(footer_box)

        footer_box.accepted.connect(self.accept)
        footer_box.rejected.connect(self.reject)

    def accept(self):
        self.close()

    def reject(self):
        self.close()

    def _show_new_window(self):
        return self.new_window.show()


class MainPanel(QWidget):
    def __init__(self, owner):
        super().__init__()
        self.owner = owner
        self._init_layout()

    def _init_layout(self):
        layout = QVBoxLayout()
        self.setLayout(layout)

        self._init_table_view()

    def _init_table_view(self):
        table_view = QTableView()
        self.table_view = table_view
        self.layout().addWidget(table_view)

        self.table_model = ProxyModel()
        table_view.setModel(self.table_model)

        table_view.resizeColumnsToContents()
        table_view.setSortingEnabled(True)
        table_view.setSelectionBehavior(QAbstractItemView.SelectRows)
        table_view.setSelectionMode(QAbstractItemView.SingleSelection)
        table_view.setColumnHidden(0, True)


class MainWindowV2(BaseMainWindow, BaseConfigLoader):
    def __init__(self, parent=None):
        super().__init__(parent)
        self._init_window(config['window'])

    def _create_main_panel(self):
        return MainPanelV2(self)


class MainPanelV2(BaseVBoxPanel, HBoxMenuable, PanelChangeable):
    MENU_CONFIG = {
        'menu': OrderedDict((
            ('Timeline', {
                'callback': lambda obj: obj.change_panel(0),
                'shortcut': 'F1',
            }),
            ('RawTable', {
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
            RawTablePanel(self),
        )


class TimelinePanel(BaseVBoxPanel, HBoxMenuable, PanelChangeable):
    MENU_CONFIG = {
        'menu': OrderedDict((
            ('Sleep', {
                'callback': lambda obj: obj.change_panel(0),
                'shortcut': 'Ctrl+1',
            }),
            ('Flesh', {
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
            SleepDurationTablePanel(self),
            FleshDurationTablePanel(self),
        )


class RawTablePanel(BaseVBoxPanel, HBoxMenuable, PanelChangeable):
    MENU_CONFIG = {
        'menu': OrderedDict((
            ('RecordGroup', {
                'callback': lambda obj: obj.change_panel(0),
                'shortcut': 'Ctrl+1',
            }),
            ('GroupRelation', {
                'callback': lambda obj: obj.change_panel(1),
                'shortcut': 'Ctrl+2',
            }),
            ('Sleep', {
                'callback': lambda obj: obj.change_panel(2),
                'shortcut': 'Ctrl+3',
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
            GroupRelationTablePanel(self),
            SleepTablePanel(self),
        )


if __name__ == "__main__":
    app = QApplication(sys.argv)

    window = MainWindow()
    window.show()

    app.exec_()
