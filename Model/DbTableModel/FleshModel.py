#!/usr/bin/env python
# -*- coding: utf-8 -*-
from Model.DbTableModel.BaseModel import BaseModel
from Model import Utility
from Model.DataAccessor.DbTableAccessor import Timeline, Flesh, DoesNotExist, fn, JOIN


class FleshModel(BaseModel):
    @classmethod
    def get_column_names(cls):
        return ['id', 'date', 'count']

    @classmethod
    def get_data(cls):
        return list(Timeline.select(Timeline.id, Timeline.date, fn.SUM(Flesh.count).alias('count')).join(
            Flesh, JOIN.INNER, on=(Timeline.id == Flesh.date)).group_by(Timeline.date))

    @staticmethod
    def add(date, count):
        if count <= 0:
            raise ValueError("Count should be greater than 0.")
        count_before = FleshModel.get_count(date)
        count_after = count_before + count
        if count_after > 2:
            raise ValueError("Count will be %d (over 2)." % count_after)

        date_id = Utility.get_or_create_date_id(date)
        Flesh.replace(date=date_id, count=count_after).execute()

        return count_after

    @staticmethod
    def get_count(date):
        try:
            timeline = Timeline.select().prefetch(Flesh).where(Timeline.date == date).get()
            return timeline.flesh[0].count
        except (DoesNotExist, IndexError):
            return 0


if __name__ == "__main__":
    pass
