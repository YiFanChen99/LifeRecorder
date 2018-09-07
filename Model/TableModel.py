#!/usr/bin/env python
# -*- coding: utf-8 -*-
from PyQt5.QtCore import *
from PyQt5.QtGui import *

from ModelUtility.DataAccessor.DbTableAccessor import Sleep


class FilterModel(QSortFilterProxyModel):
    def __init__(self, source=None, conditions=None):
        super(FilterModel, self).__init__()
        self.setSourceModel(SleepTableModel() if source is None else source)
        self.conditions = conditions


class PeeweeTableModel(QAbstractTableModel):
    table_name = ""
    column_names = []

    def __init__(self, model_data, parent=None):
        super(PeeweeTableModel, self).__init__(parent)
        self.model_data = model_data

    def rowCount(self, *args):
        return len(self.model_data)

    def columnCount(self, *args):
        return len(self.column_names)

    def data(self, q_index, role=None):
        if role == Qt.DisplayRole:
            record = self.model_data[q_index.row()]
            c_index = q_index.column()
            return record.id if c_index == 0 else self.data_record(record, c_index)
        if role == Qt.BackgroundRole:
            return QBrush(Qt.darkGray)
        if role == Qt.TextColorRole:
            return QBrush(QColor(QVariant("#b0d4b0")))

    def headerData(self, index, orientation, role=None):
        if role == Qt.DisplayRole:
            if orientation == Qt.Horizontal:
                return self.column_names[index]
            else:
                return index

    def data_record(self, records, index):
        raise NotImplementedError()


class SleepTableModel(PeeweeTableModel):
    table_name = "Sleep"
    column_names = Sleep.get_column_names()

    def __init__(self, model_data=None, parent=None):
        if model_data is None:
            model_data = list(Sleep.select())

        super(SleepTableModel, self).__init__(model_data, parent)

    def data_record(self, records, index):
        return str(getattr(records, self.column_names[index]))
