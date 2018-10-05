#!/usr/bin/env python
# -*- coding: utf-8 -*-
from Model.DbTableModel.BaseModel import BaseModel, SimpleModel
from ModelUtility import Utility
from ModelUtility.DataAccessor.DbTableAccessor import atomic, DoesNotExist
from ModelUtility.DataAccessor.DbTableAccessor import RecordGroup, GroupRelation, BasicRecord, ExtraRecord


class RecordGroupModel(BaseModel):
    @classmethod
    def get_column_names(cls):
        names = RecordGroup.get_column_names()
        names.append('children')
        return names

    @classmethod
    def get_data(cls):
        return list(RecordGroup.select().prefetch(GroupRelation))

    @staticmethod
    def get_id_description_map():
        return dict((group.id, group.description) for group in RecordGroup.select())


class GroupRelationModel(BaseModel):
    @classmethod
    def get_column_names(cls):
        return ['id', 'parent', 'child']

    @classmethod
    def get_data(cls):
        return list(GroupRelation.select().prefetch(RecordGroup))


class BasicRecordModel(SimpleModel):
    @classmethod
    def get_accessor(cls):
        return BasicRecord

    @staticmethod
    def create(date, group_id):
        date_id = Utility.get_or_create_date_id(date)
        return BasicRecord.create(date_id=date_id, group_id=group_id)

    @staticmethod
    def create_with_extras(date, group_id, extras):
        with atomic() as txn:
            try:
                basic_id = BasicRecordModel.create(date, group_id)
                for extra in extras:
                    ExtraRecordModel.create(basic_id, extra[0], extra[1])
            except ValueError as ex:
                txn.rollback()
                raise ex

    @staticmethod
    def get_count(date, group_id):
        try:
            date_id = Utility.get_or_create_date_id(date)
            return BasicRecord.select().where(BasicRecord.date_id == date_id, BasicRecord.group_id == group_id).count()
        except (DoesNotExist, IndexError):
            return 0


class ExtraRecordModel(SimpleModel):
    KEYS = ['description', 'magnitude', 'scale']

    @classmethod
    def get_accessor(cls):
        return ExtraRecord

    @staticmethod
    def create(basic_id, key, value):
        try:
            BasicRecord.get_by_id(basic_id)
        except DoesNotExist:
            raise ValueError('Basic id %d' % basic_id)

        return ExtraRecord.create(basic_id=basic_id, key=key, value=value)


class RawRecordModel(BaseModel):
    @classmethod
    def get_column_names(cls):
        return ['id', 'date', 'group', 'extra']

    @classmethod
    def get_data(cls):
        return list(BasicRecord.select().prefetch())


if __name__ == "__main__":
    pass
