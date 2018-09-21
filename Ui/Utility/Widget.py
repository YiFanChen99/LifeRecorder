#!/usr/bin/env python
# -*- coding: utf-8 -*-
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
