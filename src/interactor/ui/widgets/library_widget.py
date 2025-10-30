from PySide6.QtCore import Qt, Signal, QSize
from PySide6.QtWidgets import QWidget, QVBoxLayout, QLabel, QLineEdit, QScroller, QListView
from PySide6.QtGui import QResizeEvent

class LibraryWidget(QWidget):
    album_activated = Signal(str)

    def __init__(self, title="Library", parent=None):
        super().__init__(parent)

        view = QVBoxLayout(self)
        view.setContentsMargins(0, 0, 0, 0)
        view.setSpacing(8)

        self.title = QLabel(title)
        self.title.setProperty("h2", True)
        view.addWidget(self.title, 0, Qt.AlignLeft)

        self.view = QListView()
        self.view.setViewMode(QListView.IconMode)
        self.view.setFlow(QListView.LeftToRight)
        self.view.setWrapping(True)
        self.view.setResizeMode(QListView.Adjust)
        self.view.setUniformItemSizes(True)
        self.view.setMovement(QListView.Static)
        self.view.setSpacing(12)
        self.view.setSelectionRectVisible(False)
        self.view.setVerticalScrollMode(QListView.ScrollPerPixel)
        self.view.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        view.addWidget(self.view, 1)

        QScroller.grabGesture(self.view.viewport(), QScroller.LeftMouseButtonGesture)

        self.view.activated.connect(self._emit_selection)
        self._tileW = 180
        self._tileH = 220
        self._update_grid_size()

    def set_model(self, model):
        self.view.setModel(model)

    def _emit_selection(self, index):
        album_id = index.data(Qt.UserRole + 1)
        if not album_id:
            album_id = index.data(Qt.DisplayRole)
        if album_id:
            self.album_activated.emit(album_id)

    def resizeEvent(self, event: QResizeEvent):
        super().resizeEvent(event)
        self._update_grid_size()

    def _update_grid_size(self):
        self.view.setIconSize(QSize(self._tileW, self._tileW))
        self.view.setGridSize(QSize(self._tileW + 20, self._tileH))