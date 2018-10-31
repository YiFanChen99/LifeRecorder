#!/usr/bin/env python
# -*- coding: utf-8 -*-
from collections import OrderedDict
from PyQt5.QtWidgets import *
from PyQt5.QtCore import Qt
from PyQt5.QtGui import *


class AlignHCLabel(QLabel):
    def __init__(self, *args, **kwargs):
        super(AlignHCLabel, self).__init__(*args, **kwargs)
        self.setAlignment(Qt.AlignCenter)


class HLine(QFrame):
    def __init__(self, *args):
        super(HLine, self).__init__(frameShape=QFrame.HLine, *args)

        palette = self.palette()
        palette.setColor(QPalette.All, QPalette.Foreground, Qt.gray)
        self.setPalette(palette)


class HBoxMenu(QWidget):
    DEFAULT_LAYOUT = {
        'pre_post_spacing': 25,
        'between_spacing': 15,
        'btn_width': 100,
        'btn_height': 20
    }

    def __init__(self, owner, config):
        """
        >>> HBoxMenu(QWidget(), {
            'menu': {
                'Sleep': {'callback': lambda obj: obj.method_sleep(), 'shortcut': 'F2'},
                'Flesh': {'callback': lambda obj: obj.method_flesh()}
            },
            'default_selection': 'Sleep'
        })
        """
        super(HBoxMenu, self).__init__()

        self.owner = owner
        self._init_actions(config['menu'])
        self._init_layout(config['menu'])

        self.last_action = None
        self.default_selection = config['default_selection']

    def trigger_default(self):
        self.last_action = None
        self.actions[self.default_selection].trigger()

    def _init_actions(self, config):
        self.actions = {}
        self.action_group = QActionGroup(self)

        for name, detail in config.items():
            self.actions[name] = self._create_action(
                name, detail.get('shortcut', None), detail.get('callback'))

    def _create_action(self, text, shortcut, callback):
        action = QAction(text, self.action_group)
        if shortcut:
            action.setShortcut(shortcut)
        action.setCheckable(True)
        action.triggered.connect(lambda: self._triggering_action(action, callback))
        return action

    def _triggering_action(self, action, callback):
        if self._pre_action(action):
            callback(self.owner)
            self._post_action(action)

    def _pre_action(self, action):
        return self.last_action is not action

    def _post_action(self, action):
        self.last_action = action

    def _init_layout(self, config):
        layout = QHBoxLayout()
        self.setLayout(layout)

        layout.addSpacing(self.DEFAULT_LAYOUT['pre_post_spacing'])
        layout.setSpacing(self.DEFAULT_LAYOUT['between_spacing'])

        for button in self._create_buttons(config):
            button.setMinimumSize(self.DEFAULT_LAYOUT['btn_width'], self.DEFAULT_LAYOUT['btn_height'])
            layout.addWidget(button)

        layout.addSpacing(self.DEFAULT_LAYOUT['pre_post_spacing'])
        layout.addStretch(1)  # Align left

    def _create_buttons(self, config):
        for name in config.keys():
            button = QToolButton()
            button.setDefaultAction(self.actions[name])
            yield button


class DateEdit(QDateEdit):
    FORMAT = "yyyy-MM-dd"

    def __init__(self, *args):
        super(DateEdit, self).__init__(*args, displayFormat=DateEdit.FORMAT, calendarPopup=True)

    def get_date(self):
        return self.date().toPyDate()

    def to_str(self):
        return self.date().toString(DateEdit.FORMAT)

    def setDate(self, *args):
        super(DateEdit, self).setDate(*args)
        self.setCurrentSectionIndex(2)


class MapComboBox(QComboBox):
    def __init__(self, options):
        """
        options: {data: text} in dict or OrderedDict
        """
        super().__init__()

        for data, text in options.items():
            self.addItem(text, data)
