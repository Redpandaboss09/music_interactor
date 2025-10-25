from dataclasses import dataclass

@dataclass(frozen=True)
class LyricsLine:
    t_start: float
    t_end: float
    text: str
    words: list(tuple(float, float, str)) | None = None

@dataclass(frozen=True)
class LyricsTrack:
    lines: list[LyricsLine]
    duration: float
