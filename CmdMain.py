#!/usr/bin/env python
# -*- coding: utf-8 -*-
import datetime

from Model.FleshModel import FleshModel
from Model.SleepModel import SleepModel


def create_sleep():
    date = datetime.date.today()
    # date = datetime.date(2018, 8, 22)
    time_start = datetime.time(13, 15)
    time_end = datetime.time(13, 30)

    try:
        SleepModel.create_by_date(date, time_start, time_end)
    except ValueError:
        print("Failed to create sleep with [{0}, {1}, {2}]".format(date, time_start, time_end))


def create_flesh():
    date = datetime.date(2018, 8, 31)
    count = 1.0

    try:
        FleshModel.create(date=date, count=count)
    except ValueError:
        print("Failed to create flesh with [{0}, {1}]".format(date, count))


if __name__ == "__main__":
    create_sleep()
    # create_flesh()
    pass
