from dataclasses import dataclass
from pathlib import Path
from bisect import bisect_right
import re

_timestamp = re.compile(r"\[(\d{1,2}):(\d{1,2})(?:\.(\d{1,3}))?\]")

@dataclass(frozen=True)
class LyricLine:
    ts: float
    text: str

class LRC:
    def __init__(self, lines: list[LyricLine]):
        self.lines = sorted(lines, key=lambda l: l.ts)
        self._times = [l.ts for l in self.lines]

    @staticmethod
    def load(path: Path | None) -> "LRC":
        if not path or not path.exists():
            return LRC([])

        out: list[LyricLine] = []
        for raw in path.read_text(encoding='utf-8', errors='ignore').splitlines():
            tags = list(_timestamp.finditer(raw))
            if not tags:
                continue

            text = _timestamp.sub("", raw).strip()

            for m in tags:
                mm, ss, ms = m.groups()
                t = int(mm) * 60 + int(ss) + (int(ms) / (1000 if ms else 1))
                out.append(LyricLine(t=t, text=text))

        return LRC(out)

    def current(self, t: float) -> tuple[int, str]:
        if not self.lines:
            return -1, ""

        i = bisect_right(self._times, t) - 1
        if i < 0:
            return -1, ""

        return i, self.lines[i].text

    def next(self, i: int) -> tuple[int, float, str]:
        j = i + 1
        if j >= len(self.lines):
            return -1, float("inf"), ""

        nxt = self.lines[j]
        return j, nxt.ts, nxt.text
