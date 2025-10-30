import warnings
from pathlib import Path
import json
from src.interactor.core.config import Settings
from .models import Album, Track

class MediaService:
    def __init__(self, settings: Settings):
        self.assets_root = Path(settings.assets_dir)
        self._id_to_dir: dict[str, Path] = {}
        self._cache: dict[str, Album] = {}

        self.refresh_index()

    def refresh_index(self) -> None:
        self._id_to_dir.clear()
        self._cache.clear()
        root = self.assets_root
        if not root.exists():
            return

        for album_dir in root.iterdir():
            if album_dir.name == "ARTIST - ALBUM (YEAR)":
                continue

            j = album_dir / "album.json"
            if not j.exists():
                continue

            try:
                data = json.loads(j.read_text(encoding="utf-8"))
                album_id = data.get("album_id")
                if album_id:
                    self._id_to_dir[album_id] = album_dir
                else:
                    warnings.warn(f"No album id found in {j}")
            except Exception as e:
                warnings.warn(f"Had to skip {j}: {e!r}")
                continue

    def list_albums(self) -> list[Path]:
        """ Loads all albums """
        return [self._id_to_dir[k] for k in sorted(self._id_to_dir.keys())]

    def load_album(self, album_dir: Path) -> Album:
        album_dir = Path(album_dir)
        data = json.loads((album_dir / 'album.json').read_text(encoding='utf-8'))

        cover = album_dir / 'cover.jpg'
        if cover.exists():
            data.setdefault('album_cover', str(cover))

        alt_art = data.get('alt_art')
        if isinstance(alt_art, dict):
            if 'animated_cover' in alt_art:
                ac = alt_art['animated_cover']
                alt_art['animated_cover'] = str((album_dir / ac).resolve())

        for track in data.get('tracks', []):
            if track.get('lyrics'):
                track['lyrics'] = str((album_dir / track['lyrics']).resolve())
            if 'alt_art_track' in track and isinstance(track['alt_art_track'], list):
                track['alt_art_track'] = [str((album_dir / f).resolve()) for f in track['alt_art_track']]

        return Album.model_validate(data)

    def get_album(self, album_id: str) -> Album | None:
        if album_id in self._cache:
            return self._cache[album_id]

        album_dir = self._id_to_dir.get(album_id)
        if not album_dir:
            return None

        album = self.load_album(album_dir)
        self._cache[album_id] = album
        return album

    def get_album_tracks(self, album_id: str) -> list[Track]:
        album = self.get_album(album_id)
        return album.sorted_tracks() if album else []

    def cover_path(self, album: str | Path) -> Path | None:
        album_dir = self._id_to_dir.get(album) if isinstance(album, str) else album
        if not album_dir:
            return None
        album_dir = Path(album_dir)
        path = album_dir / 'cover.jpg'
        return path if path.exists() else None

    def get_id_to_dir_keys(self):
        return self._id_to_dir.keys()