from mutagen.flac import FLAC
from pathlib import Path
from ulid import ULID

# TODO SWITCH CONFIG STYLE TO ALLOW BETTER CHANGE
rootdir = Path('../library/')

for subfolder in rootdir.iterdir():
    if subfolder.is_dir():
        # Ignore the example folder
        if subfolder.name == 'ARTIST - ALBUM (YEAR)':
            continue

        # TODO COME UP FOR RULES TO ESCAPE ISSUES WITH () or - IN NAME (delimiters?)

        # Generate album data
        album = {
            "album_id": str(ULID()),
            "album_title": "title",
            "album_artist": "ARTIST",
            "copyright": "Music Group YEAR",
            "release_date": "xxxx-xx-xx",
            "album_cover": "cover.jpg",
            "disc_total": 1,
            "track_total": 1,
            "tracks": [
                {
                    "track_title": "A",
                    "track_artist": "ARTIST",
                    "featuring": [],
                    "composer": [],
                    "lyricist": [],
                    "disc": 1,
                    "track": 1,
                    "isrc": "x",
                    "explicit": 0,
                    "lyrics": "01. ARTIST - A.lrc",
                    "alt_art": []
                }
            ]
        }

        for file in subfolder.iterdir():
            if file.is_file():
                print(file.name)