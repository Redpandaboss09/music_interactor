from PySide6.QtCore import QObject, Signal, QTimer
from .base import Player, TrackRef


class PlaybackState:
    STOPPED = "stopped"
    PLAYING = "playing"
    PAUSED = "paused"
    BUFFERING = "buffering"

class PlaybackService(QObject):
    stateChanged = Signal(str)
    trackChanged = Signal(object)
    positionChanged = Signal(float)
    backendChanged = Signal(str)

    def __init__(self, parent=None):
        super().__init__(parent)
        self._player: Player | None = None
        self._queue: list[TrackRef] = []
        self._state = PlaybackState.STOPPED
        self._poll = QTimer(self)
        self._poll.setInterval(100)
        self._poll.timeout.connect(self._tick)

    def set_backend(self, player: Player):
        if self._player:
            self._player.stop()
        self._player = player
        self.backendChanged.emit(player.name())

    def load_queue(self, items: list[TrackRef], start_index: int = 0):
        assert self._player is not None, "Playback backend not set"
        self._queue = items
        self._player.set_queue(items, start_index)
        idx = self._player.current_index()
        if idx is not None and 0 <= idx < len(items):
            self.trackChanged.emit(items[idx])

    def play(self):
        assert self._player is not None
        self._player.play()
        self._state = PlaybackState.PLAYING
        self.stateChanged.emit(self._state)
        self._poll.start()

    def pause(self):
        if self._player and self._player.capabilities().can_pause:
            self._player.pause()
            self._state = PlaybackState.PAUSED
            self.stateChanged.emit(self._state)

    def stop(self):
        if self._player:
            self._player.stop()
        self._state = PlaybackState.STOPPED
        self.stateChanged.emit(self._state)
        self._poll.stop()

    def seek(self, position_s: float):
        if self._player and self._player.capabilities().can_seek:
            self._player.seek(position_s)

    def set_volume(self, v: float):
        if self._player:
            self._player.set_volume(v)

    def _tick(self):
        if not self._player:
            return
        pos = self._player.external_clock_position_s()
        if pos is not None:
            self.positionChanged.emit(pos)

    def play_tracks(self, items: list[TrackRef], start_index: int = 0):
        self.load_queue(items, start_index)
        self.play()
