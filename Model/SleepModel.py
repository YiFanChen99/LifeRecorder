#!/usr/bin/env python
# -*- coding: utf-8 -*-
import datetime

import ModelUtility.Utility as Utility
from ModelUtility.DataAccessor.DbTableAccessor import Sleep


class SleepModel(object):
    @staticmethod
    def create(start, end):
        date = (end - datetime.timedelta(hours=14))

        Utility.init_timeline_on_date(date)
        Sleep.create(start=start, end=end)


if __name__ == "__main__":
    pass
