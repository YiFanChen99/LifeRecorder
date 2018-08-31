#!/usr/bin/env python
# -*- coding: utf-8 -*-
import ModelUtility.Utility as Utility
from ModelUtility.DataAccessor.DbTableAccessor import Flesh, IntegrityError


class FleshModel(object):
    @staticmethod
    def create(date, count):
        date_id = Utility.get_or_create_date_id(date)
        FleshModel._create(date=date_id, count=count)

    @staticmethod
    def _create(**kwargs):
        try:
            Flesh.create(**kwargs)
        except IntegrityError as ex:
            raise ValueError("IntegrityError") from ex


if __name__ == "__main__":
    pass
