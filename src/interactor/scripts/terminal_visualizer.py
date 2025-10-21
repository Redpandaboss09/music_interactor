# src/interactor/scripts/terminal_visualizer_simple.py
import time, shutil
import numpy as np

from ..core.config import Settings
from ..audio.input import RealTimeAudioCapture
from ..audio.processing import AudioProcessor

def draw_line(bands: np.ndarray, rms: float) -> None:
    cols = shutil.get_terminal_size((100, 30)).columns
    # show first 8 bands, scale each to fit the terminal width a bit
    shown = bands[:8]
    # convert 0..1 to 0..(cols/12) blocks so it fits on one line
    max_blocks = max(1, (cols - 20) // (len(shown) + 1))
    bars = " ".join("█" * int(v * max_blocks) for v in shown)
    print(f"\rRMS:{rms:6.3f} | {bars:<{cols-14}}", end="", flush=True)

def main():
    s = Settings(audio_device_index=27)
    proc = AudioProcessor(s)

    print("Starting audio capture (Ctrl+C to stop)")
    cap = RealTimeAudioCapture(s).start()
    try:
        while True:
            # latest N samples (N = s.buffer_size)
            audio = cap.get_audio_data()

            # quick metrics
            rms = proc.calculate_rms(audio)
            mags = proc.calculate_fft_visualization(audio)   # 0..1 per rFFT bin
            bands = proc.group_frequencies(mags, num_bands=32)  # 0..1 per band

            draw_line(bands, rms)
            time.sleep(0.05)  # ~20 FPS
    except KeyboardInterrupt:
        print("\nStopping…")
    finally:
        cap.stop()

if __name__ == "__main__":
    main()
