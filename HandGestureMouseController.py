import cv2
import mediapipe as mp
import pyautogui
import time
import math

# ---------- Configuration ----------
SMOOTHING_FACTOR      = 0.8    # 0 = raw (jittery), 1 = fully smoothed (laggy)
CLICK_COOLDOWN        = 0.3    # seconds to ignore additional thumb‐clicks
RIGHTCLICK_COOLDOWN   = 0.3    # seconds to ignore additional ring‐clicks
SCROLL_CLICK_THRESHOLD = 20    # pixels of vertical movement in scroll mode for one discrete scroll
ZOOM_CLICK_THRESHOLD   = 20    # pixels of distance change for each “zoom‐notch”

FRAME_DELAY           = 0.01   # 0 = process every frame; bigger = lower CPU usage
# -----------------------------------

mp_hands   = mp.solutions.hands
mp_draw    = mp.solutions.drawing_utils

# Get screen size so we can map normalized coords → actual screen coords
screen_w, screen_h = pyautogui.size()

# Open default webcam
cap = cv2.VideoCapture(0)
if not cap.isOpened():
    raise IOError("Cannot open webcam")

# Read camera resolution (needed to convert normalized → pixel coords)
cam_w = cap.get(cv2.CAP_PROP_FRAME_WIDTH)
cam_h = cap.get(cv2.CAP_PROP_FRAME_HEIGHT)

# State variables
prev_x, prev_y          = 0.0, 0.0
last_click_time         = 0.0
last_rightclick_time    = 0.0
scroll_active           = False
prev_scroll_mid_y       = 0.0

zoom_active             = False
initial_zoom_dist       = 0.0
prev_zoom_dist          = 0.0

def fingers_up(landmarks):
    """
    Return a tuple of booleans: (thumb_up, index_up, middle_up, ring_up, pinky_up).
    - For index/middle/ring/pinky: fingertip.y < PIP.y → finger is extended.
      (Because normalized coords y=0 at top, y=1 at bottom.)
    - For thumb: in a mirrored frame, if TIP.x < IP.x → thumb is “popped out” (extended).
      You may need to invert this (< → >) depending on left vs. right hand or camera mirroring.
    """
    THUMB_TIP = mp_hands.HandLandmark.THUMB_TIP
    THUMB_IP  = mp_hands.HandLandmark.THUMB_IP
    INDEX_TIP = mp_hands.HandLandmark.INDEX_FINGER_TIP
    INDEX_PIP = mp_hands.HandLandmark.INDEX_FINGER_PIP
    MID_TIP   = mp_hands.HandLandmark.MIDDLE_FINGER_TIP
    MID_PIP   = mp_hands.HandLandmark.MIDDLE_FINGER_PIP
    RING_TIP  = mp_hands.HandLandmark.RING_FINGER_TIP
    RING_PIP  = mp_hands.HandLandmark.RING_FINGER_PIP
    PINKY_TIP = mp_hands.HandLandmark.PINKY_TIP
    PINKY_PIP = mp_hands.HandLandmark.PINKY_PIP

    thumb_tip = landmarks[THUMB_TIP]
    thumb_ip  = landmarks[THUMB_IP]
    index_tip = landmarks[INDEX_TIP]
    index_pip = landmarks[INDEX_PIP]
    mid_tip   = landmarks[MID_TIP]
    mid_pip   = landmarks[MID_PIP]
    ring_tip  = landmarks[RING_TIP]
    ring_pip  = landmarks[RING_PIP]
    pinky_tip = landmarks[PINKY_TIP]
    pinky_pip = landmarks[PINKY_PIP]

    # Thumb: in mirrored frame, TIP.x < IP.x means thumb is extended (pointing to the left).
    thumb_up  = thumb_tip.x < thumb_ip.x

    # Other four fingers: TIP.y < PIP.y → extended
    index_up  = index_tip.y < index_pip.y
    middle_up = mid_tip.y   < mid_pip.y
    ring_up   = ring_tip.y  < ring_pip.y
    pinky_up  = pinky_tip.y < pinky_pip.y

    return thumb_up, index_up, middle_up, ring_up, pinky_up

# Main loop
with mp_hands.Hands(
    static_image_mode=False,
    max_num_hands=1,
    min_detection_confidence=0.7,
    min_tracking_confidence=0.7
) as hands:
    prev_frame_time = 0.0

    while True:
        # --------- Frame‐Rate Limiter ---------
        now = time.time()
        if FRAME_DELAY > 0 and (now - prev_frame_time) < FRAME_DELAY:
            continue
        prev_frame_time = now

        ret, frame = cap.read()
        if not ret:
            print("Failed to grab frame.")
            break

        # Mirror the image so it behaves like a mirror
        frame = cv2.flip(frame, 1)

        # Convert BGR → RGB for MediaPipe processing
        rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        rgb.flags.writeable = False
        results = hands.process(rgb)
        rgb.flags.writeable = True

        if results.multi_hand_landmarks:
            handLms = results.multi_hand_landmarks[0]
            lm     = handLms.landmark  # list of 21 normalized Landmarks

            # Determine which fingers are up
            thumb_up, index_up, middle_up, ring_up, pinky_up = fingers_up(lm)

            # ---------- 1) PINCH‐ZOOM MODE ----------
            # Gesture: thumb_up AND index_up AND middle_down AND ring_down AND pinky_down
            if (thumb_up and index_up and not middle_up and not ring_up and not pinky_up):
                # Compute pixel coords for thumb tip & index tip
                thumb_px = (
                    int(lm[mp_hands.HandLandmark.THUMB_TIP].x * cam_w),
                    int(lm[mp_hands.HandLandmark.THUMB_TIP].y * cam_h)
                )
                index_px = (
                    int(lm[mp_hands.HandLandmark.INDEX_FINGER_TIP].x * cam_w),
                    int(lm[mp_hands.HandLandmark.INDEX_FINGER_TIP].y * cam_h)
                )
                # Euclidean distance between thumb & index (in camera pixels)
                curr_dist = math.hypot(thumb_px[0] - index_px[0], thumb_px[1] - index_px[1])

                if not zoom_active:
                    # Just entering zoom mode: initialize distances
                    zoom_active       = True
                    initial_zoom_dist = curr_dist
                    prev_zoom_dist    = curr_dist
                else:
                    # We are already in zoom mode; see how much distance changed
                    delta = curr_dist - prev_zoom_dist
                    if abs(delta) > ZOOM_CLICK_THRESHOLD:
                        # If thumb+index moved apart more than threshold → Zoom in
                        # If moved closer → Zoom out
                        # To zoom, hold CTRL while scrolling
                        if delta > 0:
                            # Zoom in: send Ctrl + scroll up (each scroll=+1 notch)
                            pyautogui.keyDown('ctrl')
                            pyautogui.scroll(1)
                            pyautogui.keyUp('ctrl')
                            cv2.putText(frame, "ZOOM IN", (20, 50),
                                        cv2.FONT_HERSHEY_SIMPLEX, 1.0, (0, 128, 0), 2)
                        else:
                            # Zoom out: send Ctrl + scroll down
                            pyautogui.keyDown('ctrl')
                            pyautogui.scroll(-1)
                            pyautogui.keyUp('ctrl')
                            cv2.putText(frame, "ZOOM OUT", (20, 50),
                                        cv2.FONT_HERSHEY_SIMPLEX, 1.0, (0, 0, 128), 2)
                        # Reset prev_zoom_dist for next discrete step
                        prev_zoom_dist = curr_dist
                    else:
                        # Minor changes → just stay in zoom mode overlay
                        cv2.putText(frame, "ZOOM MODE", (20, 50),
                                    cv2.FONT_HERSHEY_SIMPLEX, 1.0, (0, 255, 255), 2)

            else:
                # Exited zoom mode
                zoom_active = False

                # ---------- 2) CLICK (LEFT) MODE ----------
                # Gesture: thumb_up AND index_down AND middle_down AND ring_down AND pinky_down
                if (thumb_up and not index_up and not middle_up and not ring_up and not pinky_up):
                    if now - last_click_time > CLICK_COOLDOWN:
                        pyautogui.click()
                        last_click_time = now
                    cv2.putText(frame, "CLICK!", (20, 50),
                                cv2.FONT_HERSHEY_SIMPLEX, 1.0, (0, 0, 255), 2)

                # ---------- 3) RIGHT‐CLICK MODE ----------
                # Gesture: ring_up AND index_down AND middle_down AND thumb_down AND pinky_down
                elif (ring_up and not index_up and not middle_up and not thumb_up and not pinky_up):
                    if now - last_rightclick_time > RIGHTCLICK_COOLDOWN:
                        pyautogui.click(button='right')
                        last_rightclick_time = now
                    cv2.putText(frame, "RIGHT‐CLICK!", (20, 50),
                                cv2.FONT_HERSHEY_SIMPLEX, 1.0, (0, 0, 255), 2)

                # ---------- 4) SCROLL MODE (CLICK‐SCROLL) ----------
                # Gesture: index_up AND middle_up AND thumb_down AND ring_down AND pinky_down
                elif (index_up and middle_up and not thumb_up and not ring_up and not pinky_up):
                    # Compute camera‐pixel coords for index & middle tips
                    idx_x_px = int(lm[mp_hands.HandLandmark.INDEX_FINGER_TIP].x * cam_w)
                    idx_y_px = int(lm[mp_hands.HandLandmark.INDEX_FINGER_TIP].y * cam_h)
                    mid_x_px = int(lm[mp_hands.HandLandmark.MIDDLE_FINGER_TIP].x * cam_w)
                    mid_y_px = int(lm[mp_hands.HandLandmark.MIDDLE_FINGER_TIP].y * cam_h)
                    curr_mid_y = (idx_y_px + mid_y_px) / 2.0

                    if not scroll_active:
                        scroll_active    = True
                        prev_scroll_mid_y = curr_mid_y
                        cv2.putText(frame, "SCROLL MODE", (20, 50),
                                    cv2.FONT_HERSHEY_SIMPLEX, 1.0, (255, 255, 0), 2)
                    else:
                        # How far have we moved up/down since last “scroll notch”?
                        delta_y = prev_scroll_mid_y - curr_mid_y
                        if delta_y > SCROLL_CLICK_THRESHOLD:
                            # Finger‐pair moved upward by threshold → scroll up one notch
                            pyautogui.scroll(1)
                            prev_scroll_mid_y = curr_mid_y
                            cv2.putText(frame, "SCROLL UP", (20, 50),
                                        cv2.FONT_HERSHEY_SIMPLEX, 1.0, (0, 255, 0), 2)
                        elif delta_y < -SCROLL_CLICK_THRESHOLD:
                            # Moved downward by threshold → scroll down
                            pyautogui.scroll(-1)
                            prev_scroll_mid_y = curr_mid_y
                            cv2.putText(frame, "SCROLL DOWN", (20, 50),
                                        cv2.FONT_HERSHEY_SIMPLEX, 1.0, (0, 0, 255), 2)
                        else:
                            cv2.putText(frame, "SCROLL MODE", (20, 50),
                                        cv2.FONT_HERSHEY_SIMPLEX, 1.0, (255, 255, 0), 2)

                else:
                    # Exited scroll mode
                    scroll_active = False

                    # ---------- 5) MOVEMENT MODE ----------
                    # Gesture: index_up AND thumb_down AND middle_down AND ring_down AND pinky_down
                    if (index_up and not thumb_up and not middle_up and not ring_up and not pinky_up):
                        idx_norm = lm[mp_hands.HandLandmark.INDEX_FINGER_TIP]
                        screen_x = int(idx_norm.x * screen_w)
                        screen_y = int(idx_norm.y * screen_h)
                        curr_x = prev_x + (screen_x - prev_x) * (1 - SMOOTHING_FACTOR)
                        curr_y = prev_y + (screen_y - prev_y) * (1 - SMOOTHING_FACTOR)
                        pyautogui.moveTo(curr_x, curr_y, _pause=False)
                        prev_x, prev_y = curr_x, curr_y
                        cv2.putText(frame, "MOVE MODE", (20, 50),
                                    cv2.FONT_HERSHEY_SIMPLEX, 1.0, (0, 255, 255), 2)
                    else:
                        # No valid gesture → idle; no action
                        pass

            # Draw hand landmarks & fingertip circles for visual feedback
            mp_draw.draw_landmarks(
                frame,
                handLms,
                mp_hands.HAND_CONNECTIONS,
                mp_draw.DrawingSpec(color=(0, 255, 0), thickness=2, circle_radius=2),
                mp_draw.DrawingSpec(color=(255, 0, 0), thickness=2)
            )

            # Draw colored circles on each fingertip to show which are “up”
            def draw_tip(lm_index, is_up, color):
                x_px = int(lm[lm_index].x * cam_w)
                y_px = int(lm[lm_index].y * cam_h)
                if is_up:
                    cv2.circle(frame, (x_px, y_px), 10, color, cv2.FILLED)
                else:
                    cv2.circle(frame, (x_px, y_px), 5, (200, 200, 200), 2)

            # Thumb: blue if up
            draw_tip(mp_hands.HandLandmark.THUMB_TIP, thumb_up, (255, 0, 0))
            # Index: yellow if up
            draw_tip(mp_hands.HandLandmark.INDEX_FINGER_TIP, index_up, (0, 255, 255))
            # Middle: green if up
            draw_tip(mp_hands.HandLandmark.MIDDLE_FINGER_TIP, middle_up, (0, 255, 0))
            # Ring: teal if up
            draw_tip(mp_hands.HandLandmark.RING_FINGER_TIP, ring_up, (0, 128, 128))
            # Pinky: magenta if up
            draw_tip(mp_hands.HandLandmark.PINKY_TIP, pinky_up, (255, 0, 255))

        # Show the annotated frame
        cv2.imshow('Hand → Mouse [Move | Click | R-Click | Scroll | Zoom]', frame)

        # Exit when 'q' is pressed
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

# Cleanup
cap.release()
cv2.destroyAllWindows()
