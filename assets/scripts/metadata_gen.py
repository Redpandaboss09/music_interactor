from mutagen.flac import FLAC
from pathlib import Path
from ulid import ULID
import re
import warnings
import json

from src.interactor.core.config import Settings

rootdir = Path(Settings.from_file('settings.local.toml').assets_dir)

def run_gen():
    for subfolder in rootdir.iterdir():
        if subfolder.is_dir():
            # Ignore the example folder
            if subfolder.name == 'ARTIST - ALBUM (YEAR)':
                continue

            folder_name = str(subfolder.name)
            try:
                folder_name = _split_name(folder_name)
            except ValueError:
                continue

            # Generate album data
            album = {
                "album_id": str(ULID()),
                "album_title": folder_name[1],
                "album_artist": folder_name[0],
                "release_year": folder_name[2],
                "disc_total": 1,
                "track_total": 1,
                "tracks": [],
                "alt_art": _find_alt_artwork(subfolder)
            }

            for file in subfolder.iterdir():
                if file.is_file() and file.suffix == '.flac':
                    audio = FLAC(file)

                    track = {
                        "track_title": audio["TITLE"][0],
                        "track_artist": _convert_delimited_to_array(audio["ARTIST"][0]),
                        "composer": _convert_delimited_to_array(audio["COMPOSER"][0]),
                        "lyricist": _convert_delimited_to_array(audio["LYRICIST"][0]),
                        "disc": int(audio["DISCNUMBER"][0].split("/")[0]),
                        "track": int(audio["TRACKNUMBER"][0].split("/")[0]),
                        "isrc": audio["ISRC"][0],
                        "copyright": audio["COPYRIGHT"][0],
                        "release_date": audio["DATE"][0],
                        "duration": audio.info.length,
                        "explicit": _explicit_flag(audio),
                        "lyrics": file.with_suffix('.lrc').name.replace('\\', '/'),
                        "alt_art_track": [] # TODO FIGURE OUT LATER (HOLDS PATH STRS?)
                    }

                    album["tracks"].append(track)

            # Final additions are based off last song (for simplicity)
            last_track = album["tracks"][-1]
            album["disc_total"] = last_track["disc"]
            album["track_total"] = last_track["track"]

            full_path = subfolder / 'album.json'
            full_path.write_text(json.dumps(album, indent=4, ensure_ascii=False), encoding="utf-8")

def _split_name(subfolder: str) -> tuple[str, str, str]:
    """
    Returns the folder name as a split up tuple, where either of two regex instructions are used:
        regex_year: Split first by finding (YEAR) so we can safely look through rest without worrying about the end
        regex_no_year: Split best way possible without a year

    Folders should be:
        ARTIST - ALBUM (YEAR)
    where the album can have "-" or "()"

    :param subfolder:
    :return: tuple of [artist, album, year] OR [artist, album, "NONE"]
    """

    regex_year = re.compile(r"^\s*(?P<artist>.+?)\s*-\s*(?P<album>.+)\s*\((?P<year>\d{4})\)\s*$")
    regex_no_year = re.compile(r"^\s*(?P<artist>.+?)\s*-\s*(?P<album>.+?)\s*$")

    match = regex_year.match(subfolder)
    if match:
        return match.group('artist').strip(), match.group('album').strip(), match.group('year').strip()

    match = regex_no_year.match(subfolder)
    if match:
        warnings.warn(f'No year found for {subfolder}, default value is \"NONE\"')
        return match.group('artist').strip(), match.group('album').strip(), "NONE"

    raise ValueError(f'Cannot parse {subfolder!r}')

def _convert_delimited_to_array(names: str) -> list[str]:
    """ Convert the semicolon-delimited names into an array """
    try:
        return [name.strip() for name in names.split(';')]
    except KeyError:
        warnings.warn(f'No semicolon-delimited names found in {names!r}')
        return []

def _explicit_flag(track: FLAC) -> int:
    """ Set the flag as 1 if Explicit tag is there """
    try:
        if track["RATING"][0] == "Explicit":
            return 1
    except KeyError:
        return 0

def _find_alt_artwork(folder: Path) -> list[str] | None:
    """ Grabs all alternate artwork files for an album (like animated covers). """
    alt_artwork = folder / 'alt_art'
    all_art = []
    if alt_artwork.exists():
        for file in alt_artwork.iterdir():
            all_art.append(file.name)
        return all_art
    else:
        return None

if __name__ == '__main__':
    run_gen()