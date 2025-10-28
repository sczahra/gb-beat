import sounddevice as sd
import numpy as np
import threading
import queue
import time

class AudioTap:
    """
    Debug version:
    - WASAPI loopback capture of system playback audio.
    - Prints RMS levels so we can see if we're actually hearing Spotify.
    """

    def __init__(self, samplerate=48000, blocksize=1024):
        self.samplerate = samplerate
        self.blocksize = blocksize
        self.frames = queue.Queue()
        self._stop = False

    def start(self):
        def worker():
            try:
                default_output = sd.default.device[1]
            except Exception:
                default_output = None

            stream = sd.InputStream(
                samplerate=self.samplerate,
                blocksize=self.blocksize,
                dtype='float32',
                channels=2,
                device=default_output,
                latency='low',
                extra_settings=sd.WasapiSettings(loopback=True)
            )
            stream.start()

            last_print = 0.0
            while not self._stop:
                data, _ = stream.read(self.blocksize)
                mono = data.mean(axis=1).astype(np.float32)
                self.frames.put(mono)

                now = time.time()
                if now - last_print > 0.1:
                    rms = float(np.sqrt(np.mean(mono ** 2)))
                    print(f"[AudioTap] RMS={rms:.5f}")
                    last_print = now

            stream.stop()
            stream.close()

        t = threading.Thread(target=worker, daemon=True)
        t.start()

    def stop(self):
        self._stop = True
