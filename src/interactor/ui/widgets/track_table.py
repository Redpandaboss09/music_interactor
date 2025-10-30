from PySide6.QtCore import Signal
from PySide6.QtWidgets import QTableView

class TrackTable(QTableView):
    play_requested = Signal(int)  # row

    def __init__(self, parent=None):
        super().__init__(parent)
        self.doubleClicked.connect(lambda idx: self.play_requested.emit(idx.row()))
        self.setSelectionBehavior(QTableView.SelectionBehavior.SelectRows)
        self.setSelectionMode(QTableView.SelectionMode.SingleSelection)
        self.setEditTriggers(QTableView.EditTrigger.NoEditTriggers)
        self.horizontalHeader().setStretchLastSection(True)