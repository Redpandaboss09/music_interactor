import json
from functools import lru_cache
from pathlib import Path

from PySide6.QtCore import QAbstractListModel, Qt, QModelIndex, QByteArray
from PySide6.QtGui import QIcon, QPixmap
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
        self._icon_cache: dict[Path, QIcon] = {}

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

        if role == Qt.DecorationRole:
            cover = _find_cover(album_dir)
            if cover:
                icon = self._icon_cache.get(cover)
                if icon is None:
                    pm = QPixmap(cover)
                    pm = pm.scaledToHeight(180, Qt.SmoothTransformation)
                    icon = QIcon(pm)
                    self._icon_cache[cover] = icon
                return icon
            return None

        if role in (Qt.DisplayRole, Roles.TitleRole):
            return meta.get("album_title") or album_dir.name
        if role == Roles.IdRole:
            return meta.get("album_id")
        if role == Roles.DirRole:
            return str(album_dir)

        return None

    def load(self):
        self.beginResetModel()
        self._dirs = self.service.list_albums()
        self.endResetModel()

    def album_id_at(self, row: int) -> str | None:
        if 0 <= row < len(self._dirs):
            return _peek_album_meta(self._dirs[row].get("album_id"))
        return None

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

def _find_cover(album_dir: Path) -> Path | None:
    path = album_dir / "cover.jpg"
    if path.exists():
        return path
    return None
