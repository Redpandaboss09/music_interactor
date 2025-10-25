import re
from pathlib import Path
from .models import LyricsLine, LyricsTrack

_timestamp = re.compile(r"\[(\d+):(\d+)(?:\.(\d{1,3}))?\]")  # [mm:ss(.ms)]

def _stamp_to_s(m: str, s: str, ms: str | None) -> float:
    v = int(m)*60 + int(s)
    if ms:
        # Normalize to ms
        v += int(ms.ljust(3, "0")) / 1000.0
    return float(v)

def load_lrc(path: str | Path) -> LyricsTrack:
    path = Path(path)
    if not path.exists():
        return LyricsTrack(lines=[], duration=0.0)

    lines: list[LyricsLine] = []
    for raw in path.read_text(encoding="utf-8", errors="ignore").splitlines():
        tags = list(_timestamp.findall(raw))
        if not tags:
            continue
        text = _timestamp.sub("", raw).strip()
        for i, tag in enumerate(tags):
            t = _stamp_to_s(tag.group(1), tag.group(2), tag.group(3))
            lines.append(LyricsLine(t_start=t, t_end=t, text=text))

    # Sort and fill t_end from next line's start, last line open-ended
    lines.sort(key=lambda x: x.t_start)
    for i in range(len(lines)-1):
        lines[i] = LyricsLine(
            t_start=lines[i].t_start,
            t_end=lines[i+1].t_start,
            text=lines[i].text,
            words=lines[i].words
        )

    duration = lines[-1].t_end if lines else 0.0
    return LyricsTrack(lines=lines, duration=duration)