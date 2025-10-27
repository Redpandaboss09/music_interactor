from pathlib import Path
import json
from src.interactor.core.config import Settings
from .models import Album, Track
from .lyrics import LRC

class MediaService:
    def __init__(self, settings: Settings):
        self.assets_root = Path(settings.assets_dir)

    def list_albums(self) -> list[Path]:
        """ Loads all albums """
        root = self.assets_root
        if not root.exists():
            return []

        return sorted(p for p in root.iterdir() if (p / 'album.json').exists())

    def load_album(self, album_dir: Path) -> Album:
        data = json.loads((album_dir / 'album.json').read_text(encoding='utf-8'))
        return Album.model_validate(data)

    def cover_path(self, album_dir: Path) -> Path | None:
        path = album_dir / 'cover.jpg'
        return path if path.exists() else None

    def first_track(self, album: Album) -> Track | None:
        st = album.sorted_tracks()
        return st[0] if st else None

    def track_lyrics(self, album_dir: Path, track: Track) -> LRC:
        if not track.lyrics:
            return LRC([])

        path = album_dir / track.lyrics
        return LRC.load(path if path.exists() else None)
