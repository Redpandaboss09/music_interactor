from PySide6.QtCore import QAbstractListModel, Qt, QModelIndex
from ...media.service import MediaService

class AlbumListModel(QAbstractListModel):
    def __init__(self, settings, parent=None):
        super().__init__(parent)
        self.settings = settings
        self.service = MediaService(settings)
        self._albums = self.service.list_albums()

    def rowCount(self, parent=QModelIndex()):
        return len(self._albums)

    def data(self, index, role):
        if not index.isValid():
            return None

        item = self._albums[index.row()]
        if role == Qt.ItemDataRole.DisplayRole:
            return item.get("album_title")

        # TODO CoverPath?

        return None

    def album_id_at(self, row: int) -> str | None:
        return self._albums[row]["album_id"] if 0 <= row < len(self._albums) else None