#!/usr/bin/env python
# -*- coding: utf-8 -*-
import datetime

import ModelUtility.Utility as Utility
from ModelUtility.DataAccessor.DbTableAccessor import Sleep, SleepDateView, DoesNotExist


class SleepModel(object):
    @staticmethod
    def create_by_datetime(start, end):
        date = (end - datetime.timedelta(hours=14))

        Utility.init_timeline_on_date(date)
        Sleep.create(start=start, end=end)

    @staticmethod
    def create_by_date(date, time_start, time_end):
        SleepModel.create_by_datetime(
            start=datetime.datetime.combine(date, time_start),
            end=datetime.datetime.combine(date, time_end))


class SleepDateViewModel(object):
    @staticmethod
    def get_duration(date):
        try:
            return SleepDateView.select().where(SleepDateView.date == date).get().duration
        except DoesNotExist:
            return datetime.time()


if __name__ == "__main__":
    pass
