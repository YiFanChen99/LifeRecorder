#!/usr/bin/env python
# -*- coding: utf-8 -*-
from PyQt5.QtCore import *
from PyQt5.QtGui import *

from Model.DbTableModel.SleepModel import SleepModel, SleepDateViewModel
from Model.DbTableModel.FleshModel import FleshModel


class FilterModel(QSortFilterProxyModel):
    def __init__(self, source=None, conditions=None):
        super(FilterModel, self).__init__()
        self.setSourceModel(SleepTableModel() if source is None else source)
        self.conditions = conditions


class PeeweeTableModel(QAbstractTableModel):
    def __init__(self, model_data=None, parent=None):
        super(PeeweeTableModel, self).__init__(parent)

        self.column_headers = self.get_column_headers()
        self.model_data = model_data if model_data else self.get_all_model_data()

    @classmethod
    def get_db_model(cls):
        raise NotImplementedError()

    @classmethod
    def get_column_headers(cls):
        return cls.get_db_model().get_column_names()

    @classmethod
    def get_all_model_data(cls):
        return cls.get_db_model().get_data()

    def rowCount(self, *args):
        return len(self.model_data)

    def columnCount(self, *args):
        return len(self.column_headers)

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
                return self.column_headers[index]
            else:
                return index

    def data_record(self, records, index):
        return str(getattr(records, self.column_headers[index]))


class SleepDateViewTableModel(PeeweeTableModel):
    @classmethod
    def get_db_model(cls):
        return SleepDateViewModel


class SleepTableModel(PeeweeTableModel):
    @classmethod
    def get_db_model(cls):
        return SleepModel

    @classmethod
    def get_column_headers(cls):
        headers = super(SleepTableModel, cls).get_column_headers()
        headers.append('duration')
        return headers

    def data_record(self, records, index):
        if index <= 2:  # start, end
            return super(SleepTableModel, self).data_record(records, index)
        else:  # duration
            return str(records.end - records.start)


class FleshTableModel(PeeweeTableModel):
    @classmethod
    def get_db_model(cls):
        return FleshModel


