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


def covert_timedelta_to_time(timedelta):
    return (datetime.datetime.min + timedelta).time()


def str_timedelta(timedelta):
    return "%02d:%02d" % covert_timedelta_to_hours_and_minutes(timedelta)


def covert_timedelta_to_hours_and_minutes(timedelta):
    return timedelta.seconds//3600, (timedelta.seconds//60) % 60
