#!/usr/bin/env python
# -*- coding: utf-8 -*-
from PyQt5.QtWidgets import *
from Ui.SleepWindow import SleepAdderWindow
from Ui.FleshWindow import FleshAdderWindow
from Ui.Utility.Widget import DurationGroup, DateFilterComBox
from Model.TableViewModel import FilterProxyModel, SleepDurationTableModel, FleshDurationTableModel


class DurationTablePanel(QWidget):
    SOURCE_MODEL = None

    def __init__(self, owner):
        if self.SOURCE_MODEL is None:
            raise ValueError("SOURCE_MODEL")

        super().__init__()
        self.owner = owner
        self._init_layout()

        self.init_source_model()

    def init_source_model(self):
        self.table_model.beginResetModel()
        self.table_model.setSourceModel(self.SOURCE_MODEL)
        self.table_model.endResetModel()

        self.set_date_filter(self.SOURCE_MODEL.DEFAULT_DATE_FILTER)

    def _init_layout(self):
        layout = QVBoxLayout()
        self.setLayout(layout)

        self._init_menu_bar()
        self._init_table_view()

    def _init_menu_bar(self):
        self.menu_bar = QHBoxLayout()
        self.layout().addLayout(self.menu_bar)

        self.add_btn = QPushButton("&Add")
        try:
            callback = self.get_adder_callback()
            self.add_btn.clicked.connect(callback)
        except NotImplementedError:
            self.add_btn.setEnabled(False)
        self.menu_bar.addWidget(self.add_btn, 1)

        self.duration_group = DurationGroup(
            self.set_duration, default_checked=self.SOURCE_MODEL.DEFAULT_DURATION)
        self.menu_bar.addWidget(self.duration_group, 7)

        self.date_filter = DateFilterComBox(
            self.set_date_filter, default_index=self.SOURCE_MODEL.DEFAULT_DATE_FILTER)
        self.menu_bar.addWidget(self.date_filter, 2)

    def set_duration(self, duration):
        self.table_model.set_duration(duration)

    def set_date_filter(self, d_filter):
        self.table_model.set_date_filter(d_filter)

    def get_adder_callback(self):
        raise NotImplementedError

    def _init_table_view(self):
        table_view = QTableView()
        self.table_view = table_view
        self.layout().addWidget(table_view)

        self.table_model = FilterProxyModel()
        table_view.setModel(self.table_model)

        table_view.resizeColumnsToContents()
        table_view.setSortingEnabled(True)
        table_view.setSelectionBehavior(QAbstractItemView.SelectRows)
        table_view.setSelectionMode(QAbstractItemView.SingleSelection)


class SleepDurationTablePanel(DurationTablePanel):
    SOURCE_MODEL = SleepDurationTableModel()

    def get_adder_callback(self):
        return SleepAdderWindow(self.owner).show


class FleshDurationTablePanel(DurationTablePanel):
    SOURCE_MODEL = FleshDurationTableModel()

    def get_adder_callback(self):
        return FleshAdderWindow(self.owner).show
