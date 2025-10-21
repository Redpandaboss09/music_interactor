import threading, queue

import numpy as np
import sounddevice as sd

from ..core.config import Settings

class RealTimeAudioCapture:
    def __init__(self, config: Settings, max_record_seconds: float = 0.0):
        self.config = config
        self._sr = int(config.sample_rate)
        self.samples_captured = 0

        # Preallocate a NumPy circular buffer of samples
        cap_samples = (int(self._sr * max_record_seconds)
                       if max_record_seconds > 0 else config.buffer_size * 8)
        self._buf = np.zeros(cap_samples, dtype=np.float32)
        self._write = 0
        self._lock = threading.Lock()

        self._subs = []
        self._q = queue.Queue(maxsize=8)
        self._fanout_thread = None
        self._stop_evt = threading.Event()

        self.stream = None
        self.xruns = 0

    def subscribe_frames(self, cb):
        self._subs.append(cb)

    def start(self):
        self._stop_evt.clear()
        self._start_fanout()
        try:
            ch = 1
            self.stream = sd.InputStream(
                samplerate=self._sr,
                channels=ch,
                callback=self._callback,
                blocksize=self.config.blocksize,
                dtype=np.float32,
                device=self.config.audio_device_index,
                latency="low",
            )
            self.stream.start()
        except sd.PortAudioError:
            ch = 2
            self.stream = sd.InputStream(
                samplerate=self._sr,
                channels=ch,
                callback=self._callback,
                blocksize=self.config.blocksize,
                dtype=np.float32,
                device=self.config.audio_device_index,
                latency="low",
            )
            self.stream.start()
        return self

    def stop(self):
        self._stop_evt.set()
        if self.stream:
            self.stream.stop(); self.stream.close(); self.stream = None
        if self._fanout_thread:
            self._fanout_thread.join(timeout=1.0)
        with self._lock:
            self._write = 0
            self._buf[:] = 0

    def __enter__(self): return self.start()
    def __exit__(self, *exc): self.stop()

    def get_audio_data(self) -> np.ndarray:
        """Return the latest buffer_size samples (no allocation if contiguous)."""
        n = self.config.buffer_size
        with self._lock:
            w = self._write
            if n <= w:
                # contiguous slice
                return self._buf[w - n:w].copy()
            # wrap-around: stitch tail+head
            tail = self._buf[max(0, w - n):w]
            head = self._buf[:max(0, n - len(tail))]
            return np.concatenate((tail, head)) if head.size else tail.copy()

    @property
    def sample_rate(self) -> int:
        return self._sr

    def _callback(self, indata, frames, time_info, status):
        if status and status.input_overflow:
            self.xruns += 1

        if indata.shape[1] == 2:
            mono = indata.mean(axis=1, dtype=np.float32)
        else:
            mono = indata[:, 0].astype(np.float32, copy=False)

        # Write into ring buffer
        with self._lock:
            w = self._write
            N = mono.shape[0]
            buf = self._buf
            end = w + N
            if end <= buf.size:
                buf[w: end] = mono
            else:
                k = buf.size - w
                buf[w:] = mono[:k]
                buf[: N - k] = mono[k:]
            self._write = (w + N) % buf.size
            self.samples_captured += frames

        # Non-blocking handoff to fanout thread
        try:
            self._q.put_nowait(mono.copy()) # Copy as so we don't share PortAudio memory
        except queue.Full:
            pass # Skip for now

    def _start_fanout(self):
        def run():
            while not self._stop_evt.is_set():
                try:
                    block = self._q.get(timeout=0.1)
                except queue.Empty:
                    continue
                for cb in list(self._subs):
                    try:
                        cb(block)
                    except Exception:
                        # Ignore so we don't crash...
                        continue
        self._fanout_thread = threading.Thread(target=run, daemon=True)
        self._fanout_thread.start()
