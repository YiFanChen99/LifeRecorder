#!/usr/bin/env python
# -*- coding: utf-8 -*-
import datetime
from ModelUtility.DataAccessor.DbTableAccessor import Timeline


def init_timeline_on_date(date):
    """ Make sure the given date is on table Timeline. """
    return Timeline.get_or_create(date=date)


def get_or_create_date_id(date):
    if isinstance(date, Timeline):
        return date[0]
    else:
        return Timeline.get_or_create(date=date)[0]


def get_time_growth(start, end):
    start_delta = datetime.timedelta(hours=start.hour, minutes=start.minute, seconds=start.second)
    end_delta = datetime.timedelta(hours=end.hour, minutes=end.minute, seconds=end.second)
    return (datetime.datetime.min + end_delta - start_delta).time()
