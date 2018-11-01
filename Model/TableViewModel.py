#!/usr/bin/env python
# -*- coding: utf-8 -*-
from PyQt5.QtCore import *
from PyQt5.QtGui import *

from Model.DbTableModel.SleepModel import SleepModel, SleepDurationModel
from Model.DbTableModel.FleshModel import FleshDurationModel
from Model.DbTableModel.RecordModel import RecordGroupModel, GroupRelationModel, RawRecordModel


class ProxyModel(QSortFilterProxyModel):
    def __init__(self, source=None):
        super().__init__()
        self.setSourceModel(SleepTableModel() if source is None else source)


class PeeweeTableModel(QAbstractTableModel):
    def __init__(self, model_data=None, parent=None):
        super(PeeweeTableModel, self).__init__(parent)

        self.column_headers = self.get_column_headers()
        self.get_record_value = self.get_db_model().get_record_attr
        self.model_data = model_data if model_data else self.get_all_model_data()

    @classmethod
    def get_db_model(cls):
        raise NotImplementedError()

    @classmethod
    def get_column_headers(cls):
        return list(cls.get_db_model().get_column_names())

    @classmethod
    def get_all_model_data(cls):
        return list(cls.get_db_model().get_data())

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

    def data_record(self, record, index):
        attr = self.column_headers[index]
        return str(self.get_record_value(record, attr))


class SleepDurationTableModel(PeeweeTableModel):
    @classmethod
    def get_db_model(cls):
        return SleepDurationModel


class SleepTableModel(PeeweeTableModel):
    @classmethod
    def get_db_model(cls):
        return SleepModel

    @classmethod
    def get_column_headers(cls):
        origin = super().get_column_headers()
        return origin[:] + ['duration']


class FleshTableModel(PeeweeTableModel):
    @classmethod
    def get_db_model(cls):
        return FleshDurationModel


class RecordGroupTableModel(PeeweeTableModel):
    @classmethod
    def get_db_model(cls):
        return RecordGroupModel


class GroupRelationTableModel(PeeweeTableModel):
    @classmethod
    def get_db_model(cls):
        return GroupRelationModel


class RecordTableModel(PeeweeTableModel):
    @classmethod
    def get_db_model(cls):
        return RawRecordModel
