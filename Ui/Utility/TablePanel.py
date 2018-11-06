#!/usr/bin/env python
# -*- coding: utf-8 -*-
from PyQt5.QtWidgets import *
from Ui.Utility.Widget import DurationGroup, DateFilterComBox
from Model.TableViewModel import FilterProxyModel


class DurationTablePanel(QWidget):
    def __init__(self, owner, source_model, adder_callback=None):
        super().__init__()
        self.owner = owner
        self.adder_callback = adder_callback
        self._init_layout()

        self.set_source_model(source_model)

    def set_source_model(self, source_model):
        self.table_model.beginResetModel()
        self.table_model.setSourceModel(source_model)
        self.table_model.endResetModel()

    def _init_layout(self):
        layout = QVBoxLayout()
        self.setLayout(layout)

        self._init_menu_bar()
        self._init_table_view()

    def _init_menu_bar(self):
        self.menu_bar = QHBoxLayout()
        self.layout().addLayout(self.menu_bar)

        self.add_btn = QPushButton("&Add")
        if callable(self.adder_callback):
            self.add_btn.clicked.connect(self.adder_callback)
        else:
            self.add_btn.setEnabled(False)
        self.menu_bar.addWidget(self.add_btn, 1)

        self.duration_group = DurationGroup(self.set_duration)
        self.menu_bar.addWidget(self.duration_group, 7)

        self.date_filter = DateFilterComBox(self.set_date_filter)
        self.menu_bar.addWidget(self.date_filter, 2)

    def set_duration(self, duration):
        self.table_model.set_duration(duration)

    def set_date_filter(self, d_filter):
        self.table_model.set_date_filter(d_filter)

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
