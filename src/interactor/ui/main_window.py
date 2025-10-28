from PySide6.QtCore import Qt, Signal, QSize
from PySide6.QtWidgets import QMainWindow, QWidget, QSplitter, QStackedWidget, QSizePolicy, QVBoxLayout

from ..core.config import Settings
from .widgets.player_panel import PlayerPanel
from .pages.home_page import HomePage
from .pages.album_page import AlbumPage

class MainWindow(QMainWindow):
    play_requested = Signal(str, int) # album_id, track_index
    open_album_requested = Signal(str)
    back_to_home_requested = Signal()

    def __init__(self, settings: Settings, parent=None):
        super().__init__(parent)
        self.settings = settings
        self.setWindowTitle("Music Interactor")
        self.resize(1920, 720)

        # Splitter screen into 3 panels
        split = QSplitter(Qt.Orientation.Horizontal, self)
        split.setChildrenCollapsible(False)
        self.setCentralWidget(split)

        # Left Panel
        self.pages = QStackedWidget(split)
        self.home = HomePage(settings)
        self.album = AlbumPage(settings)

        self.pages.addWidget(self.home) # index 0
        self.pages.addWidget(self.album) # index 1
        self.pages.setCurrentIndex(0)

        # Center Panel (divider, will be empty for now
        self.mid_spacer = QWidget(split)
        self.mid_spacer.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Preferred)
        self.mid_spacer.setMinimumWidth(1)

        # Right Panel
        self.player = PlayerPanel(settings)
        split.addWidget(self.pages)
        split.addWidget(self.mid_spacer)
        split.addWidget(self.player)
        split.setSizes([1280, 12, 628])

        # Wire signals
        self.home.open_album_requested.connect(self._open_album)
        self.album.back_requested.connect(self._back_home)
        self.album.play_requested.connect(self._play)

        self.play_requested.connect(self.player.on_play_requested)

def _open_album(self, album_id: str):
    self.album.load_album(album_id)
    self.pages.setCurrentIndex(1)

def _back_home(self):
    self.pages.setCurrentIndex(0)

def _play(self, album_id: str, track_idx: int):
    self.play_requested.emit(album_id, track_idx)
