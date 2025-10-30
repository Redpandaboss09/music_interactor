import random
from PySide6.QtCore import Signal, Qt, QSize
from PySide6.QtGui import QPixmap
from PySide6.QtWidgets import QWidget, QVBoxLayout, QLabel, QPushButton

from ...media.service import MediaService

class HeroWidget(QWidget):
    open_album_requested = Signal(str)

    def __init__(self, settings, parent=None):
        super().__init__(parent)
        self.service = MediaService(settings)
        self._current_id: str | None = None

        layout = QVBoxLayout(self)

        self.cover = QLabel(self)
        self.cover.setAlignment(Qt.AlignCenter)
        self.cover.setMinimumHeight(180)

        self.title = QLabel("")
        self.title.setAlignment(Qt.AlignCenter)
        self.title.setProperty("h1", True)

        self.open_button = QPushButton("Open")

        self.open_button.clicked.connect(self._emit_open)

        layout.addWidget(self.cover)
        layout.addWidget(self.title)
        layout.addWidget(self.open_button, 0, Qt.AlignCenter)

        self.refresh_random()

    def refresh_random(self):
        """ Pick a random album_id """
        album_ids = list(self.service._id_to_dir.keys())
        if not album_ids:
            self.title.setText("No Albums Found!")
            self.cover.clear()
            self._current_id = None
            return

        self._current_id = random.choice(album_ids)
        album = self.service.get_album(self._current_id)
        if not album:
            return

        self.title.setText(album.album_title)

        path = self.service.cover_path(self._current_id)
        if path:
            pm = QPixmap(str(path))
            if not pm.isNull():
                self.cover.setPixmap(pm.scaledToHeight(180, Qt.SmoothTransformation))

    def mousePressEvent(self, event):
        self._emit_open()

    def _emit_open(self):
        if self._current_id:
            self.open_album_requested.emit(self._current_id)
