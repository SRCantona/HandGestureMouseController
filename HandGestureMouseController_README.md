# HandGestureMouseController

**HandGestureMouseController** is a Python-based project that allows you to control your computer’s mouse and basic actions (click, right-click, scroll, and zoom) using hand gestures detected through a webcam. It leverages MediaPipe for real-time hand landmark detection and PyAutoGUI to move and simulate mouse events.

---

## Features

- **Move Cursor**: Point with your index finger to move the mouse cursor.
- **Left Click**: Raise your thumb to perform a left click.
- **Right Click**: Raise your ring finger to perform a right click.
- **Scroll Click**: Extend index + middle fingers to scroll page-by-page.
- **Pinch-Zoom**: Pinch index + thumb to zoom in/out (Ctrl + scroll).
- **Idle Mode**: No action when hand gestures do not match any defined pattern.

---

## Prerequisites

- Python 3.7 or higher
- Webcam compatible with OpenCV
- The following Python packages:
  - `opencv-python`
  - `mediapipe`
  - `pyautogui`

---

## Installation

1. Clone this repository:
   ```bash
   git clone https://github.com/yourusername/HandGestureMouseController.git
   cd HandGestureMouseController
   ```

2. (Optional) Create a virtual environment:
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. Install required dependencies:
   ```bash
   pip install -r requirements.txt
   ```

---

## Usage

1. Run the main Python script:
   ```bash
   python hand_gesture_mouse.py
   ```

2. Allow the script to access your webcam. A window will appear showing the camera feed with visual overlays.

3. Use the following gestures:
   - **Move**: Only index finger extended (others folded) to move the cursor.
   - **Left Click**: Only thumb extended to click.
   - **Right Click**: Only ring finger extended to right-click.
   - **Scroll**: Index + middle fingers extended to scroll up/down one notch.
   - **Zoom**: Pinch (index + thumb extended) and move apart or together to zoom in/out.

4. Press **q** in the window to exit the application.

---

## Gesture Reference

| Mode              | Fingertips Extended                                                                                               | Action                             |
|-------------------|-------------------------------------------------------------------------------------------------------------------|------------------------------------|
| **Move**          | Only **index** ↑ (thumb ↓, middle ↓, ring ↓, pinky ↓)                                                              | Move cursor to index position      |
| **Left Click**    | Only **thumb** ↑ (index ↓, middle ↓, ring ↓, pinky ↓)                                                              | Left-click                         |
| **Right Click**   | Only **ring** ↑ (index ↓, middle ↓, thumb ↓, pinky ↓)                                                              | Right-click                        |
| **Scroll**        | **Index + middle** ↑ (thumb ↓, ring ↓, pinky ↓)                                                                    | Scroll page-by-page (click-scroll) |
| **Zoom**          | **Index + thumb** ↑ (middle ↓, ring ↓, pinky ↓)                                                                    | Ctrl + scroll (pinch to zoom)      |
| **Idle**          | Any other combination                                                                                             | No action                          |

---

## Troubleshooting & Tips

- Ensure your environment is well-lit to improve hand detection accuracy.
- Adjust thresholds and smoothing parameters in `hand_gesture_mouse.py` if you experience jitter or unintended gestures.
- On Linux, you may need to install `python3-xlib` for `pyautogui` to function correctly.

---

## License

This project is licensed under the MIT License. See the [LICENSE](LICENSE) file for details.

---

## Acknowledgements

- [MediaPipe](https://github.com/google/mediapipe) for real-time hand tracking.
- [PyAutoGUI](https://github.com/asweigart/pyautogui) for cross-platform GUI automation.
- [OpenCV](https://opencv.org/) for video capture and processing.

