from pathlib import Path
import json
from src.interactor.core.config import Settings
from .models import Album, Track

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

    def cover_path(self, album_dir: Path) -> Path | None:
        path = album_dir / 'cover.jpg'
        return path if path.exists() else None

    def first_track(self, album: Album) -> Track | None:
        st = album.sorted_tracks()
        return st[0] if st else None
