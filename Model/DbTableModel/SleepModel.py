#!/usr/bin/env python
# -*- coding: utf-8 -*-
import datetime

from Model.DbTableModel.BaseModel import SimpleModel
from ModelUtility import Utility, TimeUtility
from ModelUtility.DataAccessor.DbTableAccessor import Sleep, SleepDateView, DoesNotExist


class SleepModel(SimpleModel):
    @classmethod
    def get_accessor(cls):
        return Sleep

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

    @staticmethod
    def get_duration(date):
        try:
            duration = SleepDateView.select().where(SleepDateView.date == date).get().duration
            return datetime.timedelta(hours=duration.hour, minutes=duration.minute)
        except DoesNotExist:
            return datetime.timedelta()


if __name__ == "__main__":
    pass
