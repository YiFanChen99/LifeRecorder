#!/usr/bin/env python
# -*- coding: utf-8 -*-
from ModelUtility.DataAccessor.JsonAccessor.JsonAccessor import load_json, save_json


class Configure(object):
    def __init__(self):
        super(Configure, self).__init__()
        self.default_config = None
        self.config = None

        self.load_default_config()
        self.load_config()

    def load_config(self, path="./Data/ConfigUser.json"):
        try:
            self.config = load_json(path)
        except FileNotFoundError:
            self.config = {}

    def load_default_config(self, path="./Data/ConfigDefault.json"):
        self.default_config = load_json(path)

    def save_config(self, path="./Data/ConfigUser.json"):
        save_json(path, self.config)

    def __getitem__(self, name):
        try:
            return self.config[name]
        except KeyError:
            return self.default_config[name]


config = Configure()
