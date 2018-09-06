#!/usr/bin/env python
# -*- coding: utf-8 -*-
import sys

from Ui.Utility import *
from Ui.SleepWindow import SleepAdderWindow
from Ui.FleshWindow import FleshAdderWindow


class MainWindow(BaseMainWindow):
    def __init__(self):
        super(MainWindow, self).__init__()

        self.resize(600, 150)
        self.move(600, 150)
        self.setWindowTitle("Life Recorder")

    def _init_layout(self):
        self._init_adder()
        self._init_footer()

    def _init_adder(self):
        self.record_adder_box = QGroupBox("Record Adder")
        record_adder_box = self.record_adder_box
        self.central_layout.addWidget(record_adder_box)

        layout = QHBoxLayout()
        record_adder_box.setLayout(layout)

        flesh_btn = QPushButton("&Flesh")
        layout.addWidget(flesh_btn)
        flesh_btn.setSizePolicy(QSizePolicy.Minimum, QSizePolicy.Minimum)
        flesh_btn.clicked.connect(FleshAdderWindow(self).show)

        sleep_btn = QPushButton("&Sleep")
        layout.addWidget(sleep_btn)
        sleep_btn.setSizePolicy(QSizePolicy.Minimum, QSizePolicy.Minimum)
        sleep_btn.clicked.connect(SleepAdderWindow(self).show)

    def _init_footer(self):
        self.add_h_line()

        self.footer_box = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)

        footer_box = self.footer_box
        self.central_layout.addWidget(footer_box)

        footer_box.accepted.connect(self.accept)
        footer_box.rejected.connect(self.reject)

    def accept(self):
        self.close()

    def reject(self):
        self.close()


if __name__ == "__main__":
    app = QApplication(sys.argv)

    window = MainWindow()
    window.show()

    app.exec_()
