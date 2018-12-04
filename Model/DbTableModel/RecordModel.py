#!/usr/bin/env python
# -*- coding: utf-8 -*-
from collections import OrderedDict
from enum import Enum
import datetime

from Model.TimeUtility import get_week_start, get_month_start
from Model import Utility
from Model.DbTableModel.BaseModel import BaseModel, DurationType, DurationalColumnModel
from Model.DataAccessor.DbTableAccessor import atomic, DoesNotExist
from Model.DataAccessor.DbTableAccessor import RecordGroup, BasicRecord, ExtraRecord, Timeline


class RecordUtility(object):
    class Group(object):
        @staticmethod
        def get_id_description_map():
            return OrderedDict((group.id, group.description) for group in RecordGroup.select())

        @staticmethod
        def get_id_by_description(description):
            try:
                return next((group.id for group in RecordGroup.select() if group.description == description))
            except StopIteration:
                raise KeyError(description)

    class Basic:
        @staticmethod
        def create(date, group_id):
            date_id = Utility.get_or_create_date_id(date)
            return BasicRecord.create(date_id=date_id, group_id=group_id)

        @staticmethod
        def create_with_extras(date, group_id, extras):
            with atomic() as txn:
                try:
                    basic_id = RecordUtility.Basic.create(date, group_id)
                    for extra in extras:
                        RecordUtility.Extra.create(basic_id, extra[0], extra[1])
                except ValueError as ex:
                    txn.rollback()
                    raise ex

        @staticmethod
        def get_count(date, group_id):
            try:
                date_id = Utility.get_or_create_date_id(date)
                return BasicRecord.select().where(BasicRecord.date_id == date_id,
                                                  BasicRecord.group_id == group_id).count()
            except (DoesNotExist, IndexError):
                return 0

    class Extra:
        @staticmethod
        def create(basic_id, key, value):
            try:
                BasicRecord.get_by_id(basic_id)
            except DoesNotExist:
                raise ValueError('Basic id %d' % basic_id)

            if not isinstance(key, ExtraRecordType):
                raise TypeError('key: ', key)

            return ExtraRecord.create(basic_id=basic_id, key=key.value, value=value)


class RecordGroupModel(BaseModel):
    ACCESSOR = RecordGroup

    @classmethod
    def get_column_names(cls):
        return ['id', 'description', 'children', 'parents']

    @classmethod
    def get_data(cls, *args):
        return super().get_data(*args).order_by(RecordGroup.id)


class RecordDurationModel(DurationalColumnModel):
    ACCESSOR = Timeline

    @classmethod
    def get_column_names(cls, duration):
        if duration is DurationType.DAILY:
            columns = ['date']
        elif duration is DurationType.WEEKLY:
            columns = ['monday', 'sunday']
        elif duration is DurationType.MONTHLY:
            columns = ['month']
        else:
            raise KeyError
        columns.extend(RecordUtility.Group.get_id_description_map().values())
        return columns

    @classmethod
    def get_data(cls, duration):
        raw_data = cls._get_data_with_record()
        return _Summarizer.summarize(duration, raw_data)

    @classmethod
    def _get_data_with_record(cls):
        timeline = cls._select()
        return (datum for datum in timeline if (len(datum.record) > 0))

    @classmethod
    def get_record_attr(cls, record, attr):
        if attr == 'date' or attr == 'monday' or attr == 'month':
            return record.date
        elif attr == 'sunday':
            return record.date + datetime.timedelta(days=6)
        else:  # delegate to record(DateSummarizer) itself
            return getattr(record, attr)


class _Summarizer(object):
    @staticmethod
    def summarize(duration, timelines):
        if duration is DurationType.DAILY:
            return _Summarizer.DailySummarizer(timelines)
        elif duration is DurationType.WEEKLY:
            return _Summarizer.WeeklySummarizer(timelines)
        elif duration is DurationType.MONTHLY:
            return _Summarizer.MonthlySummarizer(timelines)
        else:
            raise KeyError

    class BaseDurationSummarizer(dict):
        def __init__(self, timelines):
            super().__init__()
            self.summarize(timelines)

        def __missing__(self, date):
            self[date] = _Summarizer.DateSummarizer(date)
            return self[date]

        def __iter__(self):
            return iter(self.values())

        def summarize(self, timelines):
            for timeline in timelines:
                self.summarize_date(timeline.date, timeline.record)

        def summarize_date(self, date, records):
            for record in records:
                self[date].add(record)

    class DailySummarizer(BaseDurationSummarizer):
        pass

    class WeeklySummarizer(BaseDurationSummarizer):
        def __getitem__(self, date):
            date = get_week_start(date)
            return super().__getitem__(date)

    class MonthlySummarizer(BaseDurationSummarizer):
        def __getitem__(self, date):
            date = get_month_start(date)
            return super().__getitem__(date)

    class DateSummarizer(dict):
        def __init__(self, date):
            super().__init__()
            self.date = date

        def __missing__(self, group):
            if group.id not in self:
                self[group.id] = _Summarizer.GroupSummarizer(group)
            return self[group.id]

        def add(self, record):
            self[record.group_id].add(record.extra)

        def __getattr__(self, attr):
            try:
                group_id = RecordUtility.Group.get_id_by_description(attr)
                return self[group_id]
            except AttributeError:
                return None

    class GroupSummarizer(object):
        @staticmethod
        def dictionarize_extra(extras):
            return {ExtraRecordType.from_value(extra.key): extra.value for extra in extras}

        def __init__(self, group):
            super().__init__()
            self._init_group_and_default_value(group)
            self.volume = 0
            self.descriptions = []

        def _init_group_and_default_value(self, group):
            self.group = group
            self._default_magnitude = 0
            self._default_scale = 1

            if self.group.countable:
                self._default_magnitude = 1

        def add(self, extras):
            extra = self.dictionarize_extra(extras)
            self.add_description(extra)
            self.add_volume(extra)

        def add_description(self, extra):
            if ExtraRecordType.DESCRIPTION in extra:
                self.descriptions.append(extra[ExtraRecordType.DESCRIPTION])

        def add_volume(self, extra):
            magnitude = float(extra.get(ExtraRecordType.MAGNITUDE, self._default_magnitude))
            scale = float(extra.get(ExtraRecordType.SCALE, self._default_scale))
            self.volume += magnitude * scale

        def __repr__(self):
            repr_ = []
            if self.volume > 0:
                repr_.append("%.1f" % self.volume)
            if self.descriptions:
                repr_.append(', '.join(self.descriptions))
            return '. '.join(repr_)


class ExtraRecordType(Enum):
    DESCRIPTION = 'description'
    MAGNITUDE = 'magnitude'
    SCALE = 'scale'

    @staticmethod
    def from_value(value):
        for type_ in ExtraRecordType:
            if value == type_.value:
                return type_
        raise KeyError


if __name__ == "__main__":
    pass
