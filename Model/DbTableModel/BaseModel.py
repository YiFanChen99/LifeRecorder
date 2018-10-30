#!/usr/bin/env python
# -*- coding: utf-8 -*-
from enum import Enum
from collections import OrderedDict

from Model.DataAccessor.DbTableAccessor import IntegrityError, fn


class BaseModel(object):
    ACCESSOR = None

    @classmethod
    def get_column_names(cls):
        """
        Can easily be implemented with cls._default_columns().
        Should add doctest for readibility.
        """
        raise NotImplementedError()

    @classmethod
    def get_data(cls):
        return cls._select()

    @classmethod
    def get_record_value(cls, record, attr):
        return getattr(record, attr)

    @classmethod
    def _select(cls, *args):
        if not cls.ACCESSOR:
            raise NotImplementedError

        return cls.ACCESSOR.select(*args)

    @classmethod
    def _default_columns(cls):
        if cls.ACCESSOR:
            return list(cls.ACCESSOR.get_column_names())
        raise KeyError('There is no ACCESSOR.')

    @classmethod
    def create(cls, **kwargs):
        if not cls.ACCESSOR:
            raise NotImplementedError

        try:
            cls.ACCESSOR.create(**kwargs)
        except IntegrityError as ex:
            raise ValueError("IntegrityError") from ex


class DurationType(Enum):
    DAILY = 'Daily'
    WEEKLY = 'Weekly'
    MONTHLY = 'Monthly'


class DurationModel(BaseModel):
    ACCESSOR = None

    @classmethod
    def get_column_names(cls, duration=DurationType.DAILY):
        return list(cls._get_columns(duration).keys())

    @classmethod
    def get_data(cls, duration=DurationType.DAILY):
        return cls._select(
            *cls._get_select_columns(duration)
        ).group_by(*cls._get_select_group_conditions(duration))

    @classmethod
    def _get_columns(cls, duration):
        if duration is DurationType.DAILY:
            return cls._default_columns()
        else:
            raise NotImplementedError

    @classmethod
    def _default_columns(cls):
        if cls.ACCESSOR:
            return OrderedDict((name, getattr(cls.ACCESSOR, name)) for name in cls.ACCESSOR.get_column_names())
        raise KeyError('There is no ACCESSOR.')

    @classmethod
    def _get_select_columns(cls, duration):
        return list(cls._get_columns(duration).values())

    @classmethod
    def _get_select_group_conditions(cls, duration):
        if not cls.ACCESSOR:
            raise NotImplementedError

        if duration is DurationType.DAILY:
            return cls.ACCESSOR.date,
        elif duration is DurationType.WEEKLY:
            return fn.STRFTIME("%W", cls.ACCESSOR.date),
        elif duration is DurationType.MONTHLY:
            return fn.STRFTIME("%m", cls.ACCESSOR.date),
        else:
            raise KeyError


class Func(object):
    @staticmethod
    def week_start(field):
        return fn.DATE(fn.DATE(field, "weekday 0"), "-6 days")

    @staticmethod
    def month_start(field):
        return fn.DATE(field, "start of month")

    @staticmethod
    def time(field):
        return fn.STRFTIME("%H:%M", field, 'unixepoch')
