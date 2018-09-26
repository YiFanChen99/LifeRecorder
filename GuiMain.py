#!/usr/bin/env python
# -*- coding: utf-8 -*-
import sys

from Ui.SleepWindow import SleepAdderWindow
from Ui.FleshWindow import FleshAdderWindow
from Ui.MainMenu import MainMenu
from Ui.Utility.Window import *
from Model.TableViewModel import FilterModel
from ModelUtility.DataAccessor.Configure import config


class MainWindow(BaseMainWindow):
    def __init__(self):
        super(MainWindow, self).__init__()

        config_w = config['window']
        self.resize(config_w['width'], config_w['height'])
        self.move(config_w['x_axis'], config_w['y_axis'])
        self.setWindowTitle(config_w['title'])

    def _init_layout(self):
        self._init_menu()
        self._init_adder()
        self._init_table_view()
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

        flesh_btn = QPushButton("&Flesh")
        layout.addWidget(flesh_btn)
        flesh_btn.setSizePolicy(QSizePolicy.Minimum, QSizePolicy.Minimum)
        flesh_btn.clicked.connect(FleshAdderWindow(self).show)

        sleep_btn = QPushButton("&Sleep")
        layout.addWidget(sleep_btn)
        sleep_btn.setSizePolicy(QSizePolicy.Minimum, QSizePolicy.Minimum)
        sleep_btn.clicked.connect(SleepAdderWindow(self).show)

    def _init_table_view(self):
        self.table_view = QTableView()
        table_view = self.table_view
        self.central_layout.addWidget(table_view)

        self.table_model = FilterModel()
        table_view.setModel(self.table_model)
        table_view.resizeColumnsToContents()
        table_view.setSortingEnabled(True)
        table_view.setSelectionBehavior(QAbstractItemView.SelectRows)
        table_view.setSelectionMode(QAbstractItemView.SingleSelection)
        table_view.setColumnHidden(0, True)

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


if __name__ == "__main__":
    app = QApplication(sys.argv)

    window = MainWindow()
    window.show()

    app.exec_()
