from PySide6.QtCore import Signal, Qt
from PySide6.QtWidgets import QWidget, QVBoxLayout, QLabel, QListView, QSplitter
from ..models.album_list_model import AlbumListModel
from ..widgets.hero_widget import HeroWidget
from ..widgets.library_widget import LibraryWidget
from ...media.service import MediaService


class HomePage(QWidget):
    open_album_requested = Signal(str) # album_id

    def __init__(self, settings, parent=None):
        super().__init__(parent)
        self.settings = settings
        self.media = MediaService(settings)

        layout = QVBoxLayout(self)
        layout.setContentsMargins(12, 12, 12, 12)
        layout.setSpacing(12)

        splitter = QSplitter(Qt.Vertical)
        layout.addWidget(splitter)

        self.hero = HeroWidget(settings)
        self.library = LibraryWidget(title="Library")

        splitter.addWidget(self.hero)
        splitter.addWidget(self.library)

        splitter.setStretchFactor(0, 6)
        splitter.setStretchFactor(1, 4)
        splitter.setOpaqueResize(False)
        splitter.setSizes([600, 400])

        self.model = AlbumListModel(self.media)
        self.library.set_model(self.model)
        self.model.load()

        self.hero.open_album_requested.connect(self.open_album_requested)
        self.library.album_activated.connect(self.open_album_requested)

    def _open_selected(self, idx):
        album_id = self.model.album_id_at(idx.row())
        if album_id:
            self.open_album_requested.emit(album_id)
