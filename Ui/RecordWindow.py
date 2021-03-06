#!/usr/bin/env python
# -*- coding: utf-8 -*-
import sys
from PyQt5.QtWidgets import *
from PyQt5.QtCore import QDate

from Ui.Utility.Window import SimpleAdderWindow
from Ui.Utility.Widget import DateEdit, MapComboBox, RecordGroupComboBox
from Model.DbTableModel.RecordModel import RecordUtility, ExtraRecordType


class RecordAdderWindow(SimpleAdderWindow):
    def __init__(self, parent=None):
        super(RecordAdderWindow, self).__init__(parent)

        self.resize(250, 150)
        self.setWindowTitle("Record Adder")

    def _create_main_panel(self):
        return RecordAdderPanel(self)


class RecordAdderPanel(QWidget):
    def __init__(self, owner):
        super().__init__()
        self.owner = owner
        self._init_layout()

    def _init_layout(self):
        layout = QVBoxLayout()
        self.setLayout(layout)

        ''' Basic record '''
        form = QFormLayout()
        form.setSpacing(10)
        layout.addLayout(form)

        self.date = DateEdit()
        form.addRow("Date:", self.date)
        self.group = RecordGroupComboBox()
        form.addRow("Group:", self.group)

        ''' Extra record '''
        self.extra = ExtraRecordList(self)
        layout.addWidget(self.extra)

    def reset_values(self):
        self.date.setDate(QDate.currentDate())
        self.group.setCurrentData(3)  # 休閒娛樂
        self.reset_extra()

    def reset_extra(self):
        self.extra.reset_values()

    def add(self):
        date = self.date.get_date()
        group_id = self.group.currentData()
        extras = self.extra.get_values()

        try:
            basic = RecordUtility.Basic.create_with_extras(date, group_id, extras)
        except ValueError as ex:
            self.owner.message_box.setText("Failed. (ValueError: %s)" % str(ex))
        else:
            self.owner.message_box.setText("{0}, {1}:  {2}".format(
                date, basic.group_id.description, basic.joined_extra))
            self.reset_extra()


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
        self.btn_add.clicked.connect(lambda: self.add_field())
        self.toolbar_layout.addWidget(self.btn_add)

    def _init_field_layout(self):
        self.field_layout = QVBoxLayout()
        self.layout().addLayout(self.field_layout)

    def reset_values(self):
        for field in self.fields[:]:
            self.remove_field(field)

        self.add_field(ExtraRecordType.DESCRIPTION)
        self.add_field(ExtraRecordType.MAGNITUDE)
        self.add_field(ExtraRecordType.SCALE)

    def add_field(self, index_data=ExtraRecordType.DESCRIPTION):
        layout = QHBoxLayout()
        self.field_layout.addLayout(layout)

        key_field = MapComboBox(items_config=ExtraRecordType, default_index_data=index_data)
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
        return ((field[1].currentData(), field[2].text()) for field in self.fields if field[2].text())


class RecordGroupAdderWindow(SimpleAdderWindow):
    def __init__(self, parent=None):
        super().__init__(parent)

        self.resize(280, 150)
        self.setWindowTitle("Group Adder")

    def _create_main_panel(self):
        return RecordGroupAdderPanel(self)


class RecordGroupAdderPanel(QWidget):
    def __init__(self, owner):
        super().__init__()
        self.owner = owner
        self._init_layout()

    def _init_layout(self):
        layout = QVBoxLayout()
        self.setLayout(layout)

        form = QFormLayout()
        form.setSpacing(10)
        layout.addLayout(form)

        self.description = QLineEdit()
        form.addRow("Description:", self.description)
        self.parent_group = RecordGroupComboBox(with_root=True)
        form.addRow("Parent:", self.parent_group)

    def reset_values(self):
        self.reset_properties()
        self.parent_group.setCurrentData(3)

    def reset_properties(self):
        self.description.setText("")

    def add(self):
        description = self.description.text()
        parent_id = self.parent_group.currentData()

        try:
            group = RecordUtility.Group.add(description, parent_id)
        except ValueError as ex:
            self.owner.message_box.setText("Failed. (ValueError: %s)" % str(ex))
        else:
            self.owner.message_box.setText(
                "{0} has been created under {1}.".format(
                    group, self.parent_group.currentText()))

            self.reset_properties()
            self.parent_group.insert_item_by_group(group)


if __name__ == "__main__":
    app = QApplication(sys.argv)

    window = RecordGroupAdderWindow()
    window.show()

    app.exec_()
