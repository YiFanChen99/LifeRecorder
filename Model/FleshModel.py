#!/usr/bin/env python
# -*- coding: utf-8 -*-
import ModelUtility.Utility as Utility
from ModelUtility.DataAccessor.DbTableAccessor import Flesh


class FleshModel(object):
    @staticmethod
    def create(date, count):
        date_id = Utility.get_or_create_date_id(date)
        Flesh.create(date=date_id, count=count)


if __name__ == "__main__":
    pass
