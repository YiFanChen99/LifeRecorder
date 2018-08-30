#!/usr/bin/env python
# -*- coding: utf-8 -*-
import sys
import datetime
from PyQt5.QtWidgets import *
from PyQt5.QtCore import QDate, QTime

from Ui.Utility import BaseMainWindow, AlignHCLabel
from Model.SleepModel import SleepModel, SleepDateViewModel


class SleepAdderWindow(BaseMainWindow):
    def __init__(self, parent=None):
        super(SleepAdderWindow, self).__init__(parent)

        self.resize(400, 150)
        self.setWindowTitle("Sleep Adder")

    def _init_layout(self):
        self._init_input_view()

    def _init_input_view(self):
        self.input_layout = QVBoxLayout()
        input_layout = self.input_layout
        self.central_layout.addLayout(input_layout)

        date_layout = QHBoxLayout()
        time_layout = QHBoxLayout()
        display_widget = QGroupBox()
        input_layout.addLayout(date_layout)
        input_layout.addLayout(time_layout)
        input_layout.addWidget(display_widget)

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

        ''' display_widget '''
        layout = QHBoxLayout()
        self.message = QLabel()
        layout.addWidget(self.message)
        display_widget.setLayout(layout)

    def _init_footer(self):
        footer_box = QDialogButtonBox(QDialogButtonBox.Reset | QDialogButtonBox.Save | QDialogButtonBox.Close)
        footer_box.button(QDialogButtonBox.Reset).clicked.connect(self.reset_input_view)
        footer_box.accepted.connect(self.add_sleep)
        footer_box.rejected.connect(self.close)

        self.central_layout.addWidget(footer_box)
        self.footer_box = footer_box

    def show(self):
        super(SleepAdderWindow, self).show()
        self.reset_input_view()

    def reset_input_view(self):
        self.date.setText(str(QDate.currentDate().toPyDate()))
        self.start_hour.setValue(QTime.currentTime().hour())
        self.start_minute.setValue(QTime.currentTime().minute())
        self.end_hour.setValue(QTime.currentTime().hour())
        self.end_minute.setValue(QTime.currentTime().minute())
        self.end_minute.setValue(QTime.currentTime().minute())
        self.message.clear()

    def add_sleep(self):
        date = datetime.datetime.strptime(self.date.text(), "%Y-%m-%d").date()
        time_start = datetime.time(self.start_hour.value(), self.start_minute.value())
        time_end = datetime.time(self.end_hour.value(), self.end_minute.value())

        duration_before = SleepDateViewModel.get_duration(date)
        SleepModel.create_by_date(date, time_start, time_end)
        duration_after = SleepDateViewModel.get_duration(date)
        self.display_message(date, duration_before, duration_after)

    def display_message(self, date, duration_before, duration_after):
        duration_growth = datetime.time(
            duration_after.hour - duration_before.hour,
            duration_after.minute - duration_before.minute)
        self.message.setText("{0}: {1} -> {2} (+{3})".format(
            date, duration_before.strftime('%H:%M'), duration_after.strftime('%H:%M'),
            duration_growth.strftime('%H:%M')))


if __name__ == "__main__":
    app = QApplication(sys.argv)

    window = SleepAdderWindow()
    window.show()

    app.exec_()
