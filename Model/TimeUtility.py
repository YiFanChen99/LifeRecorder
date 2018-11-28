#!/usr/bin/env python
# -*- coding: utf-8 -*-
import datetime
import unittest


def covert_timedelta_to_time(timedelta):
    return (datetime.datetime.min + timedelta).time()


def str_timedelta(timedelta):
    return "%02d:%02d" % covert_timedelta_to_hours_and_minutes(timedelta)


def covert_timedelta_to_hours_and_minutes(timedelta):
    return timedelta.seconds//3600, (timedelta.seconds//60) % 60


def get_week_start(date):
    return date - datetime.timedelta(days=date.weekday())


def get_week_start_and_end(date):
    start = get_week_start(date)
    end = date + datetime.timedelta(days=(6 - date.weekday()))
    return start, end


def get_month_start(date):
    return date.replace(day=1)


class _GetWeekStartAndEndTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.monday = datetime.date(2018, 10, 15)
        cls.days_in_one_week = tuple((cls.monday + datetime.timedelta(days=i)) for i in range(0, 7))
        cls.day_in_next_week = datetime.date(2018, 10, 15) + datetime.timedelta(days=9)

    def test_return_structure(self):
        results = get_week_start_and_end(self.monday)
        self.assertTrue(isinstance(results, tuple))
        self.assertEqual(len(results), 2)
        for result in results:
            self.assertTrue(isinstance(result, datetime.date))

    def test_day(self):
        results = get_week_start_and_end(self.monday)
        self.assertEqual(results[0], datetime.date(2018, 10, 15))
        self.assertEqual(results[1], datetime.date(2018, 10, 21))

        results = get_week_start_and_end(self.day_in_next_week)
        self.assertEqual(results[0], datetime.date(2018, 10, 22))
        self.assertEqual(results[1], datetime.date(2018, 10, 28))

    def test_whole_week(self):
        self.assertEqual(7, len(self.days_in_one_week))

        for day in self.days_in_one_week:
            start, end = get_week_start_and_end(day)
            self.assertEqual(start, self.days_in_one_week[0])
            self.assertEqual(end, self.days_in_one_week[6])


if __name__ == '__main__':
    unittest.main()
