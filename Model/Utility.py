#!/usr/bin/env python
# -*- coding: utf-8 -*-
import datetime
from enum import Enum

from Model.DataAccessor.DbTableAccessor import Timeline


def init_timeline_on_date(date):
    """ Make sure the given date is on table Timeline. """
    return Timeline.get_or_create(date=date)


def get_or_create_date_id(date):
    if isinstance(date, Timeline):
        return date[0]
    else:
        return Timeline.get_or_create(date=date)[0]


class DateFilter(object):
    class Type(Enum):
        ONE_MONTH = '1 month'
        SIX_MONTH = '6 months'
        TWO_YEAR = '2 years'
        NO = 'no'

    @staticmethod
    def get_date(date_filter):
        if date_filter == DateFilter.Type.NO:
            return datetime.datetime.min.date()
        elif date_filter == DateFilter.Type.ONE_MONTH:
            return datetime.date.today() - datetime.timedelta(days=30)
        elif date_filter == DateFilter.Type.SIX_MONTH:
            return datetime.date.today() - datetime.timedelta(days=183)
        elif date_filter == DateFilter.Type.TWO_YEAR:
            return datetime.date.today() - datetime.timedelta(days=730)
        else:
            raise KeyError
