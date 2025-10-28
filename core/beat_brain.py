import numpy as np
import threading
import queue
import time

class BeatBrain:
    """
    Debug version:
    - Lower beat threshold (more sensitive)
    - Prints detected beats
    """

    def __init__(self, audio_source, samplerate=48000):
        self.audio_source = audio_source
        self.samplerate = samplerate
        self.frame_size = 1024
        self.hop = 512
        self.events = queue.Queue()
        self._baseline_window = []
        self._ring = np.zeros(0, dtype=np.float32)
        self._stop = False

    def _bass_energy(self, chunk):
        w = np.hanning(len(chunk))
        spectrum = np.fft.rfft(chunk * w)
        mag = np.abs(spectrum)
        idx_limit = int(200.0 / (self.samplerate / 2.0) * len(mag))
        if idx_limit < 1:
            idx_limit = 1
        bass = float(np.mean(mag[:idx_limit]))
        return bass

    def _maybe_emit_beat(self, energy):
        self._baseline_window.append(energy)
        if len(self._baseline_window) > 50:
            self._baseline_window.pop(0)
        avg = np.mean(self._baseline_window) if self._baseline_window else 0.0
        if avg <= 0:
            return
        if energy > avg * 1.2:
            strength = min(2.0, (energy / avg) - 1.0)
            print(f"[BeatBrain] beat! energy={energy:.3f} avg={avg:.3f} strength={strength:.3f}")
            self.events.put(("beat", strength))

    def start(self):
        def worker():
            last_time = time.time()
            while not self._stop:
                try:
                    block = self.audio_source.frames.get(timeout=0.1)
                except queue.Empty:
                    continue
                self._ring = np.concatenate([self._ring, block])
                while len(self._ring) >= self.frame_size:
                    chunk = self._ring[:self.frame_size]
                    self._ring = self._ring[self.hop:]
                    energy = self._bass_energy(chunk)
                    self._maybe_emit_beat(energy)
                now = time.time()
                frame_time = self.hop / self.samplerate
                delay = frame_time - (now - last_time)
                if delay > 0:
                    time.sleep(delay)
                last_time = now
        t = threading.Thread(target=worker, daemon=True)
        t.start()

    def stop(self):
        self._stop = True
