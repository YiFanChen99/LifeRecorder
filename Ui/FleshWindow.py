#!/usr/bin/env python
# -*- coding: utf-8 -*-
import sys
from PyQt5.QtCore import QDate
from PyQt5.QtGui import QDoubleValidator

from Ui.Utility.Window import *
from Ui.Utility.Widget import DateEdit
from Model.DbTableModel.FleshModel import FleshUtility


class FleshAdderWindow(SimpleAdderWindow):
    def __init__(self, parent=None):
        super().__init__(parent)

        self.resize(250, 150)
        self.setWindowTitle("Flesh Adder")

    def _create_main_panel(self):
        return FleshAdderPanel(self)


class FleshAdderPanel(QWidget):
    def __init__(self, owner):
        super().__init__()
        self.owner = owner
        self._init_layout()

    def _init_layout(self):
        layout = QFormLayout()
        self.setLayout(layout)

        layout.setSpacing(10)

        self.date_field = DateEdit()
        layout.addRow("Date:", self.date_field)
        self.count_field = QLineEdit()
        layout.addRow("Count:", self.count_field)

    def reset_values(self):
        self.date_field.setDate(QDate.currentDate())
        self.count_field.setText("1.0")
        self.count_field.setValidator(QDoubleValidator(0, 10, 1, notation=QDoubleValidator.StandardNotation))

    def add(self):
        date = self.date_field.get_date()
        count = float(self.count_field.text())

        try:
            result = FleshUtility.add(date, count)
        except ValueError as ex:
            self.owner.message_box.setText("Failed. (ValueError: %s)" % str(ex))
        else:
            self.owner.message_box.setText("{0}:  +{1}  -->  {2}\nWeek: {3}.  (Last week: {4})".format(
                date, count, result['day'], result['week'], result['last_week']))


if __name__ == "__main__":
    app = QApplication(sys.argv)

    window = FleshAdderWindow()
    window.show()

    app.exec_()
