from pydantic import field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    sample_rate: int = 48000
    blocksize: int = 512
    buffer_size: int = 2048
    audio_device_index: int | None = None
    noise_floor_db: float = -60.0
    silence_threshold: float = 0.001

    model_config = SettingsConfigDict(env_file='.env', env_prefix='INTERACTOR_')

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