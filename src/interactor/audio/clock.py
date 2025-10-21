from __future__ import annotations

class AudioClock:
    """
    Master clock derived from audio samples.
    t_song = samples_captured / (sample_rate * (1 + rate_ppm/1e6)) + start_offset
    """
    def __init__(self, audio_input, max_nudge_ms: float = 10.0):
        self.audio = audio_input
        self._start_offset = 0.0 # In seconds
        self._max_nudge = float(max_nudge_ms) / 1000.0
        self._rate_ppm = 0.0  # rate tweak in parts per million

    def time(self) -> float:
        effective_sr = self.audio.sample_rate * (1.0 + self._rate_ppm / 1000000.0)
        return (self.audio.samples_captured / effective_sr) + self._start_offset

    def lock_to(self, offset_seconds: float) -> None:
        """
        Call when user stream is started and sets the start offset so current song matches offset_seconds
        """
        effective_sr = self.audio.sample_rate * (1.0 + self._rate_ppm / 1000000.0)
        now = self.audio.samples_captured / effective_sr
        self._start_offset = float(offset_seconds) - now

    def nudge(self, milliseconds: float) -> None:
        """
        Apply a small correction / nudge to the audio clock (to be attached to either keys or GPIO buttons)
        Changes are done in 10ms increments / decrements.
        """
        step = float(milliseconds) / 1000.0
        if step > 0:
            step = min(step, self._max_nudge)
        else:
            step = max(step, -self._max_nudge)
        self._start_offset += step

    def set_rate_ppm(self, ppm: float) -> None:
        """
        Used for small manual rate adjustments.
        """
        self._rate_ppm = float(ppm)

    def progress(self, duration_s: float) -> float:
        """
        0..1 progress for a given track duration.
        """
        if duration_s <= 0:
            return 0.0
        t = self.time()
        if t <= 0: return 0.0
        if t >= duration_s: return 1.0
        return t / duration_s