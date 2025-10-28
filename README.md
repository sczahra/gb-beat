# gb-beat

Reactive Game Boy / Game Boy Color visualizer driven by live system audio.

- We capture system audio output (Spotify, YouTube, etc.) using WASAPI loopback.
- We detect bass hits.
- On each beat:
  - We spam inputs into mGBA so Pokémon Crystal freaks out in rhythm.
  - We capture mGBA's screen region and apply shake / flash / "SYNC MODE".
  - We show that composited output in a window called "Visualizer Output".

## Prereqs (do once)

1. Python 3.11+ installed and works in terminal:
   `python --version`

2. Install requirements:
   ```bat
   pip install -r requirements.txt
   ```

3. Open mGBA:
   - Load Pokémon Crystal (US).
   - In mGBA controls:
     - Up/Down/Left/Right = Arrow keys
     - A = X
     - B = Z
   - Put the mGBA window near the top-left of your main monitor (roughly x=100,y=100).
   - Click mGBA so it is focused and leave it focused.

4. Make sure audio is playing in Spotify on the same output device (speakers / headphones).
   Stereo Mix / loopback is enabled (you did this already).

## Run it

From the repo root folder:
```bat
python core\run.py
```

(or `python -m core.run` if you prefer that style)

You should see:
- Console prints like `[AudioTap] RMS=0.03` and `[BeatBrain] beat! ...` (with debug overrides)
- A window called "Visualizer Output"
- Pokémon shaking/flashing to the beat
- The game in mGBA jerking/twitching because we're injecting inputs

If "Visualizer Output" is mostly black or offset, edit the `left/top/width/height` numbers in `core/run.py` (ScreenVisualizer call).
