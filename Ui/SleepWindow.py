#!/usr/bin/env python
# -*- coding: utf-8 -*-
import sys
import datetime
from PyQt5.QtWidgets import *
from PyQt5.QtCore import QDate

from Ui.Utility import BaseAdderWindow, AlignHCLabel
from ModelUtility import Utility
from Model.SleepModel import SleepModel


class SleepAdderWindow(BaseAdderWindow):
    def __init__(self, parent=None):
        super(SleepAdderWindow, self).__init__(parent)

        self.resize(400, 150)
        self.setWindowTitle("Sleep Adder")

    def _init_layout(self):
        self.input_layout = QVBoxLayout()
        input_layout = self.input_layout
        self.central_layout.addLayout(input_layout)

        date_layout = QHBoxLayout()
        time_layout = QHBoxLayout()
        input_layout.addLayout(date_layout)
        input_layout.addLayout(time_layout)

        ''' date_layout '''
        date_label = AlignHCLabel("Date:")
        date_layout.addWidget(date_label, 1)
        self.date = QLineEdit()
        date_layout.addWidget(self.date, 3)
        date_layout.addStretch(1)

        ''' time_layout '''
        time_layout.addWidget(AlignHCLabel("Start:"))
        self.start_hour = QSpinBox()
        time_layout.addWidget(self.start_hour)
        self.start_minute = QSpinBox()
        time_layout.addWidget(self.start_minute)

        time_layout.addWidget(AlignHCLabel("End:"))
        self.end_hour = QSpinBox()
        time_layout.addWidget(self.end_hour)
        self.end_minute = QSpinBox()
        time_layout.addWidget(self.end_minute)

    def show(self):
        super(SleepAdderWindow, self).show()
        self.reset_values()

    def reset_values(self):
        self.date.setText(str(QDate.currentDate().toPyDate()))
        self.start_hour.setValue(1)
        self.start_minute.setValue(0)
        self.end_hour.setValue(13)
        self.end_minute.setValue(30)
        self.message_box.clear()

    def add(self):
        date = datetime.datetime.strptime(self.date.text(), "%Y-%m-%d").date()
        delta_start = datetime.timedelta(hours=self.start_hour.value(), minutes=self.start_minute.value())
        delta_end = datetime.timedelta(hours=self.end_hour.value(), minutes=self.end_minute.value())

        try:
            feedback = SleepModel.create_by_date(date, delta_start, delta_end)
            self.message_box.setText("{0}:  +{1}  -->  {2}".format(
                feedback['date'], Utility.str_timedelta(feedback['growth']),
                Utility.str_timedelta(feedback['after'])))
        except ValueError as ex:
            self.message_box.setText("Failed. (ValueError: %s)" % str(ex))


if __name__ == "__main__":
    app = QApplication(sys.argv)

    window = SleepAdderWindow()
    window.show()

    app.exec_()
