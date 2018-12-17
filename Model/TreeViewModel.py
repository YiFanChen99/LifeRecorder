#!/usr/bin/env python
# -*- coding: utf-8 -*-
from types import SimpleNamespace

from Model.DataAccessor.DbTableAccessor import RecordGroup


class RecordGroupTreeModel(object):
    @staticmethod
    def get_tree():
        raw_data = RecordGroup.select()
        return RecordGroupTreeModel.create_root(raw_data)

    @staticmethod
    def create_root(record_group_data):
        root = SimpleNamespace()
        root.id = -1
        root.description = "root"
        root.children = list(filter(lambda datum: datum.parent is None, record_group_data))
        return root


if __name__ == "__main__":
    pass
