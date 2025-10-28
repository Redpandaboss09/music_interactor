from PySide6.QtCore import Qt
from PySide6.QtWidgets import QWidget, QVBoxLayout, QLabel, QPushButton, QSlider

class PlayerPanel(QWidget):
    def __init__(self, settings, parent=None):
        super().__init__(parent)
        self.settings = settings

        layout = QVBoxLayout(self)
        self.art = QLabel("Album Art")
        self.art.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.art.setMinimumHeight(245)
        layout.addWidget(self.art)

        self.title = QLabel("Song Name")
        layout.addWidget(self.title)

        self.slider = QSlider(Qt.Orientation.Horizontal)
        layout.addWidget(self.slider)

        row = QWidget()
        row_1 = QVBoxLayout(row)
        row_1.setContentsMargins(0, 0, 0, 0)
        self.play = QPushButton("▶")
        row_1.addWidget(self.play)
        layout.addWidget(row)

    def on_play_requested(self, album_id: str, track_idx: int):
        # TODO CALL MEDIASERVICE
        self.title.setText("Song Name")