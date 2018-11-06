#!/usr/bin/env python
# -*- coding: utf-8 -*-
from PyQt5.QtWidgets import *
from PyQt5.QtCore import Qt

from Ui.Utility.Widget import HLine


class BaseMainWindow(QMainWindow):
    def __init__(self, parent=None):
        super().__init__(parent)
        self._init_central_widget()
        self._init_layout()
        self.setWindowModality(Qt.WindowModal)

    def _init_central_widget(self):
        widget = QWidget()
        widget.setLayout(QVBoxLayout())
        self.setCentralWidget(widget)

    def _init_layout(self):
        self._init_main_panel()

    def _init_main_panel(self):
        self.main_panel = self._create_main_panel()
        self.central_layout.addWidget(self.main_panel)

    def _create_main_panel(self):
        raise NotImplementedError()

    @property
    def central_layout(self):
        return self.centralWidget().layout()

    def add_h_line(self):
        self.central_layout.addWidget(HLine())


class _BaseExtendedMainWindow(object):
    def __init__(self, *args):
        if not isinstance(self, BaseMainWindow):
            raise TypeError("Not a BaseMainWindow.")

        super(_BaseExtendedMainWindow, self).__init__(*args)


# noinspection PyUnresolvedReferences
class BaseMessageBoxWindow(_BaseExtendedMainWindow):
    def _init_message_box(self):
        self.add_h_line()

        box = QGroupBox()
        self.central_layout.addWidget(box)

        layout = QHBoxLayout()
        self.message_box = QLabel()
        layout.addWidget(self.message_box)
        box.setLayout(layout)


# noinspection PyUnresolvedReferences
class BaseAdderWindow(_BaseExtendedMainWindow):
    def _init_footer(self):
        self.add_h_line()

        footer_box = QDialogButtonBox(QDialogButtonBox.Reset | QDialogButtonBox.Save | QDialogButtonBox.Close)
        footer_box.button(QDialogButtonBox.Reset).clicked.connect(self.reset_values)
        footer_box.accepted.connect(self.add)
        footer_box.rejected.connect(self.close)

        self.central_layout.addWidget(footer_box)
        self.footer_box = footer_box

    def reset_values(self):
        raise NotImplementedError()

    def add(self):
        raise NotImplementedError()


class BaseConfigLoader(_BaseExtendedMainWindow):
    def _init_window(self, config):
        self.resize(config['width'], config['height'])
        self.move(config['x_axis'], config['y_axis'])
        self.setWindowTitle(config['title'])


class SimpleAdderWindow(BaseMainWindow, BaseMessageBoxWindow, BaseAdderWindow):
    def _init_layout(self):
        super()._init_layout()
        self._init_message_box()
        self._init_footer()

    def _create_main_panel(self):
        raise NotImplementedError()

    def reset_values(self):
        self.main_panel.reset_values()
        self.message_box.clear()

    def add(self):
        self.main_panel.add()

    def show(self):
        super().show()
        self.reset_values()
