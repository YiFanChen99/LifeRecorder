#!/usr/bin/env python
# -*- coding: utf-8 -*-
from PyQt5.QtWidgets import *
from PyQt5.QtCore import Qt


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

    def _init_footer(self):
        self.add_h_line()

    @property
    def central_layout(self):
        return self.centralWidget().layout()

    def add_h_line(self):
        line = QFrame(frameShape=QFrame.HLine)
        self.central_layout.addWidget(line)


class BaseMessageWindow(BaseMainWindow):
    def __init__(self, parent=None):
        super(BaseMessageWindow, self).__init__(parent)
        self._init_message_box()

    def _init_layout(self):
        raise NotImplementedError()

    def _init_message_box(self):
        self.add_h_line()

        box = QGroupBox()
        self.central_layout.addWidget(box)

        layout = QHBoxLayout()
        self.message_box = QLabel()
        layout.addWidget(self.message_box)
        box.setLayout(layout)


class BaseAdderWindow(BaseMessageWindow):
    def __init__(self, parent=None):
        super(BaseAdderWindow, self).__init__(parent)
        self._init_footer()

    def _init_layout(self):
        raise NotImplementedError()

    def _init_footer(self):
        super(BaseAdderWindow, self)._init_footer()

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
