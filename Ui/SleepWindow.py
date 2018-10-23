#!/usr/bin/env python
# -*- coding: utf-8 -*-
import sys
import datetime
from PyQt5.QtCore import QDate

from Ui.Utility.Window import *
from Ui.Utility.Widget import AlignHCLabel, DateEdit
from Model import TimeUtility
from Model.DbTableModel.SleepModel import SleepUtility


class SleepAdderWindow(SimpleAdderWindow):
    def __init__(self, parent=None):
        super().__init__(parent)

        self.resize(400, 150)
        self.setWindowTitle("Sleep Adder")

    def _create_main_panel(self):
        return SleepAdderPanel(self)


class SleepAdderPanel(QWidget):
    def __init__(self, owner):
        super().__init__()
        self.owner = owner
        self._init_layout()

    def _init_layout(self):
        layout = QVBoxLayout()
        self.setLayout(layout)

        date_layout = QHBoxLayout()
        time_layout = QHBoxLayout()
        layout.addLayout(date_layout)
        layout.addLayout(time_layout)

        ''' date_layout '''
        date_label = AlignHCLabel("Date:")
        date_layout.addWidget(date_label, 1)
        self.date = DateEdit()
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

    def reset_values(self):
        self.date.setDate(QDate.currentDate())
        self.start_hour.setValue(1)
        self.start_minute.setValue(0)
        self.end_hour.setValue(13)
        self.end_minute.setValue(30)

    def add(self):
        date = self.date.get_date()
        delta_start = datetime.timedelta(hours=self.start_hour.value(), minutes=self.start_minute.value())
        delta_end = datetime.timedelta(hours=self.end_hour.value(), minutes=self.end_minute.value())

        try:
            feedback = SleepUtility.create_by_date(date, delta_start, delta_end)
            self.owner.message_box.setText("{0}:  +{1}  -->  {2}".format(
                feedback['date'], TimeUtility.str_timedelta(feedback['growth']),
                TimeUtility.str_timedelta(feedback['after'])))
        except ValueError as ex:
            self.owner.message_box.setText("Failed. (ValueError: %s)" % str(ex))


if __name__ == "__main__":
    app = QApplication(sys.argv)

    window = SleepAdderWindow()
    window.show()

    app.exec_()
