import sys
import os

ROOT_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if ROOT_DIR not in sys.path:
    sys.path.insert(0, ROOT_DIR)

try:
    from updates.audio_tap import AudioTap
except ImportError:
    from core.audio_tap import AudioTap

try:
    from updates.beat_brain import BeatBrain
except ImportError:
    from core.beat_brain import BeatBrain

try:
    from updates.screen_capture import ScreenVisualizer
except ImportError:
    from core.screen_capture import ScreenVisualizer

try:
    from updates.visual_driver import VisualDriver
except ImportError:
    from core.visual_driver import VisualDriver


def main():
    tap = AudioTap()
    tap.start()

    brain = BeatBrain(audio_source=tap)
    brain.start()

    vis = ScreenVisualizer(left=100, top=100, width=480, height=432)

    driver = VisualDriver(beat_brain=brain, screen_visualizer=vis)
    driver.run()

if __name__ == '__main__':
    main()
