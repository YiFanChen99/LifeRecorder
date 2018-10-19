#!/usr/bin/env python
# -*- coding: utf-8 -*-
import datetime

from Model.DbTableModel.BaseModel import BaseModel, SimpleModel
from Model import TimeUtility, Utility
from Model.DataAccessor.DbTableAccessor import Sleep, SleepDateView, DoesNotExist, fn


class SleepModel(SimpleModel):
    @classmethod
    def get_accessor(cls):
        return Sleep

    @classmethod
    def get_column_names(cls):
        """
        >>> SleepModel.get_column_names()
        ['id', 'start', 'end']
        """
        return super().get_column_names()

    @classmethod
    def get_record_value(cls, record, attr):
        if attr == 'duration':
            return record.end - record.start
        else:  # default
            return super().get_record_value(record, attr)

    @staticmethod
    def _create_with_feedback(start, end):
        date_belonged = SleepModel.get_date_belonged(end)
        duration_before = SleepDateViewModel.get_duration(date_belonged)

        Utility.init_timeline_on_date(date_belonged)
        SleepModel.create(start=start, end=end)

        duration_after = SleepDateViewModel.get_duration(date_belonged)
        duration_growth = duration_after - duration_before
        return {'date': date_belonged, 'after': duration_after, 'growth': duration_growth}

    @staticmethod
    def create_by_datetime(start, end):
        if start >= end:
            raise ValueError("End should be later than start.")
        elif (end - start) >= datetime.timedelta(days=1):
            raise ValueError("Sleep over 24 hours.")

        return SleepModel._create_with_feedback(start, end)

    @staticmethod
    def create_by_date(date, time_start, time_end):
        if time_start > time_end:
            time_end += datetime.timedelta(days=1)
        elif time_start == time_end:
            raise ValueError("Start is equal to end.")
        start = datetime.datetime.combine(date, TimeUtility.covert_timedelta_to_time(time_start))
        end = datetime.datetime.combine(date, TimeUtility.covert_timedelta_to_time(time_end))

        return SleepModel._create_with_feedback(start=start, end=end)

    @staticmethod
    def get_date_belonged(the_datetime):
        return (the_datetime - datetime.timedelta(hours=17)).date()


class SleepDateViewModel(SimpleModel):
    @classmethod
    def get_accessor(cls):
        return SleepDateView

    @classmethod
    def get_column_names(cls):
        """
        >>> SleepDateViewModel.get_column_names()
        ['id', 'date', 'duration', 'count']
        """
        return super().get_column_names()

    @staticmethod
    def get_duration(date):
        try:
            duration = SleepDateView.select().where(SleepDateView.date == date).get().duration
            return datetime.timedelta(hours=duration.hour, minutes=duration.minute)
        except DoesNotExist:
            return datetime.timedelta()


class SleepDurationModel(BaseModel):
    @classmethod
    def get_column_names(cls):
        raise NotImplementedError

    @classmethod
    def get_data(cls):
        return list(SleepDateView.select(*cls._get_select_columns()).group_by(*cls._get_select_group_condition()))

    @classmethod
    def _get_select_columns(cls):
        raise NotImplementedError

    @classmethod
    def _get_select_group_condition(cls):
        raise NotImplementedError


class SleepDayModel(SleepDurationModel):
    @classmethod
    def get_column_names(cls):
        return ['id', 'date', 'duration', 'count']

    @classmethod
    def _get_select_columns(cls):
        return SleepDateView.id, SleepDateView.date, SleepDateView.duration, SleepDateView.count

    @classmethod
    def _get_select_group_condition(cls):
        return SleepDateView.date,


class SleepWeekModel(SleepDurationModel):
    @classmethod
    def get_column_names(cls):
        return ['id', 'week', 'duration', 'min']

    @classmethod
    def _get_select_columns(cls):
        return SleepDateView.id, fn.DATE(fn.DATE(SleepDateView.date, "weekday 0"), "-6 days").alias('week'), \
               fn.STRFTIME("%H:%M", fn.AVG(fn.STRFTIME("%s", SleepDateView.duration)), 'unixepoch').alias('duration'), \
               fn.STRFTIME("%H:%M", fn.MIN(fn.STRFTIME("%s", SleepDateView.duration)), 'unixepoch').alias('min')

    @classmethod
    def _get_select_group_condition(cls):
        return fn.STRFTIME("%W", SleepDateView.date),


class SleepMonthModel(SleepDurationModel):
    @classmethod
    def get_column_names(cls):
        return ['id', 'month', 'duration']

    @classmethod
    def _get_select_columns(cls):
        return SleepDateView.id, fn.DATE(SleepDateView.date, "start of month").alias('month'), \
               fn.STRFTIME("%H:%M", fn.AVG(fn.STRFTIME("%s", SleepDateView.duration)), 'unixepoch').alias('duration')

    @classmethod
    def _get_select_group_condition(cls):
        return fn.STRFTIME("%m", SleepDateView.date),


if __name__ == "__main__":
    import doctest
    doctest.testmod(report=True)
