from bisect import bisect_right
from .models import LyricsTrack, LyricsLine

class LyricsEngine:
    def __init__(self):
        self._track: LyricsTrack | None = None
        self._starts: list[float] = []

    def set_track(self, track: LyricsTrack) -> None:
        self._track = track
        self._starts = [ln.t_start for ln in track.lines]

    def current_line(self, t: float) -> LyricsLine | None:
        if not self._track or not self._starts:
            return None

        i = bisect_right(self._starts, t) - 1
        if i < 0 or i >= len(self._track.lines):
            return None
        ln = self._track.lines[i]
        return ln if t < ln.t_end else None

    def progress_in_line(self, t: float) -> float:
        ln = self.current_line(t)
        if not ln:
            return 0.0

        dur = max(ln.t_end - ln.t_start, 1e-6)
        return max(0.0, min(1.0, (t - ln.t_start) / dur))
