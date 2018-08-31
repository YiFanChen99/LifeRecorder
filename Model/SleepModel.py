#!/usr/bin/env python
# -*- coding: utf-8 -*-
import datetime

import ModelUtility.Utility as Utility
from ModelUtility.DataAccessor.DbTableAccessor import Sleep, SleepDateView, DoesNotExist


class SleepModel(object):
    @staticmethod
    def create_by_datetime(start, end):
        date_belonged = SleepModel.get_date_belonged(end)
        Utility.init_timeline_on_date(date_belonged)

        duration_before = SleepDateViewModel.get_duration(date_belonged)
        Sleep.create(start=start, end=end)
        duration_after = SleepDateViewModel.get_duration(date_belonged)
        duration_growth = datetime.time(
            duration_after.hour - duration_before.hour,
            duration_after.minute - duration_before.minute)
        return [date_belonged, duration_growth]

    @staticmethod
    def create_by_date(date, time_start, time_end):
        return SleepModel.create_by_datetime(
            start=datetime.datetime.combine(date, time_start),
            end=datetime.datetime.combine(date, time_end))

    @staticmethod
    def get_date_belonged(the_datetime):
        return (the_datetime - datetime.timedelta(hours=14)).date()


class SleepDateViewModel(object):
    @staticmethod
    def get_duration(date):
        try:
            return SleepDateView.select().where(SleepDateView.date == date).get().duration
        except DoesNotExist:
            return datetime.time()


if __name__ == "__main__":
    pass
