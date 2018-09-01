#!/usr/bin/env python
# -*- coding: utf-8 -*-
import sys
import datetime
from PyQt5.QtWidgets import *
from PyQt5.QtCore import QDate
from PyQt5.QtGui import QDoubleValidator

from Ui.Utility import BaseAdderWindow
from Model.FleshModel import FleshModel


class FleshAdderWindow(BaseAdderWindow):
    def __init__(self, parent=None):
        super(FleshAdderWindow, self).__init__(parent)

        self.resize(250, 150)
        self.setWindowTitle("Flesh Adder")

    def _init_layout(self):
        self.input_layout = QFormLayout()
        input_layout = self.input_layout
        self.central_layout.addLayout(input_layout)

        input_layout.setSpacing(10)

        self.date = QLineEdit()
        input_layout.addRow("Date:", self.date)
        self.count = QLineEdit()
        input_layout.addRow("Count:", self.count)

    def show(self):
        super(FleshAdderWindow, self).show()
        self.reset_values()

    def reset_values(self):
        self.date.setText(str(QDate.currentDate().toPyDate()))
        self.count.setText("1.0")
        self.count.setValidator(QDoubleValidator(0, 10, 1, notation=QDoubleValidator.StandardNotation))
        self.message_box.clear()

    def add(self):
        date = datetime.datetime.strptime(self.date.text(), "%Y-%m-%d").date()
        count = float(self.count.text())

        try:
            count_after = FleshModel.add(date, count)
            self.message_box.setText("{0}:  +{1}  -->  {2}".format(date, count, count_after))
        except ValueError as ex:
            self.message_box.setText("Failed. (ValueError: %s)" % str(ex))


if __name__ == "__main__":
    app = QApplication(sys.argv)

    window = FleshAdderWindow()
    window.show()

    app.exec_()
