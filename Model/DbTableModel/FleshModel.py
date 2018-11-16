#!/usr/bin/env python
# -*- coding: utf-8 -*-
from collections import OrderedDict
from datetime import timedelta

from Model.DbTableModel.BaseModel import DurationModel, DurationType, Func
from Model import Utility, TimeUtility
from Model.DataAccessor.DbTableAccessor import Timeline, Flesh, DoesNotExist, fn, JOIN


class FleshUtility(object):
    @staticmethod
    def add(date, count):
        if count <= 0:
            raise ValueError("Count should be greater than 0.")

        count_before = FleshUtility.get_count(date)
        count_after = count_before + count
        if count_after > 3:
            raise ValueError("Count will be %d (over 3) in one day." % count_after)

        date_id = Utility.get_or_create_date_id(date)
        Flesh.replace(date=date_id, count=count_after).execute()

        return {
            'day': count_after,
            'week': FleshUtility.get_week_count(date),
            'last_week': FleshUtility.get_week_count(date - timedelta(days=7))}

    @staticmethod
    def get_count(date):
        try:
            timeline = Timeline.select().prefetch(Flesh).where(Timeline.date == date).get()
            return timeline.flesh[0].count
        except (DoesNotExist, IndexError):
            return 0

    @staticmethod
    def get_week_count(date):
        start, end = TimeUtility.get_week_start_and_end(date)
        try:
            record = FleshDurationModel.get_data(DurationType.WEEKLY).where(
                start <= Timeline.date, Timeline.date <= end).get()
        except DoesNotExist:
            return 0
        else:
            return record.count


class FleshDurationModel(DurationModel):
    ACCESSOR = Timeline

    @classmethod
    def get_columns_definition(cls, duration):
        sum_count = fn.SUM(Flesh.count).alias('count')

        if duration is DurationType.DAILY:
            return OrderedDict((
                ('id', Timeline.id),
                ('date', Timeline.date),
                ('count', sum_count),
            ))
        elif duration is DurationType.WEEKLY:
            return OrderedDict((
                ('id', Timeline.id),
                ('monday', Func.week_start(Timeline.date).alias('monday')),
                ('sunday', Func.week_end(Timeline.date).alias('sunday')),
                ('count', sum_count),
            ))
        elif duration is DurationType.MONTHLY:
            return OrderedDict((
                ('id', Timeline.id),
                ('month', Func.month_start(Timeline.date).alias('month')),
                ('count', sum_count),
            ))
        else:
            return super().get_columns_definition(duration)

    @classmethod
    def _select(cls, *args):
        return super()._select(*args).join(Flesh, JOIN.INNER, on=(Timeline.id == Flesh.date))


if __name__ == "__main__":
    pass
