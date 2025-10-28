import pyautogui
import time

BUTTONS = ["right", "x", "z", "up"]

def burst(duration=0.1, strength=1.0):
    total = duration * (0.5 + strength)
    end_t = time.time() + total
    while time.time() < end_t:
        for key in BUTTONS:
            pyautogui.keyDown(key)
        for key in reversed(BUTTONS):
            pyautogui.keyUp(key)
