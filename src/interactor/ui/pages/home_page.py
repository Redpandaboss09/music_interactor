from PySide6.QtCore import Signal
from PySide6.QtWidgets import QWidget, QVBoxLayout, QLabel, QListView
from ..models.album_list_model import AlbumListModel
from ..widgets.hero_widget import HeroWidget
from ..widgets.library_widget import LibraryWidget


class HomePage(QWidget):
    open_album_requested = Signal(str) # album_id

    def __init__(self, settings, parent=None):
        super().__init__(parent)
        self.settings = settings

        layout = QVBoxLayout(self)
        layout.setContentsMargins(12, 12, 12, 12)
        layout.setSpacing(12)

        self.hero = HeroWidget(settings)
        layout.addWidget(self.hero, 7)

        self.library = LibraryWidget(title="Library")
        layout.addWidget(self.library, 3)

        self.model = AlbumListModel(settings)
        self.library.set_model(self.model)

        self.hero.open_album_requested.connect(self.open_album_requested)
        self.library.album_activated.connect(self.open_album_requested)

    def _open_selected(self, idx):
        album_id = self.model.album_id_at(idx.row())
        if album_id:
            self.open_album_requested.emit(album_id)
