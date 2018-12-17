#!/usr/bin/env python
# -*- coding: utf-8 -*-
from enum import Enum
from collections import OrderedDict
import unittest

from Model.DataAccessor.DbTableAccessor import fn, create


class BaseModel(object):
    # Used on create, _select, _default_columns.
    ACCESSOR = None

    @classmethod
    def get_column_names(cls, *args):
        """
        Can easily be implemented with cls._default_columns().
        Should add doctest for readibility.
        """
        raise NotImplementedError()

    @classmethod
    def get_data(cls, *args):
        return cls._select()

    @classmethod
    def get_record_attr(cls, record, attr):
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

        return create(cls.ACCESSOR, **kwargs)


class DurationType(Enum):
    DAILY = 'Daily'
    WEEKLY = 'Weekly'
    MONTHLY = 'Monthly'


class DurationalColumnModel(BaseModel):
    # Used on create, _select, _default_columns by super().
    ACCESSOR = None

    @staticmethod
    def get_definition_leaders(definition):
        if isinstance(definition, dict):
            return list(definition.keys())
        else:
            return [item[0] if isinstance(item, (list, tuple)) else item
                    for item in definition]

    @classmethod
    def get_column_names(cls, duration):
        definition = cls.get_columns_definition(duration)
        return cls.get_definition_leaders(definition)

    @classmethod
    def get_columns_definition(cls, duration):
        if duration is DurationType.DAILY:
            return cls._default_columns()
        else:
            raise NotImplementedError


class DurationModel(DurationalColumnModel):
    # Used on get_columns_definition, _get_select_group_conditions.
    #   Also used on create, _select, _default_columns by super().
    ACCESSOR = None

    @classmethod
    def get_data(cls, duration):
        return cls._select(
            *cls.get_select_columns(duration)
        ).group_by(*cls._get_select_group_conditions(duration))

    @classmethod
    def get_columns_definition(cls, duration):
        if duration is DurationType.DAILY:
            return OrderedDict((name, getattr(cls.ACCESSOR, name)) for name in cls._default_columns())
        else:
            raise NotImplementedError

    @classmethod
    def get_select_columns(cls, duration):
        return list(cls.get_columns_definition(duration).values())

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
        return fn.DATE(field, "weekday 0", "-6 days")

    @staticmethod
    def week_end(field):
        return fn.DATE(field, "weekday 0")

    @staticmethod
    def month_start(field):
        return fn.DATE(field, "start of month")

    @staticmethod
    def time(field):
        return fn.STRFTIME("%H:%M", field, 'unixepoch')


class _DurationalColumnModelTest(unittest.TestCase):

    def assertLeader(self, definition, expect):
        result = DurationalColumnModel.get_definition_leaders(definition)
        self.assertEqual(result, expect)

    def test_single_definition(self):
        expect = ['ekko', 'eiki']

        definition = expect
        self.assertLeader(definition, expect)

        definition = tuple(definition)
        self.assertNotEqual(definition, expect)
        self.assertLeader(definition, expect)

    def test_dict_definition(self):
        expect = ['ekko', 'eiki']

        # dict definition
        definition = {key: 30 for key in expect}
        self.assertLeader(definition, expect)

        # OrderedDict definition
        definition = OrderedDict((key, 30) for key in expect)
        self.assertLeader(definition, expect)

    def test_multi_definition(self):
        expect = ['ekko', 'eiki']

        # tuple sub-definition
        definition = ((key, 9, 2) for key in expect)
        self.assertLeader(definition, expect)

        # list sub-definition
        definition = ([key, 'name', False] for key in expect)
        self.assertLeader(definition, expect)


if __name__ == "__main__":
    unittest.main()
