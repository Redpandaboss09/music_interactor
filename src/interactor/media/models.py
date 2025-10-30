from pydantic import BaseModel, Field, field_validator

class Track(BaseModel):
    track_title: str
    track_artist: list[str] = Field(default_factory=list)
    composer: list[str] = Field(default_factory=list)
    lyricist: list[str] = Field(default_factory=list)

    disc: int
    track: int
    duration: float
    release_date: str

    isrc: str | None = None
    copyright: str | None = None
    explicit: int = 0
    lyrics: str | None = None
    alt_art: list[str] = Field(default_factory=list)

    @field_validator('explicit', mode='before')
    @classmethod
    def _exp_to_int(cls, v):
        if isinstance(v, bool):
            return 1 if v else 0
        try:
            return 1 if int(v) != 0 else 0
        except Exception:
            return 0

class Album(BaseModel):
    album_id: str
    album_title: str
    album_artist: str
    release_year: str
    disc_total: int
    track_total: int
    tracks: list[Track]

    def sorted_tracks(self) -> list[Track]:
        return sorted(self.tracks, key=lambda t: (t.disc, t.track))

    def find(self, disc: int, number: int) -> Track | None:
        for t in self.tracks:
            if t.disc == disc and t.track == number:
                return t
        return None
