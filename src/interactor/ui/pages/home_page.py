from PySide6.QtCore import Signal
from PySide6.QtWidgets import QWidget, QVBoxLayout, QLabel, QListView
from ..models.album_list_model import AlbumListModel
from ..widgets.hero_widget import HeroWidget

class HomePage(QWidget):
    open_album_requested = Signal(str) # album_id

    def __init__(self, settings, parent=None):
        super().__init__(parent)
        self.settings = settings

        layout = QVBoxLayout(self)
        self.hero = HeroWidget(settings)
        layout.addWidget(self.hero)

        title = QLabel('Library')
        title.setProperty('h2', True)
        layout.addWidget(title)

        self.list = QListView()
        self.list.setViewMode(QListView.ViewMode.IconMode)
        self.list.setResizeMode(QListView.ResizeMode.Adjust)
        self.list.setWrapping(True)
        self.list.setSpacing(12)
        self.list.setUniformItemSizes(True)
        layout.addWidget(self.list, 1)

        self.model = AlbumListModel(settings)
        self.list.setModel(self.model)

        self.list.clicked.connect(self._open_selected)

        self.hero.open_album_requested.connect(self.open_album_requested)

def _open_selected(self, idx):
    album_id = self.model.album_id_at(idx.row())
    if album_id:
        self.open_album_requested.emit(album_id)
