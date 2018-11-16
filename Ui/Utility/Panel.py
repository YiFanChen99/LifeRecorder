from PyQt5.QtGui import QCursor
from PyQt5.QtWidgets import *

from Ui.Utility.Widget import HBoxMenu


class PanelChangeable(object):
    def __init__(self):
        self.current_panel = None
        super().__init__()

    def _init_panels(self):
        self.panels = tuple(self._create_panels())

        for panel in self.panels:
            self.layout().addWidget(panel)
            panel.hide()

        self.change_panel(self.menu.default_index)

    def _create_panels(self):
        raise NotImplementedError

    def change_panel(self, index):
        if self.current_panel:
            self.current_panel.hide()

        self.current_panel = self.panels[index]
        self.current_panel.show()


class BaseVBoxPanel(QWidget):
    def __init__(self, owner):
        super().__init__()
        self.owner = owner
        self.setLayout(QVBoxLayout())
        self._init_layout()

    def _init_layout(self):
        raise NotImplementedError()


class HBoxMenuable(QWidget):
    def _init_menu(self, menu_config):
        if not isinstance(self.layout(), QVBoxLayout):
            raise ValueError("HBoxMenuable should be instance of QVBoxLayout.")

        self.menu = HBoxMenu(self, menu_config)
        self.layout().addWidget(self.menu)


class RightClickable(QWidget):
    def __init__(self, *args):
        super().__init__(*args)
        self._init_right_click_menu()

    def _init_right_click_menu(self):
        self.right_click_menu = QMenu(self)
        self._init_right_click_menu_actions()

    def _init_right_click_menu_actions(self):
        raise NotImplementedError

    def contextMenuEvent(self, event):
        self.right_click_menu.popup(QCursor.pos())
        super().contextMenuEvent(event)


class TableViewable(QWidget):
    PROXY_MODEL_CLASS = None

    def _init_table_view(self):
        if not self.PROXY_MODEL_CLASS:
            raise NotImplementedError("PROXY_MODEL_CLASS")
        if not isinstance(self.layout(), QBoxLayout):
            raise ValueError("TableViewable should be instance of QBoxLayout.")

        table_view = QTableView()
        self.table_view = table_view
        self.layout().addWidget(table_view)

        self.table_model = self.PROXY_MODEL_CLASS()
        table_view.setModel(self.table_model)

        table_view.resizeColumnsToContents()
        table_view.setSortingEnabled(True)
        table_view.setSelectionBehavior(QAbstractItemView.SelectRows)
        table_view.setSelectionMode(QAbstractItemView.SingleSelection)


class Addable(object):
    ADDER_WINDOW_CLASS = None

    def __init__(self, *args):
        super().__init__(*args)
        self._init_action_add()

    def _init_action_add(self):
        self.action_add = QAction('Adder', self)
        if self.ADDER_WINDOW_CLASS:
            self.action_add.triggered.connect(self.ADDER_WINDOW_CLASS(self).show)
            self.action_add.setEnabled(True)
        else:
            self.action_add.setEnabled(False)
