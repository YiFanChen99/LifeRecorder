#!/usr/bin/env python
# -*- coding: utf-8 -*-
from collections import OrderedDict

from Model.DbTableModel.BaseModel import DurationModel, DurationType, Func
from Model import Utility
from Model.DataAccessor.DbTableAccessor import Timeline, Flesh, DoesNotExist, fn, JOIN


class FleshUtility(object):
    @staticmethod
    def add(date, count):
        if count <= 0:
            raise ValueError("Count should be greater than 0.")
        count_before = FleshUtility.get_count(date)
        count_after = count_before + count
        if count_after > 2:
            raise ValueError("Count will be %d (over 2)." % count_after)

        date_id = Utility.get_or_create_date_id(date)
        Flesh.replace(date=date_id, count=count_after).execute()

        return count_after

    @staticmethod
    def get_count(date):
        try:
            timeline = Timeline.select().prefetch(Flesh).where(Timeline.date == date).get()
            return timeline.flesh[0].count
        except (DoesNotExist, IndexError):
            return 0


class FleshDurationModel(DurationModel):
    ACCESSOR = Timeline

    @classmethod
    def _get_columns(cls, duration):
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
                ('week', Func.week_start(Timeline.date).alias('week')),
                ('count', sum_count),
            ))
        elif duration is DurationType.MONTHLY:
            return OrderedDict((
                ('id', Timeline.id),
                ('month', Func.month_start(Timeline.date).alias('month')),
                ('count', sum_count),
            ))
        else:
            return super()._get_columns(duration)

    @classmethod
    def _select(cls, *args):
        return Timeline.select(*args).join(Flesh, JOIN.INNER, on=(Timeline.id == Flesh.date))


if __name__ == "__main__":
    pass
