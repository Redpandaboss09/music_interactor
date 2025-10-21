from __future__ import annotations
from typing import Tuple

import numpy as np
from numpy.fft import rfft, rfftfreq

from ..core.config import Settings

class AudioProcessor:
    """
    Prepares raw audio for visualization (RMS + FFT + banding)
    """
    def __init__(self, settings: Settings):
        self.s = settings
        self._win_cache: dict[int, np.ndarray] = {}
        self._win_cache[self.s.buffer_size] = np.hanning(self.s.buffer_size).astype(np.float32)

    def _hann(self, size: int) -> np.ndarray:
        win = self._win_cache.get(size)
        if win is None:
            win = np.hanning(size).astype(np.float32)
            self._win_cache[size] = win
        return win

    def calculate_rms(self, audio_data: np.ndarray) -> float:
        """
        RMS (Volume) in linear units of [0...1]
        """
        if audio_data.size == 0:
            return 0.0
        # Treat near-silence as zero to avoid weird noise flutter
        if float(np.max(np.abs(audio_data))) < self.s.silence_threshold:
            return 0.0
        return float(np.sqrt(np.mean(audio_data ** 2)))

    def calculate_fft_visualization(self, audio_data: np.ndarray) -> np.ndarray:
        """
        Real FFT magnitudes -> normalized 0...1 array (length N/2+1),
        using dB clamp [-80, 0] mapped to [0, 1]
        """
        n = audio_data.size
        if n == 0 or float(np.max(np.abs(audio_data))) < self.s.silence_threshold:
            return np.zeros(n // 2 + 1, dtype=np.float32)

        window = self._hann(n)
        X = rfft(window * audio_data)
        mag = np.abs(X).astype(np.float32)

        mag_db = 20.0 * np.log10(mag + 1e-10)
        mag_db = np.clip(mag_db, -80, 0.0)
        mag_norm = (mag_db + 80.0) / 80.0
        return mag_norm.astype(np.float32)

    def group_frequencies(self, fft_magnitudes: np.ndarray, num_bands: int = 32) -> np.ndarray:
        """
        Group FFT bins into log-spaced bands for visualization (returns 0..1).
        Applies a noise-floor gate in dB before returning.
        """
        if fft_magnitudes.size == 0:
            return np.zeros(num_bands, dtype=np.float32)

        num_bins = fft_magnitudes.size
        min_freq = 20.0
        max_freq = self.s.sample_rate / 2.0

        # Frequency vector for this FFT (infer N from rfft length)
        # rfftfreq expects the full N (where len(rfft) = N//2 + 1) -> N = (num_bins-1)*2
        full_n = (num_bins - 1) * 2
        freqs = rfftfreq(full_n, 1.0 / self.s.sample_rate)

        # Log-spaced edges in Hz
        edges_hz = np.logspace(np.log10(min_freq), np.log10(max_freq), num_bands + 1)

        # Convert edges to bin indices via searchsorted
        idx = np.searchsorted(freqs, edges_hz, side='left')
        idx = np.clip(idx, 0, num_bins - 1)

        bands = np.zeros(num_bands, dtype=np.float32)
        for i in range(num_bands):
            a, b = int(idx[i]), int(idx[i + 1])
            if b > a:
                bands[i] = float(fft_magnitudes[a:b].mean())
            else:
                bands[i] = float(fft_magnitudes[a])

        # Apply noise floor in dB space
        bands_db = bands * 80.0 - 80.0
        bands[bands_db < self.s.noise_floor_db] = 0.0
        return bands

class SpectrumWorker:
    """
    Subscribes to audio frames and keeps a ready-to-render band vector for the visualizer.
    Usage:
        worker = SpectrumWorker(audio, settings, n_fft=1024, n_bands=48)
        bins = worker.latest_bands()
    """
    def __init__(self, audio, settings: Settings, n_fft: int = 1024, n_bands: int = 48,
                 fmin_hz: float = 40.0, fmax_hz: float | None = None):
        self._audio = audio
        self._s = settings
        self._n_fft = int(n_fft)
        self._proc = AudioProcessor(settings)
        self._n_bands = int(n_bands)
        self._fmin = float(fmin_hz)
        self._fmax = float(fmax_hz or (settings.sample_rate / 2.0))

        # Reusable window for this FFT size
        self._win = self._proc._hann(self._n_fft)

        # Precompute edges for band grouping once for this FFT length
        # group_frequencies logic is reused but precomputed arrays are used for speed
        self._freqs = rfftfreq(self._n_fft, 1.0 / self._s.sample_rate)
        self._edges = np.logspace(np.log10(self._fmin), np.log10(self._fmax), self._n_bands + 1)
        self._latest = np.zeros(self._n_bands, dtype=np.float32)

        # Subscribe to audio frames
        audio.subscribe_frames(self._on_block)

    def _on_block(self, mono: np.ndarray) -> None:
        # Take last n_fft samples (padded with zeros if short)
        if mono.size < self._n_fft:
            buf = np.zeros(self._n_fft, dtype=np.float64)
            buf[-mono.size:] = mono
        else:
            buf = mono[-self._n_fft:]

        # FFT -> dB-normalization
        X = rfft(buf * self._win)
        mag = np.abs(X, dtype=np.float32)
        mag_db = 20.0 * np.log10(mag + 1e-10)
        mag_db = np.clip(mag_db, -80.0, 0.0)
        mag_norm = (mag_db + 80.0) / 80.0

        # Group bins into log bands using precomputed edges
        idx = np.searchsorted(self._freqs, self._edges, side='left')
        idx = np.clip(idx, 0, mag_norm.size - 1)
        bands = np.empty(self._n_bands, dtype=np.float32)
        for i in range(self._n_bands):
            a, b = int(idx[i]), int(idx[i + 1])
            if b > a:
                bands[i] = float(mag_norm[a:b].mean())
            else:
                bands[i] = float(mag_norm[a])

        # Noise floor gate
        bands_db = bands * 80.0 - 80.0
        bands[bands_db < self._s.noise_floor_db] = 0.0

        self._latest = bands

    def latest_bands(self) -> np.ndarray:
        return self._latest.copy()
