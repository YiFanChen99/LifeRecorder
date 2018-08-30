# -*- coding: utf-8 -*-
from peewee import *
import datetime
import unittest

from ModelUtility.DataAccessor.Base.DbOrmAccessor import db, BaseModel


class Timeline(BaseModel):
    date = DateField(default=datetime.date.today)


class DateBaseModel(BaseModel):
    date = DateField(default=datetime.date.today)

    @classmethod
    def create(cls, **kwargs):
        param_date = kwargs.get('date', None)
        if (param_date is not None) and not isinstance(param_date, Timeline):
            kwargs['date'] = Timeline.get_or_create(date=param_date)[0]

        super(DateBaseModel, cls).create(**kwargs)


class Flesh(DateBaseModel):
    date = ForeignKeyField(Timeline, backref='flesh')
    count = FloatField(default=1.0)


class Sleep(BaseModel):
    start = DateTimeField()
    end = DateTimeField()

    @classmethod
    def create(cls, **kwargs):
        datetime_end = kwargs.get('end')
        param_date = datetime_end - datetime.timedelta(hours=14)

        Timeline.get_or_create(date=param_date)
        super(BaseModel, cls).create(**kwargs)


class SleepDateView(DateBaseModel):
    date = DateField()
    duration = TimeField()
    count = IntegerField()


class _BasicTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        db.init("./DbTableAccessorUnittest.db")

    def test_current_rows(self):
        self.assertEqual(7, Flesh.select().count())
        self.assertEqual(24, Timeline.select().count())
        self.assertEqual(11, Sleep.select().count())
        self.assertEqual(7, SleepDateView.select().count())


class _JoinTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        db.init("./DbTableAccessorUnittest.db")

    @staticmethod
    def left_outer_join_timeline_and_flesh():
        """ Able to join by \"prefetch\" with foreign-key-relation. """

        return Timeline.select().prefetch(Flesh)

    @staticmethod
    def left_outer_join_timeline_and_flesh_and_sleep_dv():
        """ Join with explicit selected columns. """

        query = _JoinTest.left_outer_join_timeline_and_flesh()
        return (query.select(
            Timeline.id, Timeline.date, SleepDateView.date, SleepDateView.duration, SleepDateView.count
        ).join(SleepDateView, JOIN.LEFT_OUTER, on=(Timeline.date == SleepDateView.date)))

    def test_timeline_join_flesh(self):
        """ Timeline join Flesh. """

        query = self.left_outer_join_timeline_and_flesh()
        self.assertEqual(24, query.count())

        specific_date = query.where(Timeline.date == "2018-08-04").get()
        self.assertEqual(7, specific_date.id)
        self.assertEqual(datetime.date(2018, 8, 4), specific_date.date)
        flesh_records = [record.count for record in specific_date.flesh]
        self.assertEqual(1, len(flesh_records))
        self.assertEqual(1.0, flesh_records[0])

    def test_timeline_join_flesh_join_sleep_dv(self):
        """ (Timeline join Flesh) join SleepDateView. """

        query = self.left_outer_join_timeline_and_flesh_and_sleep_dv()
        self.assertEqual(24, query.count())

        specific_date = query.where(Timeline.date == "2018-08-13").get()
        self.assertEqual(16, specific_date.id)
        self.assertEqual(datetime.date(2018, 8, 13), specific_date.date)
        flesh_records = [record.count for record in specific_date.flesh]
        self.assertEqual(0, len(flesh_records))
        self.assertEqual(datetime.time(7, 30), specific_date.sleepdateview.duration)
        self.assertEqual(2, specific_date.sleepdateview.count)


if __name__ == "__main__":
    unittest.main()
else:
    db.init("D:\Dropbox\YiFanAndPig\LifeRecorder.db")
    db.connect()

