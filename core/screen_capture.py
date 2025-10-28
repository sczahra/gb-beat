import mss
import numpy as np
import cv2
import random

class ScreenVisualizer:
    def __init__(self, left=100, top=100, width=480, height=432):
        self.sct = mss.mss()
        self.region = {"left": left, "top": top, "width": width, "height": height}
        self.shake_timer = 0.0
        self.flash_timer = 0.0

    def trigger_beat(self, strength):
        self.shake_timer = max(self.shake_timer, 0.15 * (0.5 + strength))
        self.flash_timer = max(self.flash_timer, 0.07 * (0.5 + strength))

    def _capture_frame(self):
        shot = self.sct.grab(self.region)
        return np.array(shot)[:, :, :3]

    def _apply_shake(self, frame_bgr):
        if self.shake_timer <= 0:
            return frame_bgr
        h, w, _ = frame_bgr.shape
        dx = random.randint(-4,4)
        dy = random.randint(-4,4)
        M = np.float32([[1,0,dx],[0,1,dy]])
        shaken = cv2.warpAffine(frame_bgr, M, (w,h))
        self.shake_timer -= 1/60.0
        return shaken

    def _apply_flash(self, frame_bgr):
        if self.flash_timer <= 0:
            return frame_bgr
        alpha = min(1.0, self.flash_timer * 8.0)
        flash_color = np.full_like(frame_bgr, (255,255,255))
        out = cv2.addWeighted(frame_bgr, 1-alpha, flash_color, alpha, 0)
        self.flash_timer -= 1/60.0
        return out

    def _overlay_text(self, frame_bgr):
        h, w, _ = frame_bgr.shape
        text = "SYNC MODE"
        cv2.putText(frame_bgr, text, (10, h-10),
                    cv2.FONT_HERSHEY_SIMPLEX,
                    0.5, (0,0,0), 3, cv2.LINE_AA)
        cv2.putText(frame_bgr, text, (10, h-10),
                    cv2.FONT_HERSHEY_SIMPLEX,
                    0.5, (255,255,255), 1, cv2.LINE_AA)
        return frame_bgr

    def render_once(self):
        frame = self._capture_frame()
        frame = self._apply_shake(frame)
        frame = self._apply_flash(frame)
        frame = self._overlay_text(frame)
        cv2.imshow("Visualizer Output", frame)
        cv2.waitKey(1)
