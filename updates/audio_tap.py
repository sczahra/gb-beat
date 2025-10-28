import sounddevice as sd
import numpy as np
import threading
import queue
import time

class AudioTap:
    """
    Stereo Mix / loopback grabber without WasapiSettings.

    Strategy:
    - Scan input devices for names like 'Stereo Mix', 'What U Hear', 'Wave Out', 'Loopback'.
    - If found, open as a normal input stream (no special flags).
    - Else, fall back to default input; if none, feed silence (no crash).
    - Print chosen device and periodic RMS so we can verify audio flow.
    """

    def __init__(self, samplerate=48000, blocksize=1024):
        self.samplerate = samplerate
        self.blocksize = blocksize
        self.frames = queue.Queue()
        self._stop = False

    def _find_loopback_device_index(self):
        devices = sd.query_devices()
        target_keywords = ["stereo mix", "what u hear", "wave out", "loopback"]
        for idx, dev in enumerate(devices):
            name = (dev.get("name") or "").lower()
            max_in = dev.get("max_input_channels", 0)
            if max_in >= 2:
                for kw in target_keywords:
                    if kw in name:
                        print(f"[AudioTap] using '{dev['name']}' (index {idx})")
                        return idx
        # fallback to default input if available
        try:
            default_input = sd.default.device[0]
            print(f"[AudioTap] fallback to default input index {default_input}")
            return default_input
        except Exception:
            print("[AudioTap] no usable input device found, feeding silence")
            return None

    def start(self):
        def worker():
            dev_index = self._find_loopback_device_index()
            stream = None
            if dev_index is not None:
                try:
                    stream = sd.InputStream(
                        samplerate=self.samplerate,
                        channels=2,
                        blocksize=self.blocksize,
                        dtype='float32',
                        device=dev_index,
                        latency='low'
                    )
                    stream.start()
                except Exception as e:
                    print(f"[AudioTap] failed to open stream on index {dev_index}: {e}")
                    stream = None

            last_print = 0.0
            while not self._stop:
                if stream is not None:
                    data, _ = stream.read(self.blocksize)  # (block, 2)
                    mono = data.mean(axis=1).astype(np.float32)
                else:
                    mono = np.zeros(self.blocksize, dtype=np.float32)

                self.frames.put(mono)

                now = time.time()
                if now - last_print > 0.25:
                    rms = float(np.sqrt(np.mean(mono ** 2)))
                    print(f"[AudioTap] RMS={rms:.5f}")
                    last_print = now

            if stream is not None:
                stream.stop()
                stream.close()

        t = threading.Thread(target=worker, daemon=True)
        t.start()

    def stop(self):
        self._stop = True
