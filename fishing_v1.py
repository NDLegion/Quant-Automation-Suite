import pyautogui
import time
import keyboard
import numpy as np
import cv2

# -----------------------------
# CONFIGURATOR
# -----------------------------

points = [
    (187, 1234),   # left click trigger
    (2273, 1244),  # right click trigger
    (1165, 511),   # popup detection
    (1092, 1318)   # red zone detection
]

target_colors = [
    (0, 0, 0),
    (0, 0, 0),
    (255, 255, 255),
    (255, 0, 0)
]

script_running = False


# -----------------------------
# COLOR DETECTION
# -----------------------------

def check_red_color(pixel):
    b, g, r = pixel
    return r > 150 and g < 100 and b < 100


# -----------------------------
# CONTROL FUNCTIONS
# -----------------------------

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


# -----------------------------
# MAIN LOOP
# -----------------------------

while True:

    while script_running:

        # ONE screenshot per cycle
        screenshot = pyautogui.screenshot()

        # convert to OpenCV format
        frame = cv2.cvtColor(np.array(screenshot), cv2.COLOR_RGB2BGR)

        for i, (x, y) in enumerate(points):

            pixel = frame[y, x]

            # RED STOP CONDITION
            if i == 3:
                if check_red_color(pixel):
                    print("Red condition detected. Stopping script.")
                    script_running = False
                    break
                continue

            color = tuple(pixel)

            if color == target_colors[i]:

                if i == 0:
                    pyautogui.click(x, y)
                    print("Left click triggered")

                elif i == 1:
                    pyautogui.rightClick(x, y)
                    print("Right click triggered")

                elif i == 2:
                    pyautogui.press('esc')
                    print("Popup detected → ESC pressed")

                    time.sleep(0.5)

                    red_pixel = frame[1318, 1092]

                    if check_red_color(red_pixel):
                        print("Red detected. Stopping script.")
                        script_running = False
                        break
                    else:
                        time.sleep(1)
                        keyboard.press('1')
                        time.sleep(1)
                        keyboard.release('1')
                        print("Key 1 pressed")

            else:
                print(f"Waiting... pixel at ({x},{y}) not changed")

        time.sleep(0.02)

    time.sleep(0.5)
