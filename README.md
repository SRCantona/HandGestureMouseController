# 🚀 HandGestureMouseController


> **Wave** goodbye to your mouse and **👋** say hello to controlling your computer with **natural hand gestures**!



## 🔥 Features

- 🎯 **Intuitive Mouse Movement**  
  Point with your **index finger** to move the cursor across the screen — smooth as silk!

- 🖱️ **Left Click**  
  Pop up your **thumb** to perform a quick left-click. No more fiddling with your trackpad!

- 🖲️ **Right Click**  
  Raise your **ring finger** to trigger a right-click context menu.

- 📜 **Click-Scroll (Page-by-Page)**  
  Extend your **index + middle fingers** to scroll step-by-step, perfect for reading articles.

- 🔍 **Pinch-Zoom**  
  Pinch your **index + thumb** to zoom in/out in any app (sends Ctrl + scroll events).

- 🛑 **Idle Mode**  
  Any non-matching hand pose → No action. Prevents accidental gestures.

---





## 🎮 Use the gestures below to control your mouse:
   - 🖐️ **Move**: Only index finger extended → Move cursor.
   - 👍 **Left Click**: Only thumb extended → Left-click.
   - 🤙 **Right Click**: Only ring finger extended → Right-click.
   - 🖖 **Scroll**: Index + middle extended → Scroll one notch per vertical move.
   - 🤏 **Zoom**: Pinch index + thumb → Zoom in/out (Ctrl + scroll).


---

## 📋 Gesture Reference

| Mode              | Fingertips Extended                                                                           | Action                             |
|-------------------|-----------------------------------------------------------------------------------------------|------------------------------------|
| **Move**          | ✨ **Index** only (thumb, middle, ring, pinky folded)                                         | Move cursor (smooth tracking)      |
| **Left Click**    | 👍 **Thumb** only (index, middle, ring, pinky folded)                                         | Left-click                         |
| **Right Click**   | 🔘 **Ring Finger** only (index, middle, thumb, pinky folded)                                  | Right-click                        |
| **Scroll**        | ✌️ **Index + Middle** (thumb, ring, pinky folded)                                             | Click-scroll up/down one notch     |
| **Zoom**          | 🤏 **Index + Thumb** (middle, ring, pinky folded)                                             | Ctrl + scroll (pinch to zoom)      |
| **Idle**          | Any other combination                                                                        | No action                          |

---

## 🔧 Troubleshooting &amp; Tips

- **Lighting Matters**  
  Ensure your environment is well-lit for accurate hand detection. Avoid strong backlight.

- **Adjust Thresholds**  
  - In `HandGestureMouseController.py`, tweak `SCROLL_CLICK_THRESHOLD` and `ZOOM_CLICK_THRESHOLD` for sensitivity.
  - Lower thresholds for more responsiveness, higher for stability.

- **Smoothing Factor**  
  - `SMOOTHING_FACTOR = 0.0` → Direct, no smoothing (may jitter).  
  - `SMOOTHING_FACTOR = 0.9` → Very smooth, but slightly laggy.  
  - Find the sweet spot for your setup!

- **Camera Angle**  
  Hold your hand **parallel** to the camera plane. Keep fingers clearly visible.

- **Debounce Cooldowns**  
  If clicks/scrolls fire too often, increase `CLICK_COOLDOWN` and `RIGHTCLICK_COOLDOWN`.


---

## ❤️ Acknowledgements

- **[MediaPipe](https://github.com/google/mediapipe)**: Real-time hand tracking.  
- **[PyAutoGUI](https://github.com/asweigart/pyautogui)**: Cross-platform GUI automation.  
- **[OpenCV](https://opencv.org/)**: Video capture & processing.

