#!/usr/bin/env python
# -*- coding: utf-8 -*-
from collections import OrderedDict
from enum import Enum
import datetime
import re

from Model.TimeUtility import get_week_start, get_month_start
from Model import Utility
from Model.DbTableModel.BaseModel import BaseModel, DurationType, DurationalColumnModel
from Model.DataAccessor.DbTableAccessor import atomic, create, DoesNotExist
from Model.DataAccessor.DbTableAccessor import RecordGroup, GroupRelation, BasicRecord, ExtraRecord, Timeline
from Model.DataAccessor.Configure import group_alias_rules


class RecordUtility(object):
    class Group(object):
        # cache, should be updated on DB changed
        _record_groups = {group.id: group for group in RecordGroup.select()}

        @classmethod
        def update_cache(cls):
            cls._record_groups = {group.id: group for group in RecordGroup.select()}

        @classmethod
        def get_description(cls):
            return map(lambda record: record.description, cls._record_groups.values())

        @classmethod
        def get_id_description_map(cls):
            return OrderedDict((id_, record.description)
                               for id_, record in cls._record_groups.items())

        @classmethod
        def get_id_by_description(cls, description):
            try:
                return next((id_ for id_, record in cls._record_groups.items()
                             if record.description == description))
            except StopIteration:
                raise KeyError(description)

        @classmethod
        def get_parent(cls, current_id):
            return cls._record_groups[current_id].parent

        @classmethod
        def add(cls, description, countable, parent_id=-1):
            with atomic() as transaction:
                try:
                    group = RecordGroupModel.create(
                        description=description, countable=countable)
                    if parent_id != -1:
                        cls._add_relation(parent_id, group)
                except ValueError as ex:
                    transaction.rollback()
                    raise ex
            cls.update_cache()
            return group

        @classmethod
        def _add_relation(cls, parent_id, child_group):
            create(GroupRelation, parent=parent_id, child=child_group)

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
                    return basic_id
                except ValueError as ex:
                    txn.rollback()
                    raise ex

    class Extra:
        @classmethod
        def create(cls, basic_id, key, value):
            try:
                basic = BasicRecord.get_by_id(basic_id)
            except DoesNotExist:
                raise ValueError('Basic id %d' % basic_id)

            if not isinstance(key, ExtraRecordType):
                raise TypeError('key: ', key)

            value = value.strip()
            if key is ExtraRecordType.DESCRIPTION:
                value = cls._rephrase_alias(basic.group_id_id, value)
            return ExtraRecord.create(basic_id=basic_id, key=key.value, value=value)

        @staticmethod
        def _rephrase_alias(group_id, description):
            result = description

            # rephrase by my rules
            for name, rules in group_alias_rules[group_id].items():
                pattern = re.compile("|".join(rules), flags=re.IGNORECASE)
                result = pattern.sub(name, result)

            try:
                # rephrase by ancestors's rules
                parent_id = RecordUtility.Group.get_parent(group_id).id
                return RecordUtility.Extra._rephrase_alias(parent_id, result)
            except AttributeError:
                return result


class RecordGroupModel(BaseModel):
    ACCESSOR = RecordGroup

    @classmethod
    def get_column_names(cls):
        return ['id', 'description', 'children', 'parent']

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
        columns.extend(RecordUtility.Group.get_description())
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
        def _create_default_extra(group):
            dict_ = {
                ExtraRecordType.DESCRIPTION: [],
                ExtraRecordType.MAGNITUDE: 0,
                ExtraRecordType.SCALE: 1
            }
            if group.countable:
                dict_[ExtraRecordType.MAGNITUDE] = 1
            return dict_

        def __init__(self, group):
            super().__init__()
            self.group = group
            self.volume = 0
            self.descriptions = []

        def add(self, extras):
            extra = self._dictionarize_extra(extras)
            self._add_description(extra)
            self._add_volume(extra)

        def _dictionarize_extra(self, extras):
            # init dict_
            dict_ = self._create_default_extra(self.group)

            # apply extras
            for extra in extras:
                type_ = ExtraRecordType.from_value(extra.key)
                if type_ == ExtraRecordType.DESCRIPTION:
                    dict_[type_].append(extra.value)
                else:
                    dict_[type_] = extra.value
            return dict_

        def _add_description(self, extra):
            self.descriptions.extend(extra[ExtraRecordType.DESCRIPTION])

        def _add_volume(self, extra):
            magnitude = float(extra[ExtraRecordType.MAGNITUDE])
            scale = float(extra[ExtraRecordType.SCALE])
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
