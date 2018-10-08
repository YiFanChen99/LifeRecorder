#!/usr/bin/env python
# -*- coding: utf-8 -*-
from ModelUtility.DataAccessor.DbTableAccessor import IntegrityError


class BaseModel(object):
    @classmethod
    def get_column_names(cls):
        raise NotImplementedError()

    @classmethod
    def get_data(cls):
        raise NotImplementedError()

    @classmethod
    def get_record_value(cls, record, attr):
        return getattr(record, attr)


class SimpleModel(BaseModel):
    @classmethod
    def get_accessor(cls):
        raise NotImplementedError()

    @classmethod
    def get_column_names(cls):
        return cls.get_accessor().get_column_names()

    @classmethod
    def get_data(cls):
        return list(cls.get_accessor().select())

    @classmethod
    def create(cls, **kwargs):
        try:
            cls.get_accessor().create(**kwargs)
        except IntegrityError as ex:
            raise ValueError("IntegrityError") from ex
