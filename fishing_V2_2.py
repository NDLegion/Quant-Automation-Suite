import pyautogui
import time
import keyboard
import numpy as np
import cv2

# =========================
# CONFIG
# =========================

DEBUG = False

pyautogui.FAILSAFE = True

# Points to monitor
points = [
    (187, 1234),   # left click trigger
    (2273, 1244),  # right click trigger
    (1165, 511),   # popup detection
    (1092, 1318)   # red stop detection
]

# Target colors
target_colors = [
    (0, 0, 0),
    (0, 0, 0),
    (255, 255, 255),
    (255, 0, 0)
]

script_running = False

# =========================
# UTILITY FUNCTIONS
# =========================

def debug_log(message):
    if DEBUG:
        print(message)


def check_red_color(pixel):
    b, g, r = pixel
    return r > 150 and g < 100 and b < 100


# =========================
# CONTROL FUNCTIONS
# =========================

def start_script():
    global script_running
    script_running = True
    print("Automation started")


def stop_script():
    global script_running
    script_running = False
    print("Automation stopped")


keyboard.add_hotkey('9', start_script)
keyboard.add_hotkey('0', stop_script)


# =========================
# MAIN LOOP
# =========================

while True:

    while script_running:

        # Take ONE screenshot
        screenshot = pyautogui.screenshot()

        # Convert to OpenCV format
        frame = cv2.cvtColor(np.array(screenshot), cv2.COLOR_RGB2BGR)

        for i, (x, y) in enumerate(points):

            pixel = frame[y, x]

            # STOP CONDITION (RED)
            if i == 3:
                if check_red_color(pixel):
                    print("Red condition detected. Stopping script.")
                    script_running = False
                    break
                continue

            color = tuple(pixel)

            if color == target_colors[i]:

                # LEFT CLICK
                if i == 0:
                    pyautogui.click(x, y)
                    debug_log("Left click triggered")

                # RIGHT CLICK
                elif i == 1:
                    pyautogui.rightClick(x, y)
                    debug_log("Right click triggered")

                # POPUP DETECTION
                elif i == 2:

                    print("Popup detected → ESC pressed")
                    pyautogui.press('esc')

                    time.sleep(0.5)

                    red_pixel = frame[1318, 1092]

                    if check_red_color(red_pixel):
                        print("Red condition detected. Stopping script.")
                        script_running = False
                        break

                    else:
                        time.sleep(1)

                        keyboard.press('1')
                        time.sleep(1)
                        keyboard.release('1')

                        print("Key 1 pressed")

            else:
                debug_log(f"Waiting... pixel ({x},{y})")

        # loop delay (~50 checks/sec)
        time.sleep(0.02)

    time.sleep(0.5)
