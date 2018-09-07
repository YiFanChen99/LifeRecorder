#!/usr/bin/env python
# -*- coding: utf-8 -*-
from PyQt5.QtWidgets import *
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QPalette


class BaseMainWindow(QMainWindow):
    def __init__(self, parent=None):
        super(BaseMainWindow, self).__init__(parent)
        self._init_central_widget()
        self._init_layout()
        self.setWindowModality(Qt.WindowModal)

    def _init_central_widget(self):
        widget = QWidget()
        widget.setLayout(QVBoxLayout())
        self.setCentralWidget(widget)

    def _init_layout(self):
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
