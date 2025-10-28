from PySide6.QtCore import QAbstractTableModel, Qt, QModelIndex
from ...media.service import MediaService

class TrackTableModel(QAbstractTableModel):
    HEADERS = ["#", "Title", "Artist", "Duration", "Explicit"]

    def __init__(self, settings, parent=None):
        super().__init__(parent)
        self.settings = settings
        self._tracks = []
        self._album_id = ""

    def load_album(self, album_id: str):
        self.beginResetModel()
        self._album_id = album_id
        # self._tracks = MediaService. # TODO get_album_tracks
        self._tracks = []
        self.endResetModel()

    def rowCount(self, parent=QModelIndex()):
        return len(self._tracks)

    def columnCount(self, parent=QModelIndex()):
        return len(self.HEADERS)

    def headerData(self, section, orientation, role):
        if orientation == Qt.Orientation.Horizontal and role == Qt.ItemDataRole.DisplayRole.DisplayRole:
            return self.HEADERS[section]
        return None

    # TODO VERIFY WORKS
    def data(self, index, role):
        if not index.isValid(): return None

        track = self._tracks[index.row()]
        column = index.column()
        if role == Qt.ItemDataRole.DisplayRole:
            if column == 0: return track["track"]
            if column == 1: return track["track_title"]
            if column == 2: return ", ".join(track["track_artist"])
            if column == 3: return self._fmt(track["duration"])
            if column == 4: return "E" if track["explicit"] else ""

        return None

    @staticmethod
    def _fmt(sec: float) -> str:
        m, s = divmod(int(round(sec)), 60)
        return f"{m}:{s:02d}"