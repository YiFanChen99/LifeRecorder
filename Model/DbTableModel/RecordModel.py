#!/usr/bin/env python
# -*- coding: utf-8 -*-
from collections import OrderedDict
from enum import Enum
import datetime
import re
import unittest

from Model.TimeUtility import get_week_start, get_month_start
from Model import Utility
from Model.DbTableModel.BaseModel import BaseModel, DurationType, DurationalColumnModel
from Model.DataAccessor.DbTableAccessor import DoesNotExist
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
        def add(cls, description, parent_id=-1):
            with RecordGroup.atomic() as transaction:
                try:
                    group = RecordGroupModel.create(description=description)
                    if parent_id != -1:
                        cls._add_relation(parent_id, group)
                except ValueError as ex:
                    transaction.rollback()
                    raise ex
            cls.update_cache()
            return group

        @classmethod
        def _add_relation(cls, parent_id, child_group):
            GroupRelation.create(parent=parent_id, child=child_group)

    class Basic:
        @staticmethod
        def create(date, group_id):
            date_id = Utility.get_or_create_date_id(date)
            return BasicRecord.create(date_id=date_id, group_id=group_id)

        @staticmethod
        def create_with_extras(date, group_id, extras):
            with RecordGroup.atomic() as txn:
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
        def _dictionarize_extra(extras):
            # init dict_
            dict_ = {
                ExtraRecordType.DESCRIPTION: [],
                ExtraRecordType.MAGNITUDE: 0,
                ExtraRecordType.SCALE: 1,
                ExtraRecordType.TIME: 0,
                ExtraRecordType.DISTANCE: 0
            }

            # apply extras
            for extra in extras:
                type_ = ExtraRecordType.from_value(extra.key)
                if type_ == ExtraRecordType.DESCRIPTION:
                    dict_[type_].append(extra.value)
                else:
                    dict_[type_] = extra.value
            return dict_

        def __init__(self, group):
            super().__init__()
            self.group = group
            self.description_groups = []

        def add(self, extras):
            extra_dict = self._dictionarize_extra(extras)
            extra = _Summarizer.DescriptionSummarizer(extra_dict)

            try:
                matched = next(filter(lambda old: old == extra, self.description_groups))
                matched += extra
            except StopIteration:
                self.description_groups.append(extra)

        def __repr__(self):
            return '.  '.join(str(each) for each in self.description_groups)

    class DescriptionSummarizer(object):
        def __init__(self, extra_dict):
            super().__init__()

            self.times = 0
            self.descriptions = extra_dict[ExtraRecordType.DESCRIPTION]

            magnitude = float(extra_dict[ExtraRecordType.MAGNITUDE])
            scale = float(extra_dict[ExtraRecordType.SCALE])
            volume = magnitude * scale
            self.volume = volume

            self.others = {}
            for type_ in (ExtraRecordType.DISTANCE, ExtraRecordType.TIME):
                self.others[type_] = float(extra_dict[type_])

            self.time()

        def __eq__(self, other):
            if len(self.descriptions) != len(other.descriptions):
                return False
            return all((desc_ in other.descriptions for desc_ in self.descriptions))

        def __ne__(self, other):
            return not self.__eq__(other)

        def __iadd__(self, other):
            self.volume += other.volume
            self.times += other.times
            for key in self.others.keys():
                self.others[key] += other.others[key]
            return self

        def time(self):
            if self.volume == 0 and not any(self.others.values()):
                self.times += 1

        def __str__(self):
            if self.volume > 0 and self.times > 0:
                count = "(%.1f+%d)" % (self.volume, self.times)
            elif self.volume > 0:
                count = "%.1f" % self.volume
            elif any(self.others.values()):
                count = ", ".join(["{0}{1}".format(type_.value[0:3], value)
                                  for type_, value in self.others.items() if value > 0])
            else:  # self.times > 0
                count = "%d" % self.times

            if self.descriptions:
                return count + "*" + repr(self.descriptions)
            else:
                return count


class ExtraRecordType(Enum):
    DESCRIPTION = 'description'
    MAGNITUDE = 'magnitude'
    SCALE = 'scale'
    TIME = 'time'
    DISTANCE = 'distance'

    @staticmethod
    def from_value(value):
        for type_ in ExtraRecordType:
            if value == type_.value:
                return type_
        raise KeyError


class _DescriptionSummarizerTest(unittest.TestCase):
    @staticmethod
    def create_description_summarizer(desc, magn=0, scal=1):
        return _Summarizer.DescriptionSummarizer({
            ExtraRecordType.DESCRIPTION: desc,
            ExtraRecordType.MAGNITUDE: magn,
            ExtraRecordType.SCALE: scal
        })

    def test_equality(self):
        obj_99_1 = self.create_description_summarizer(['99'], scal=1)
        self.assertTrue(obj_99_1 == obj_99_1)

        obj_99_5 = self.create_description_summarizer(['99'], scal=5)
        self.assertTrue(obj_99_1 == obj_99_5)

        obj_99_k_2 = self.create_description_summarizer(['99', 'k'], magn=2)
        self.assertFalse(obj_99_1 == obj_99_k_2)

        obj_k_99_4 = self.create_description_summarizer(['k', '99'], magn=4)
        self.assertFalse(obj_99_k_2 != obj_k_99_4)

    def test_addition(self):
        obj_99_v0 = self.create_description_summarizer(['99'])
        self.assertEqual(0, obj_99_v0.volume)
        self.assertEqual(1, obj_99_v0.times)
        obj_99_k_v0 = self.create_description_summarizer(['99', 'k'])
        self.assertEqual(0, obj_99_k_v0.volume)
        self.assertEqual(1, obj_99_k_v0.times)

        obj_99_v0 += obj_99_k_v0
        self.assertEqual(0, obj_99_v0.volume)
        self.assertEqual(2, obj_99_v0.times)

        obj_99_k_v3 = self.create_description_summarizer(['99', 'k'], magn=3)
        self.assertEqual(3, obj_99_k_v3.volume)
        self.assertEqual(0, obj_99_k_v3.times)

        obj_99_v0 += obj_99_k_v3
        self.assertEqual(3, obj_99_v0.volume)
        self.assertEqual(2, obj_99_v0.times)


if __name__ == "__main__":
    unittest.main()
