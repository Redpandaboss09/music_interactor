import json
from functools import lru_cache
from pathlib import Path

from PySide6.QtCore import QAbstractListModel, Qt, QModelIndex, QByteArray
from ...media.service import MediaService

class Roles:
    TitleRole = Qt.UserRole + 1
    IdRole = Qt.UserRole + 2
    DirRole = Qt.UserRole + 3

class AlbumListModel(QAbstractListModel):
    def __init__(self, media_service: MediaService, parent=None):
        super().__init__(parent)
        self.service = media_service
        self._dirs: list[Path] = []

    def roleNames(self):
        return {
            Qt.DisplayRole: QByteArray(b'display'),
            Roles.TitleRole: QByteArray(b'title'),
            Roles.IdRole: QByteArray(b'album_id'),
            Roles.DirRole: QByteArray(b'album_dir'),
        }

    def rowCount(self, parent=QModelIndex()):
        return 0 if parent.isValid() else len(self._dirs)

    def data(self, index, role=Qt.DisplayRole):
        if not index.isValid():
            return None

        album_dir = self._dirs[index.row()]
        meta = _peek_album_meta(album_dir)

        if role in (Qt.DisplayRole, Roles.TitleRole):
            return meta.get("album_title") or album_dir.name
        if role == Roles.IdRole:
            return meta.get("album_id")
        if role == Roles.DirRole:
            return str(album_dir)

        # TODO CoverPath?

        return None

    def load(self):
        self.beginResetModel()
        self._dirs = self.service.list_albums()
        self.endResetModel()

    def album_id_at(self, row: int) -> str | None:
        return self._albums[row]["album_id"] if 0 <= row < len(self._albums) else None

@lru_cache(maxsize=512)
def _peek_album_meta(album_dir: Path) -> dict:
    """ Cached read of a few fields from album.json. """
    try:
        data = json.loads((album_dir / "album.json").read_text(encoding="utf-8"))
        return {
            "album_id": data.get("album_id"),
            "album_title": data.get("album_title") or data.get("album") or album_dir.name,
        }
    except Exception:
        return {"album_id": None, "album_title": album_dir.name}
