from PyQt5.QtWidgets import *
from PyQt5.QtCore import QSize

from Model.TableViewModel import ProxyModel, FilterProxyModel
from Model.TableViewModel import SleepTableModel, RecordGroupTableModel
from Model.TableViewModel import SleepDurationTableModel, FleshDurationTableModel, RecordDurationTableModel
from Ui.FleshWindow import FleshAdderWindow
from Ui.SleepWindow import SleepAdderWindow
from Ui.RecordWindow import RecordAdderWindow
from Ui.Utility.Panel import BaseVBoxPanel, TableViewable, RightClickable, Addable
from Ui.Utility.Widget import DurationGroup, DateFilterComBox


class BaseMainTablePanel(BaseVBoxPanel, TableViewable, RightClickable, Addable):
    PROXY_MODEL_CLASS = ProxyModel
    SOURCE_MODEL = None
    ADDER_WINDOW_CLASS = None

    def __init__(self, owner):
        if self.SOURCE_MODEL is None:
            raise ValueError("SOURCE_MODEL")
        super().__init__(owner)
        self.init_source_model()

    def _init_layout(self):
        self._init_table_view()

    def _init_table_view(self):
        super()._init_table_view()
        self.table_view.setColumnHidden(0, self.SOURCE_MODEL.HIDDEN_COLUMN_0)

    def _init_right_click_menu_actions(self):
        menu = self.right_click_menu
        menu.addAction(self.action_add)

    def init_source_model(self):
        self.table_model.beginResetModel()
        self.table_model.setSourceModel(self.SOURCE_MODEL)
        self.table_model.endResetModel()


class SleepTablePanel(BaseMainTablePanel):
    SOURCE_MODEL = SleepTableModel()
    ADDER_WINDOW_CLASS = SleepAdderWindow


class RecordGroupTablePanel(BaseMainTablePanel):
    SOURCE_MODEL = RecordGroupTableModel()
    ADDER_WINDOW_CLASS = None


class DurationTablePanel(BaseMainTablePanel):
    PROXY_MODEL_CLASS = FilterProxyModel
    SOURCE_MODEL = None
    ADDER_WINDOW_CLASS = None

    def _init_layout(self):
        self._init_menu_bar()
        self._init_table_view()

    def _init_menu_bar(self):
        self.menu_bar = QHBoxLayout()
        self.layout().addLayout(self.menu_bar)

        btn_add = QToolButton()
        btn_add.setDefaultAction(self.action_add)
        btn_add.sizeHint = lambda: QSize(40, 23)
        btn_add.setSizePolicy(QSizePolicy.Preferred, QSizePolicy.Maximum)
        self.menu_bar.addWidget(btn_add, 1)

        self.duration_group = DurationGroup(
            self.set_duration, default_checked=self.SOURCE_MODEL.DEFAULT_DURATION)
        self.menu_bar.addWidget(self.duration_group, 7)

        self.date_filter = DateFilterComBox(
            self.set_date_filter, default_index=self.SOURCE_MODEL.DEFAULT_DATE_FILTER)
        self.menu_bar.addWidget(self.date_filter, 2)

    def set_duration(self, duration):
        self.table_model.set_duration(duration)

    def set_date_filter(self, d_filter):
        self.table_model.set_date_filter(d_filter)

    def _init_table_view(self):
        super()._init_table_view()

    def _init_right_click_menu_actions(self):
        menu = self.right_click_menu
        menu.addAction(self.action_add)

    def init_source_model(self):
        super().init_source_model()

        self.set_date_filter(self.SOURCE_MODEL.DEFAULT_DATE_FILTER)


class SleepDurationTablePanel(DurationTablePanel):
    SOURCE_MODEL = SleepDurationTableModel()
    ADDER_WINDOW_CLASS = SleepAdderWindow


class FleshDurationTablePanel(DurationTablePanel):
    SOURCE_MODEL = FleshDurationTableModel()
    ADDER_WINDOW_CLASS = FleshAdderWindow


class RecordDurationTablePanel(DurationTablePanel):
    SOURCE_MODEL = RecordDurationTableModel()
    ADDER_WINDOW_CLASS = RecordAdderWindow
