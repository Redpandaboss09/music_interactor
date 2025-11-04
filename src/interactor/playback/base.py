from dataclasses import dataclass
from abc import ABC, abstractmethod

@dataclass(frozen=True)
class TrackRef:
    track_id: str
    album_id: str
    uri: str
    title: str
    artists: list[str]
    duration_s: float | None = None

class PlayerCapabilities:
    def __init__(self, *, can_seek: bool, can_pause: bool, has_audio_output: bool):
        self.can_seek = can_seek
        self.can_pause = can_pause
        self.has_audio_output = has_audio_output

class Player(ABC):
    @abstractmethod
    def name(self) -> str: ...

    @abstractmethod
    def capabilities(self) -> PlayerCapabilities: ...

    @abstractmethod
    def set_queue(self, items: list[TrackRef], start_index: int = 0) -> None: ...

    @abstractmethod
    def play(self) -> None: ...

    @abstractmethod
    def pause(self) -> None: ...

    @abstractmethod
    def stop(self) -> None: ...

    @abstractmethod
    def seek(self, position_s: float) -> None: ...

    @abstractmethod
    def current_position_s(self) -> float | None: ...

    @abstractmethod
    def current_index(self) -> int | None: ...

    @abstractmethod
    def set_volume(self, volume: float) -> None: ...

    def external_clock_position_s(self) -> float | None:
        return self.current_position_s()
