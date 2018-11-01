#!/usr/bin/env python
# -*- coding: utf-8 -*-
import datetime
from collections import OrderedDict

from Model.DbTableModel.BaseModel import BaseModel, DurationModel, DurationType, Func
from Model import TimeUtility, Utility
from Model.DataAccessor.DbTableAccessor import Sleep, SleepDateView, DoesNotExist, fn


class SleepUtility(object):
    @staticmethod
    def _create_with_feedback(start, end):
        date_belonged = SleepUtility.get_date_belonged(end)
        duration_before = SleepUtility.get_duration(date_belonged)

        Utility.init_timeline_on_date(date_belonged)
        SleepModel.create(start=start, end=end)

        duration_after = SleepUtility.get_duration(date_belonged)
        duration_growth = duration_after - duration_before
        return {'date': date_belonged, 'after': duration_after, 'growth': duration_growth}

    @staticmethod
    def create_by_datetime(start, end):
        if start >= end:
            raise ValueError("End should be later than start.")
        elif (end - start) >= datetime.timedelta(days=1):
            raise ValueError("Sleep over 24 hours.")

        return SleepUtility._create_with_feedback(start, end)

    @staticmethod
    def create_by_date(date, time_start, time_end):
        if time_start > time_end:
            time_end += datetime.timedelta(days=1)
        elif time_start == time_end:
            raise ValueError("Start is equal to end.")
        start = datetime.datetime.combine(date, TimeUtility.covert_timedelta_to_time(time_start))
        end = datetime.datetime.combine(date, TimeUtility.covert_timedelta_to_time(time_end))

        return SleepUtility._create_with_feedback(start=start, end=end)

    @staticmethod
    def get_date_belonged(the_datetime):
        return (the_datetime - datetime.timedelta(hours=17)).date()

    @staticmethod
    def get_duration(date):
        try:
            duration = SleepDateView.select().where(SleepDateView.date == date).get().duration
            return datetime.timedelta(hours=duration.hour, minutes=duration.minute)
        except DoesNotExist:
            return datetime.timedelta()


class SleepModel(BaseModel):
    ACCESSOR = Sleep

    @classmethod
    def get_column_names(cls):
        """
        >>> SleepModel.get_column_names()
        ['id', 'start', 'end']
        """
        return super()._default_columns()

    @classmethod
    def get_record_attr(cls, record, attr):
        if attr == 'duration':
            return record.end - record.start
        else:  # default
            return super().get_record_attr(record, attr)


class SleepDurationModel(DurationModel):
    ACCESSOR = SleepDateView

    @classmethod
    def _get_columns(cls, duration):
        avg_duration = Func.time(fn.AVG(fn.STRFTIME("%s", SleepDateView.duration))).alias('duration')

        if duration is DurationType.WEEKLY:
            return OrderedDict((
                ('id', SleepDateView.id),
                ('week', Func.week_start(SleepDateView.date).alias('week')),
                ('duration', avg_duration),
                ('min', Func.time(fn.MIN(fn.STRFTIME("%s", SleepDateView.duration))).alias('min')),
            ))
        elif duration is DurationType.MONTHLY:
            return OrderedDict((
                ('id', SleepDateView.id),
                ('month', Func.month_start(SleepDateView.date).alias('month')),
                ('duration', avg_duration),
            ))
        else:
            """ names for DurationType.Day: ['id', 'date', 'duration', 'count'] """
            return super()._get_columns(duration)


if __name__ == "__main__":
    import doctest
    doctest.testmod(report=True)
