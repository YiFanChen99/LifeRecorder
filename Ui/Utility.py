#!/usr/bin/env python
# -*- coding: utf-8 -*-
from PyQt5.QtWidgets import QMainWindow, QWidget, QVBoxLayout, QLabel
from PyQt5.QtCore import Qt


class BaseMainWindow(QMainWindow):
    def __init__(self, parent=None):
        super(BaseMainWindow, self).__init__(parent)
        self._init_central_widget()
        self._init_layout()
        self._init_footer()
        self.setWindowModality(Qt.WindowModal)

    def _init_central_widget(self):
        widget = QWidget()
        widget.setLayout(QVBoxLayout())
        self.setCentralWidget(widget)

    def _init_layout(self):
        raise NotImplementedError()

    def _init_footer(self):
        pass

    @property
    def central_layout(self):
        return self.centralWidget().layout()


class AlignHCLabel(QLabel):
    def __init__(self, *args, **kwargs):
        super(AlignHCLabel, self).__init__(*args, **kwargs)
        self.setAlignment(Qt.AlignCenter)
