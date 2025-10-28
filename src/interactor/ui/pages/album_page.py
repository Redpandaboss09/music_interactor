from PySide6.QtCore import Signal
from PySide6.QtWidgets import QWidget, QVBoxLayout, QPushButton
from ..models.track_table_model import TrackTableModel
from ..widgets.track_table import TrackTable

class AlbumPage(QWidget):
    back_requested = Signal()
    play_requested = Signal(str, int) # album_id, row

    def __init__(self, settings, parent=None):
        super().__init__(parent)
        self.settings = settings
        self.album_id = ''

        layout = QVBoxLayout(self)
        back = QPushButton("← Library")
        back.clicked.connect(self.back_requested)
        layout.addWidget(back)

        self.table = TrackTable()
        layout.addWidget(self.table, 1)

        self.table.play_requested.connect(self._play_row)

        self.model = TrackTableModel(settings)
        self.table.setModel(self.model)

def load_album(self, album_id: str):
        self.album_id = album_id
        self.model.load_album(album_id)

def _play_row(self, row: int):
        self.play_requested.emit(self.album_id, row)