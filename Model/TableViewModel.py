#!/usr/bin/env python
# -*- coding: utf-8 -*-
from PyQt5.QtCore import *
from PyQt5.QtGui import *

from Model.DbTableModel.BaseModel import DurationType
from Model.DbTableModel.SleepModel import SleepModel, SleepDurationModel
from Model.DbTableModel.FleshModel import FleshDurationModel
from Model.DbTableModel.RecordModel import RecordGroupModel, GroupRelationModel, RecordRawModel
from Model.Utility import DateFilter


class ProxyModel(QSortFilterProxyModel):
    def __init__(self, source=None):
        super().__init__()
        self.setSourceModel(SleepTableModel() if source is None else source)


class FilterProxyModel(QSortFilterProxyModel):
    def __init__(self, duration=DurationType.DAILY, date_filter=DateFilter.Type.NO):
        super().__init__()
        self.duration = duration
        self.date_filter = date_filter
        self.date_started_cache = DateFilter.get_date(date_filter)

    def set_duration(self, duration):
        self.duration = duration

        self.beginResetModel()
        self.sourceModel().set_duration(duration)
        self.endResetModel()

    def set_date_filter(self, date_filter):
        self.date_filter = date_filter
        self.date_started_cache = DateFilter.get_date(date_filter)

        self.beginResetModel()
        self.endResetModel()

    def filterAcceptsRow(self, row, model_index):
        date = self.sourceModel().get_record_date(self.sourceModel().model_data[row])
        return self.date_started_cache <= date

    def filterAcceptsColumn(self, column, model_index):
        return column != 0


class BaseTableModel(QAbstractTableModel):
    DB_MODEL = None

    @classmethod
    def get_column_headers(cls, *args):
        return list(cls.DB_MODEL.get_column_names(*args))

    @classmethod
    def get_model_data(cls, *args):
        return list(cls.DB_MODEL.get_data(*args))

    def __init__(self):
        if not self.DB_MODEL:
            raise NotImplementedError

        super().__init__()
        self._init_data()

    def _init_data(self, *args):
        self.column_headers = self.get_column_headers(*args)
        self.model_data = self.get_model_data(*args)

    def rowCount(self, *args):
        return len(self.model_data)

    def columnCount(self, *args):
        return len(self.column_headers)

    def data(self, q_index, role=None):
        if role == Qt.DisplayRole:
            record = self.model_data[q_index.row()]
            c_index = q_index.column()
            return record.id if c_index == 0 else str(self.get_record_data(record, c_index))
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

    def get_record_data(self, record, index):
        attr = self.column_headers[index]
        return self.DB_MODEL.get_record_attr(record, attr)


class BaseRawTableModel(BaseTableModel):
    DB_MODEL = None

    @classmethod
    def get_column_headers(cls):
        return super().get_column_headers()

    @classmethod
    def get_model_data(cls):
        return super().get_model_data()

    def _init_data(self):
        super()._init_data()


class SleepTableModel(BaseRawTableModel):
    DB_MODEL = SleepModel


class RecordRawTableModel(BaseRawTableModel):
    DB_MODEL = RecordRawModel


class RecordGroupTableModel(BaseRawTableModel):
    DB_MODEL = RecordGroupModel


class GroupRelationTableModel(BaseRawTableModel):
    DB_MODEL = GroupRelationModel


class BaseDurationTableModel(BaseTableModel):
    DB_MODEL = None
    DEFAULT_DURATION = None
    DEFAULT_DATE_FILTER = None

    @classmethod
    def get_column_headers(cls, duration):
        return super().get_column_headers(duration)

    @classmethod
    def get_model_data(cls, duration):
        return super().get_model_data(duration)

    def _init_data(self, duration=None):
        if duration is None:
            duration = self.DEFAULT_DURATION
        super()._init_data(duration)

    def set_duration(self, duration):
        self._init_data(duration)

    def get_record_date(self, record):
        # Assuming date will always be index 1.
        return self.get_record_data(record, 1)


class SleepDurationTableModel(BaseDurationTableModel):
    DB_MODEL = SleepDurationModel
    DEFAULT_DURATION = DurationType.DAILY
    DEFAULT_DATE_FILTER = DateFilter.Type.ONE_MONTH


class FleshDurationTableModel(BaseDurationTableModel):
    DB_MODEL = FleshDurationModel
    DEFAULT_DURATION = DurationType.WEEKLY
    DEFAULT_DATE_FILTER = DateFilter.Type.SIX_MONTH
