#!/usr/bin/env python
# -*- coding: utf-8 -*-
from collections import OrderedDict
from PyQt5.QtWidgets import *
from PyQt5.QtCore import Qt, QSize
from PyQt5.QtGui import *

from Model.DbTableModel.BaseModel import DurationType
from Model.TableViewModel import DateFilter


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
    def __init__(self, options, default_index=0):
        """
        options: {data: text} in dict or OrderedDict
        """
        super().__init__()

        for data, text in options.items():
            self.addItem(text, data)
        self.setCurrentIndex(default_index)


class DateFilterComBox(MapComboBox):
    def __init__(self, callback, default_index=3):
        if not callable(callback):
            raise ValueError

        options = OrderedDict((enum, enum.value) for enum in DateFilter.Type)
        super().__init__(options, default_index=default_index)

        self.callback = callback
        self.currentIndexChanged.connect(self.notify)

    def notify(self):
        self.callback(self.currentData())


class DurationGroup(QWidget):
    BUTTONS = ((d_type, d_type.value) for d_type in DurationType)

    def __init__(self, callback, buttons=None, default_checked=0):
        """
        buttons: ((callback_key, display_text), )
        """
        if not callable(callback):
            raise ValueError
        if buttons is None:
            buttons = self.BUTTONS

        super().__init__()
        self.callback = callback
        self.default_checked = default_checked
        self._init_layout(buttons)

    def trigger(self, index):
        action = self.group.actions()[index]
        action.trigger()

    def notify(self, key):
        self.callback(key)

    def set_checked(self, index):
        action = self.group.actions()[index]
        action.setChecked(True)

    def _init_layout(self, buttons):
        self.setLayout(QHBoxLayout())

        self.group = QActionGroup(self)
        self._init_action_buttons(buttons)
        self.set_checked(self.default_checked)

    def _init_action_buttons(self, buttons):
        for key, value in buttons:
            button = QToolButton()
            button.setDefaultAction(self._create_action(key, value))
            button.setSizePolicy(QSizePolicy.Preferred, QSizePolicy.Preferred)
            button.sizeHint = lambda: QSize(75, 23)
            self.layout().addWidget(button)

    def _create_action(self, callback_key, text):
        if not self.group:
            raise AttributeError("ActionGroup(self.group) is None.")

        action = QAction(text, self.group)
        action.setCheckable(True)
        action.triggered.connect(lambda: self.notify(callback_key))
        return action
