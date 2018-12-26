#!/usr/bin/env python
# -*- coding: utf-8 -*-
from collections import OrderedDict
from enum import Enum
from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
from PyQt5.QtGui import *

from Model.DbTableModel.BaseModel import DurationType
from Model.TreeViewModel import RecordGroupTreeModel
from Model.Utility import DateFilter


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
            'default_selection': 'Sleep'  # Optional
        })
        """
        super(HBoxMenu, self).__init__()

        self.owner = owner
        self._init_actions(config['menu'])
        self._init_layout(config['menu'])

        self.default_index = 0
        if config['default_selection']:
            self.set_default_selection(config['default_selection'])
        self.set_checked()

    def trigger(self, index=-1):
        if index == -1:
            index = self.default_index

        action = self.action_group.actions()[index]
        action.trigger()

    def set_checked(self, index=-1):
        if index == -1:
            index = self.default_index

        action = self.action_group.actions()[index]
        action.setChecked(True)

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

    # noinspection PyUnusedLocal, PyMethodMayBeStatic
    def _pre_action(self, action):
        """
        ex: return self.last_action is not action
        """
        return True

    def _post_action(self, action):
        pass

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

    def set_default_selection(self, selection):
        """
        :param selection: Allowing either str as action name or int as index.
        """
        if isinstance(selection, str):
            actions = self.action_group.actions()
            selection = [action.text() for action in actions].index(selection)
        self._set_default_index(selection)

    def _set_default_index(self, index):
        if index >= len(self.action_group.actions()):
            raise IndexError("Index %d out of range %d" % (index, len(self.action_group.actions())))

        self.default_index = index


class DateEdit(QDateEdit):
    FORMAT = "yyyy-MM-dd"

    def __init__(self, *args):
        super().__init__(*args, displayFormat=DateEdit.FORMAT, calendarPopup=True)

    def get_date(self):
        return self.date().toPyDate()

    def to_str(self):
        return self.date().toString(DateEdit.FORMAT)

    def setDate(self, *args):
        super(DateEdit, self).setDate(*args)
        self.setCurrentSectionIndex(2)


class BaseComboBox(QComboBox):
    def __init__(self, items_config=None, default_index=0, default_index_data=None):
        super().__init__()
        self._init_items(items_config)
        if default_index_data:
            self.setCurrentData(default_index_data)
        else:
            self.setCurrentIndex(default_index)

    # noinspection PyPep8Naming
    def setCurrentData(self, data):
        index = self.findData(data)
        self.setCurrentIndex(index)


class MapComboBox(BaseComboBox):
    def _init_items(self, config):
        if isinstance(config, (dict, OrderedDict)):
            for data, text in config.items():
                self.addItem(text, data)
        elif issubclass(config, Enum):
            for type_ in config:
                self.addItem(type_.value, type_)
        else:
            raise ValueError


class DateFilterComBox(MapComboBox):
    def __init__(self, callback, *args, default_index_data=DateFilter.Type.NO, **kwargs):
        if not callable(callback):
            raise ValueError

        super().__init__(*args, items_config=DateFilter.Type,
                         default_index_data=default_index_data, **kwargs)

        self.callback = callback
        self.currentIndexChanged.connect(self.notify)

    def notify(self):
        self.callback(self.currentData())


class DurationGroup(QWidget):
    BUTTONS = tuple((d_type, d_type.value) for d_type in DurationType)

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

    # noinspection PyTypeChecker
    def set_checked(self, checked):
        """
        :param checked: index or instance of DurationType
        """
        if isinstance(checked, DurationType):
            checked = list(DurationType).index(checked)
        action = self.group.actions()[checked]
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


class RecordGroupComboBox(BaseComboBox):
    """ Faking a un-collapse tree-view like menu. """
    ROOT_DESCRIPTION = "-"

    def __init__(self, *args, with_root=False, **kwargs):
        """
        :param with_root: When True, adding root on top of menu with data=-1.
        """
        super().__init__(*args, items_config=with_root, **kwargs)

    def _init_items(self, with_root):
        if with_root:
            self.addItem(self.ROOT_DESCRIPTION, -1)

        root = RecordGroupTreeModel.get_tree()
        for level0 in root.children:
            self._add_item_by_node(level0, 0)

    def insert_item_by_group(self, group):
        # Find last sibling's position, +1 to insert after
        children = group.parent.children
        node_appended = group.parent if len(children) <= 1 else children[-2]
        index = self.findData(node_appended.id) + 1

        self.insertItem(index, *self.text_and_data(group, group.level))

    def _add_item_by_node(self, node, level):
        self.addItem(*self.text_and_data(node, level))
        for child in node.children:
            self._add_item_by_node(child, level + 1)

    @staticmethod
    def text_and_data(item, indent_level):
        indent = ''.join(["　"] * indent_level)
        return indent + item.description, item.id
