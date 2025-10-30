import random
from PySide6.QtCore import Signal, Qt
from PySide6.QtGui import QPixmap, QIcon
from PySide6.QtWidgets import QWidget, QVBoxLayout, QLabel, QPushButton, QHBoxLayout

from ...media.service import MediaService

class HeroWidget(QWidget):
    open_album_requested = Signal(str)

    def __init__(self, settings, parent=None):
        super().__init__(parent)
        self.service = MediaService(settings)
        self._current_id: str | None = None

        row = QHBoxLayout(self)
        row.setContentsMargins(0, 0, 0, 0)
        row.setSpacing(16)

        # Album art side (left)
        self.open_button = QPushButton()
        self.open_button.clicked.connect(self._emit_open)
        row.addWidget(self.open_button, 0, Qt.AlignLeft | Qt.AlignVCenter)

        # Small info blurb (right)
        info_col = QVBoxLayout()
        info_col.setSpacing(8)

        self.title = QLabel("")
        self.title.setProperty("h1", True)
        self.title.setAlignment(Qt.AlignLeft | Qt.AlignVCenter)

        info_col.addStretch()
        info_col.addWidget(self.title, 0, Qt.AlignLeft)
        info_col.addStretch()

        row.addLayout(info_col, 1)

        self.refresh_random()

    def refresh_random(self):
        """ Pick a random album_id """
        album_ids = list(self.service.get_id_to_dir_keys())
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
                pm = pm.scaledToHeight(320, Qt.SmoothTransformation)
                icon = QIcon(pm)
                self.open_button.setIcon(icon)
                self.open_button.setIconSize(pm.size())

    def mousePressEvent(self, event):
        self._emit_open()

    def _emit_open(self):
        if self._current_id:
            self.open_album_requested.emit(self._current_id)
