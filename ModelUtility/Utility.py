#!/usr/bin/env python
# -*- coding: utf-8 -*-
from ModelUtility.DataAccessor.DbTableAccessor import Timeline


def init_timeline_on_date(date):
    """ Make sure the given date is on table Timeline. """
    return Timeline.get_or_create(date=date)


def get_or_create_date_id(date):
    if isinstance(date, Timeline):
        return date[0]
    else:
        return Timeline.get_or_create(date=date)[0]
