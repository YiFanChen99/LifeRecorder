#!/usr/bin/env python
# -*- coding: utf-8 -*-
import os
import unittest
from collections import defaultdict

from Model.DataAccessor.JsonAccessor.JsonAccessor import load_json, save_json


class Configure(object):
    def __init__(self, dir_path):
        super(Configure, self).__init__()
        self.dir_path = dir_path
        self.default_config = None
        self.config = None

        self.load_default_config()
        self.load_config()

    def load_config(self):
        try:
            self.config = load_json(self.dir_path + "ConfigUser.json")
        except FileNotFoundError:
            self.config = {}

    def load_default_config(self):
        self.default_config = load_json(self.dir_path + "ConfigDefault.json")

    def save_config(self):
        save_json(self.dir_path + "ConfigUser.json", self.config)

    def __getitem__(self, name):
        try:
            return self.config[name]
        except KeyError:
            return self.default_config[name]


def get_matched_dir(path, project_dir_name="LifeRecorder"):
    while True:
        head, tail = os.path.split(path)
        if tail == project_dir_name:
            return path
        elif head == path:
            raise ValueError(path)
        else:
            path = head


class _Test(unittest.TestCase):
    EXPECT = "D:\Projects\LifeRecorder"

    def assert_get_matched_dir(self, path, *args, **kwargs):
        self.assertEqual(self.EXPECT, get_matched_dir(path, *args, **kwargs))

    def test_get_matched_dir(self):
        self.assert_get_matched_dir(self.EXPECT)
        self.assert_get_matched_dir(self.EXPECT + "\ModelUtility\DataAccessor")

    def test_get_matched_dir_invalid_path(self):
        with self.assertRaises(ValueError):
            self.assert_get_matched_dir("")

        with self.assertRaises(ValueError):
            self.assert_get_matched_dir(self.EXPECT[:-1])

    def test_get_matched_dir_with_project_dir(self):
        self.assert_get_matched_dir(self.EXPECT, "LifeRecorder")
        self.assert_get_matched_dir(self.EXPECT + "\DDD\\", project_dir_name="LifeRecorder")

        with self.assertRaises(ValueError):
            self.assert_get_matched_dir(self.EXPECT, project_dir_name="AAA")


def _convert_alias_group_rules(raw_alias):
    result = defaultdict(dict)
    for rule_set in raw_alias.values():
        for group_id in rule_set['groups']:
            result[group_id].update(rule_set['rules'])
    return result


config = {}
group_alias_rules = {}

if __name__ == "__main__":
    unittest.main()
else:
    dir_path = get_matched_dir(os.getcwd()) + os.sep + "Data" + os.sep

    config = Configure(dir_path)

    raw = load_json(dir_path + "Alias.json")
    group_alias_rules = _convert_alias_group_rules(raw)
