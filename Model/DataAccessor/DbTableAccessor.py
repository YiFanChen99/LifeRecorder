# -*- coding: utf-8 -*-
from peewee import *
import datetime
import unittest

from Model.DataAccessor.DbAccessor.DbOrmAccessor import db, BaseModel
from Model.DataAccessor.Configure import config


def atomic():
    return db.atomic()


class Timeline(BaseModel):
    date = DateField(default=datetime.date.today)


class Flesh(BaseModel):
    date = ForeignKeyField(Timeline, backref='flesh')
    count = FloatField(default=1.0)


class Sleep(BaseModel):
    start = DateTimeField()
    end = DateTimeField()


class SleepDateView(BaseModel):
    date = DateField()
    duration = TimeField()
    count = IntegerField()


class RecordGroup(BaseModel):
    description = TextField(unique=True)
    alias = TextField(null=True)
    countable = BooleanField(null=False)

    def __getattr__(self, item):
        if item == 'parents':
            return tuple(relation.parent for relation in self.parent)
        elif item == 'children':
            return tuple(relation.child for relation in self.child)
        else:
            return super().__getattr__(item)

    def __repr__(self):
        return "{0}-{1}".format(self.id, self.description)


class GroupRelation(BaseModel):
    parent = ForeignKeyField(RecordGroup, backref='child')
    child = ForeignKeyField(RecordGroup, backref='parent')


class BasicRecord(BaseModel):
    date_id = ForeignKeyField(Timeline, backref='record')
    group_id = ForeignKeyField(RecordGroup, backref='basic')


class ExtraRecord(BaseModel):
    basic_id = ForeignKeyField(BasicRecord, backref='extra')
    key = TextField(null=False)
    value = TextField(null=False)


_test_data = {
    'record_group': ['讀書', '數學', '國文', '古典文學', '運動', '打坐']
}


class _BasicTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        db.init("./DbTableAccessorUnittest.db")

    def test_basic_tables(self):
        self.assertEqual(7, Flesh.select().count())
        self.assertEqual(24, Timeline.select().count())
        self.assertEqual(11, Sleep.select().count())
        self.assertEqual(7, SleepDateView.select().count())

    def test_life_record_tables(self):
        self.assertEqual(6, RecordGroup.select().count())
        self.assertEqual(_test_data['record_group'],
                         [record.description for record in RecordGroup.select()])
        self.assertEqual(3, GroupRelation.select().count())
        self.assertEqual(4, BasicRecord.select().count())
        self.assertEqual(5, ExtraRecord.select().count())


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


class _TableOperationTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        db.init("./DbTableAccessorUnittest.db")

    def test_create_tables(self):
        with self.assertRaises(OperationalError):  # table already exists
            db.create_tables([RecordGroup], safe=False)

    def test_drop_tables(self):
        with db.atomic() as transaction:
            db.drop_tables([RecordGroup, GroupRelation])

            with self.assertRaises(OperationalError):  # no such table
                RecordGroup.select().count()
            with self.assertRaises(OperationalError):  # no such table
                GroupRelation.select().count()

            transaction.rollback()

    def test_create_record(self):
        with db.atomic() as transaction:
            with self.assertRaises(IntegrityError):  # UNIQUE constraint failed
                RecordGroup.create(description='古典文學')

            RecordGroup.create(description='Ha?Ha')
            self.assertEqual(7, RecordGroup.select().count())

            transaction.rollback()


if __name__ == "__main__":
    unittest.main()
else:
    db.init(config['db_path'])
    db.connect()
