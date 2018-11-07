#!/usr/bin/env python
# -*- coding: utf-8 -*-
import datetime
from enum import Enum
from PyQt5.QtCore import *
from PyQt5.QtGui import *

from Model.DbTableModel.BaseModel import DurationType
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


class DateFilter(object):
    class Type(Enum):
        ONE_MONTH = '1 month'
        SIX_MONTH = '6 months'
        TWO_YEAR = '2 years'
        NO = 'no'

    @staticmethod
    def get_date(date_filter):
        if date_filter == DateFilter.Type.NO:
            return datetime.datetime.min.date()
        elif date_filter == DateFilter.Type.ONE_MONTH:
            return datetime.date.today() - datetime.timedelta(days=30)
        elif date_filter == DateFilter.Type.SIX_MONTH:
            return datetime.date.today() - datetime.timedelta(days=183)
        elif date_filter == DateFilter.Type.TWO_YEAR:
            return datetime.date.today() - datetime.timedelta(days=730)
        else:
            raise KeyError


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
        raise NotImplementedError

    @classmethod
    def get_model_data(cls, *args):
        raise NotImplementedError

    def __init__(self):
        if not self.DB_MODEL:
            raise NotImplementedError

        super().__init__()
        self.column_headers = None
        self.model_data = None
        self._init_data()

    def _init_data(self):
        raise NotImplementedError

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
        return list(cls.DB_MODEL.get_column_names())

    @classmethod
    def get_model_data(cls):
        return list(cls.DB_MODEL.get_data())

    def _init_data(self):
        self.column_headers = self.get_column_headers()
        self.model_data = self.get_model_data()


class SleepTableModel(BaseRawTableModel):
    DB_MODEL = SleepModel


class BaseDurationTableModel(BaseTableModel):
    DB_MODEL = None
    DEFAULT_DURATION = DurationType.DAILY

    @classmethod
    def get_column_headers(cls, duration):
        return list(cls.DB_MODEL.get_column_names(duration))

    @classmethod
    def get_model_data(cls, duration):
        return list(cls.DB_MODEL.get_data(duration))

    def _init_data(self):
        self.set_duration(duration=self.DEFAULT_DURATION)

    def set_duration(self, duration):
        self.column_headers = self.get_column_headers(duration)
        self.model_data = self.get_model_data(duration)

    def get_record_date(self, record):
        """
        Assuming date will always be index 1.
        """
        return self.get_record_data(record, 1)


class SleepDurationTableModel(BaseDurationTableModel):
    DB_MODEL = SleepDurationModel


class FleshDurationTableModel(BaseDurationTableModel):
    DB_MODEL = FleshDurationModel
    DEFAULT_DURATION = DurationType.WEEKLY
