#!/usr/bin/env python
# -*- coding: utf-8 -*-
import sys
from PyQt5.QtCore import QDate
from PyQt5.QtGui import QDoubleValidator

from Ui.Utility.Window import *
from Ui.Utility.Widget import DateEdit
from Model.DbTableModel.FleshModel import FleshModel


class FleshAdderWindow(BaseMainWindow, BaseMessageBoxWindow, BaseAdderWindow):
    def __init__(self, parent=None):
        super(FleshAdderWindow, self).__init__(parent)

        self.resize(250, 150)
        self.setWindowTitle("Flesh Adder")

    def _init_layout(self):
        self._init_input_layout()
        self._init_message_box()
        self._init_footer()

    def _init_input_layout(self):
        self.input_layout = QFormLayout()
        input_layout = self.input_layout
        self.central_layout.addLayout(input_layout)

        input_layout.setSpacing(10)

        self.date_field = DateEdit()
        input_layout.addRow("Date:", self.date_field)
        self.count_field = QLineEdit()
        input_layout.addRow("Count:", self.count_field)

    def show(self):
        super(FleshAdderWindow, self).show()
        self.reset_values()

    def reset_values(self):
        self.date_field.setDate(QDate.currentDate())
        self.count_field.setText("1.0")
        self.count_field.setValidator(QDoubleValidator(0, 10, 1, notation=QDoubleValidator.StandardNotation))
        self.message_box.clear()

    def add(self):
        date = self.date_field.get_date()
        count = float(self.count_field.text())

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
