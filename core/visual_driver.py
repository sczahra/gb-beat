import time
import queue
from core.input_injector import burst

class VisualDriver:
    def __init__(self, beat_brain, screen_visualizer):
        self.beat_brain = beat_brain
        self.screen_visualizer = screen_visualizer

    def run(self):
        last = time.time()
        while True:
            try:
                while True:
                    kind, strength = self.beat_brain.events.get_nowait()
                    if kind == 'beat':
                        burst(duration=0.1, strength=strength)
                        self.screen_visualizer.trigger_beat(strength)
            except queue.Empty:
                pass

            self.screen_visualizer.render_once()

            now = time.time()
            delta = now - last
            sleep_for = max(0, (1/60.0) - delta)
            time.sleep(sleep_for)
            last = now
