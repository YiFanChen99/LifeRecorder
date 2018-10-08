#!/usr/bin/env python
# -*- coding: utf-8 -*-
import datetime


def covert_timedelta_to_time(timedelta):
    return (datetime.datetime.min + timedelta).time()


def str_timedelta(timedelta):
    return "%02d:%02d" % covert_timedelta_to_hours_and_minutes(timedelta)


def covert_timedelta_to_hours_and_minutes(timedelta):
    return timedelta.seconds//3600, (timedelta.seconds//60) % 60
