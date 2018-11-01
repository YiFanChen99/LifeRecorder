#!/usr/bin/env python
# -*- coding: utf-8 -*-
from collections import OrderedDict
from Model.DbTableModel.BaseModel import BaseModel
from Model import Utility
from Model.DataAccessor.DbTableAccessor import atomic, DoesNotExist
from Model.DataAccessor.DbTableAccessor import RecordGroup, GroupRelation, BasicRecord, ExtraRecord


class RecordUtility(object):
    class Group:
        @staticmethod
        def get_id_description_map():
            return OrderedDict((group.id, group.description) for group in RecordGroup.select())

    class Basic:
        @staticmethod
        def create(date, group_id):
            date_id = Utility.get_or_create_date_id(date)
            return BasicRecord.create(date_id=date_id, group_id=group_id)

        @staticmethod
        def create_with_extras(date, group_id, extras):
            with atomic() as txn:
                try:
                    basic_id = RecordUtility.Basic.create(date, group_id)
                    for extra in extras:
                        RecordUtility.Extra.create(basic_id, extra[0], extra[1])
                except ValueError as ex:
                    txn.rollback()
                    raise ex

        @staticmethod
        def get_count(date, group_id):
            try:
                date_id = Utility.get_or_create_date_id(date)
                return BasicRecord.select().where(BasicRecord.date_id == date_id,
                                                  BasicRecord.group_id == group_id).count()
            except (DoesNotExist, IndexError):
                return 0

    class Extra:
        KEYS = ['description', 'magnitude', 'scale']

        @staticmethod
        def create(basic_id, key, value):
            try:
                BasicRecord.get_by_id(basic_id)
            except DoesNotExist:
                raise ValueError('Basic id %d' % basic_id)

            return ExtraRecord.create(basic_id=basic_id, key=key, value=value)


class RecordGroupModel(BaseModel):
    @classmethod
    def get_column_names(cls):
        """
        >>> RecordGroupModel.get_column_names()
        ['id', 'description', 'alias', 'children']
        """
        names = RecordGroup.get_column_names()
        names.append('children')
        return names

    @classmethod
    def get_data(cls):
        return RecordGroup.select().prefetch(GroupRelation)

    @classmethod
    def get_record_attr(cls, record, attr):
        if attr == 'children':
            return ", ".join([relation.child.description for relation in record.parent])
        else:  # default
            return super().get_record_attr(record, attr)


class GroupRelationModel(BaseModel):
    @classmethod
    def get_column_names(cls):
        return ['id', 'parent', 'child']

    @classmethod
    def get_data(cls):
        return GroupRelation.select().prefetch(RecordGroup)

    @classmethod
    def get_record_attr(cls, record, attr):
        if attr == 'parent':
            return record.parent.description
        elif attr == 'child':
            return record.child.description
        else:  # default
            return super().get_record_attr(record, attr)


class BasicRecordModel(BaseModel):
    ACCESSOR = BasicRecord

    @classmethod
    def get_column_names(cls):
        """
        >>> BasicRecordModel.get_column_names()
        ['id', 'date_id', 'group_id']
        """
        return super()._default_columns()


class ExtraRecordModel(BaseModel):
    ACCESSOR = ExtraRecord

    @classmethod
    def get_column_names(cls):
        """
        >>> ExtraRecordModel.get_column_names()
        ['id', 'basic_id', 'key', 'value']
        """
        return super()._default_columns()


class RawRecordModel(BaseModel):
    @classmethod
    def get_column_names(cls):
        return ['id', 'date', 'group', 'extra']

    @classmethod
    def get_data(cls):
        return BasicRecord.select().prefetch()

    @classmethod
    def get_record_attr(cls, record, attr):
        if attr == 'date':
            return record.date_id.date
        elif attr == 'group':
            return record.group_id.description
        elif attr == 'extra':
            return ", ".join(["<{0}: {1}>".format(extra.key, extra.value) for extra in record.extrarecord])
        else:  # default
            return super().get_record_attr(record, attr)


if __name__ == "__main__":
    import doctest
    doctest.testmod(report=True)
