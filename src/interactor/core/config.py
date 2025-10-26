from pathlib import Path

from pydantic import field_validator
from pydantic_settings import BaseSettings

def _repo_root():
    here = Path(__file__).resolve()
    return here.parents[3] if len(here.parents) >= 4 else here.parent

class Settings(BaseSettings):
    assets_dir: Path = Path('assets/library')
    sample_rate: int = 48000
    blocksize: int = 512
    buffer_size: int = 2048
    audio_device_index: int | None = None
    noise_floor_db: float = -60.0
    silence_threshold: float = 0.001

    @classmethod
    def from_file(cls,
                  primary: str | Path ="settings.toml",
                  override: str | Path = "settings.local.toml") -> "Settings":
        import tomllib
        repo = _repo_root()

        def load(path: Path) -> dict:
            return tomllib.loads(path.read_text(encoding="utf-8")) if path.exists() else {}

        base = load(repo / primary)
        overrider = load(repo / override)

        return cls(**{**base, **overrider})

    @field_validator("assets_dir", mode="before")
    @classmethod
    def _normalize_assets_dir(cls, v):
        path = Path(v).expanduser()
        if path.is_absolute():
            return path
        return (_repo_root() / path).resolve()

    @field_validator('sample_rate')
    @classmethod
    def _sr_ok(cls, v: int) -> int:
        if v not in (44100, 48000, 96000):
            raise ValueError('sample_rate must be one of 44100, 48000, 96000')
        return v

    @field_validator('blocksize')
    @classmethod
    def _blk_ok(cls, v: int) -> int:
        if v < 128 or v > 4096 or (v & (v - 1)) != 0:
            raise ValueError('blocksize must be power of two between 128 and 4096')
        return v