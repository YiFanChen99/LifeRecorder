#!/usr/bin/env python
# -*- coding: utf-8 -*-
import sys
from PyQt5.QtCore import QDate

from Ui.Utility.Window import *
from Ui.Utility.Widget import DateEdit, MapComboBox
from Model.DbTableModel.RecordModel import RecordGroupModel, BasicRecordModel, ExtraRecordModel


class RecordAdderWindow(BaseMainWindow, BaseMessageBoxWindow, BaseAdderWindow):
    def __init__(self, parent=None):
        super(RecordAdderWindow, self).__init__(parent)

        self.resize(250, 150)
        self.setWindowTitle("Record Adder")

    def _init_layout(self):
        self._init_input_layout()
        self._init_message_box()
        self._init_footer()

    def _init_input_layout(self):
        self.input_layout = QVBoxLayout()
        input_layout = self.input_layout
        self.central_layout.addLayout(input_layout)

        ''' Basic record '''
        form = QFormLayout()
        form.setSpacing(10)
        self.input_layout.addLayout(form)

        self.date = DateEdit()
        form.addRow("Date:", self.date)
        self.group = MapComboBox(RecordGroupModel.get_id_description_map())
        form.addRow("Group:", self.group)

        ''' Extra record '''
        self.extra = ExtraRecordList(self)
        input_layout.addWidget(self.extra)

    def show(self):
        super(RecordAdderWindow, self).show()
        self.reset_values()

    def reset_values(self):
        self.date.setDate(QDate.currentDate())
        self.group.setCurrentIndex(2)  # 休閒娛樂
        self.extra.reset_values()
        self.message_box.clear()

    def reset_values_partially(self):
        self.group.setCurrentIndex(2)  # 休閒娛樂
        self.extra.reset_values()

    def add(self):
        date = self.date.get_date()
        group_id = self.group.currentData()
        extras = self.extra.get_values()

        try:
            BasicRecordModel.create_with_extras(date, group_id, extras)
        except ValueError as ex:
            self.message_box.setText("Failed. (ValueError: %s)" % str(ex))
        else:
            self.message_box.setText("{0}, {1}:  +1  -->  {2}".format(
                date, self.group.currentText(), BasicRecordModel.get_count(date, group_id)))
            self.reset_values_partially()


class ExtraRecordList(QWidget):
    def __init__(self, parent=None):
        super(ExtraRecordList, self).__init__(parent)
        self.fields = []
        self._init_layout()

    def _init_layout(self):
        self.setLayout(QVBoxLayout())
        self._init_toolbar_layout()
        self._init_field_layout()

    def _init_toolbar_layout(self):
        self.toolbar_layout = QHBoxLayout()
        self.layout().addLayout(self.toolbar_layout)

        self.btn_add = QPushButton("Add")
        self.btn_add.clicked.connect(self.add_field)
        self.toolbar_layout.addWidget(self.btn_add)

    def _init_field_layout(self):
        self.field_layout = QVBoxLayout()
        self.layout().addLayout(self.field_layout)

    def reset_values(self):
        for field in self.fields[:]:
            self.remove_field(field)
        self.add_field()

    def add_field(self):
        layout = QHBoxLayout()
        self.field_layout.addLayout(layout)

        key_field = QComboBox()
        key_field.addItems(ExtraRecordModel.KEYS)
        value_field = QLineEdit()

        fields = (layout, key_field, value_field)

        remove = QToolButton(text="-")
        remove.clicked.connect(lambda: self.remove_field(fields))

        layout.addWidget(key_field, 1)
        layout.addWidget(value_field, 2)
        layout.addWidget(remove)

        self.fields.append(fields)

    def remove_field(self, fields):
        self.field_layout.removeItem(fields[0])
        self.fields.remove(fields)

    def get_values(self):
        return ((field[1].currentText(), field[2].text()) for field in self.fields if field[2].text())


if __name__ == "__main__":
    app = QApplication(sys.argv)

    window = RecordAdderWindow()
    window.show()

    app.exec_()
