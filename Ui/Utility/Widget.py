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

    # noinspection PyTypeChecker
    def setCurrentIndex(self, index):
        """
        :param index: index or instance of DateFilter.Type
        """
        if isinstance(index, DateFilter.Type):
            index = list(DateFilter.Type).index(index)
        super().setCurrentIndex(index)

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


class PanelChangeable(object):
    def __init__(self):
        self.current_panel = None
        super().__init__()

    def _init_panels(self):
        self.panels = tuple(self._create_panels())

        for panel in self.panels:
            self.layout().addWidget(panel)
            panel.hide()

        self.change_panel(self.menu.default_index)

    def _create_panels(self):
        raise NotImplementedError

    def change_panel(self, index):
        if self.current_panel:
            self.current_panel.hide()

        self.current_panel = self.panels[index]
        self.current_panel.show()


class BaseMenuPanel(QWidget):
    MENU_CONFIG = None

    def __init__(self, owner):
        if self.MENU_CONFIG is None:
            raise ValueError("MENU_CONFIG")

        super().__init__()
        self.owner = owner
        self._init_layout()

    def _init_layout(self):
        layout = QVBoxLayout()
        self.setLayout(layout)

        self._init_menu()
        self._init_main_panel()

    def _init_menu(self):
        self.menu = HBoxMenu(self, self.MENU_CONFIG)
        self.layout().addWidget(self.menu)

    def _init_main_panel(self):
        raise NotImplementedError


class RightClickable(QWidget):
    def __init__(self, *args):
        super().__init__(*args)

        self.right_click_menu = None
        self._init_right_click_menu()
        self._assert_right_click_menu()

    def _init_right_click_menu(self):
        """
        Should assign self.right_click_menu.
        """
        raise NotImplementedError

    def _assert_right_click_menu(self):
        if not isinstance(self.right_click_menu, QMenu):
            raise ValueError("self.right_click_menu not a QMenu.")

    def contextMenuEvent(self, event):
        self.right_click_menu.popup(QCursor.pos())
        super().contextMenuEvent(event)
