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

    SleepModel.create(
        start=datetime.datetime.combine(date, time_start),
        end=datetime.datetime.combine(date, time_end))


def create_flesh():
    FleshModel.create(date=datetime.date(2018, 8, 31), count=1.0)


if __name__ == "__main__":
    create_sleep()
    # create_flesh()
    pass
