# milk6.13_dual_color_overlay.py — milk6.12_03hot_fix + dual color trigger + overlay
import threading
import tkinter as tk
from tkinter import scrolledtext
from PIL import ImageGrab
import pyautogui
import numpy as np
import cv2
import time
import keyboard
import sys
import os
import json

# -----------------------------
# config file path
# -----------------------------
if getattr(sys, 'frozen', False):
    APP_DIR = os.path.dirname(sys.executable)
else:
    APP_DIR = os.path.dirname(__file__)

CONFIG_FILE = os.path.join(APP_DIR, "config.json")

# -----------------------------
# global parameters
# -----------------------------
running = False
marker_in_zone = False

start_stop_point = (1318, 668)
polygon_coords = np.array([
    [1465, 503],
    [1803, 502],
    [1820, 850],
    [1441, 863]
], np.int32).reshape((-1,1,2))

# detection masks
lower_white   = np.array([0, 0, 220])
upper_white   = np.array([180, 30, 255])
lower_green   = np.array([80, 40, 40])
upper_green   = np.array([100, 255, 200])
kernel        = np.ones((3,3), np.uint8)
space_delay   = 0.3

# DUAL COLOR SUPPORT for start/stop trigger
start_stop_colors = [
    (125, 192, 170),  # Original green color
    (216, 218, 108)   # New yellow color #d8da6c
]

# -----------------------------
# save / load config
# -----------------------------
def save_config():
    config = {
        "start_stop_point": list(start_stop_point),
        "polygon_coords":   polygon_coords.tolist()
    }
    with open(CONFIG_FILE, "w") as f:
        json.dump(config, f, indent=2)
    print("Config saved to config.json")

def load_config():
    global start_stop_point, polygon_coords
    if os.path.exists(CONFIG_FILE):
        try:
            with open(CONFIG_FILE) as f:
                config = json.load(f)
            start_stop_point = tuple(config["start_stop_point"])
            polygon_coords   = np.array(config["polygon_coords"], np.int32).reshape((-1,1,2))
            print("Config loaded from config.json")
        except Exception as e:
            print("Error loading config.json:", e)
            save_config()   # overwrite broken file with defaults
    else:
        save_config()       # create file with defaults
        print("config.json not found — created with default values")

load_config()

# -----------------------------
# overlays
# -----------------------------
def pick_start_point_overlay(callback):
    def on_click(event):
        callback(event.x_root, event.y_root)
        overlay.destroy()

    overlay = tk.Tk()
    overlay.attributes("-topmost", True)
    overlay.overrideredirect(True)
    overlay.geometry(f"{overlay.winfo_screenwidth()}x{overlay.winfo_screenheight()}+0+0")
    overlay.config(bg='black')
    overlay.attributes("-alpha", 0.3)
    overlay.bind("<Button-1>", on_click)
    overlay.mainloop()

def pick_polygon_overlay(callback):
    start_x = start_y = end_x = end_y = 0

    def on_button_press(event):
        nonlocal start_x, start_y
        start_x, start_y = event.x_root, event.y_root
        canvas.coords(rect, start_x, start_y, start_x, start_y)

    def on_move(event):
        nonlocal end_x, end_y
        end_x, end_y = event.x_root, event.y_root
        canvas.coords(rect, start_x, start_y, end_x, end_y)

    def on_release(event):
        callback((start_x, start_y, event.x_root, event.y_root))
        overlay.destroy()

    overlay = tk.Tk()
    overlay.attributes("-topmost", True)
    overlay.overrideredirect(True)
    overlay.geometry(f"{overlay.winfo_screenwidth()}x{overlay.winfo_screenheight()}+0+0")
    overlay.config(bg='black')
    overlay.attributes("-alpha", 0.3)

    canvas = tk.Canvas(overlay, bg='black', highlightthickness=0)
    canvas.pack(fill=tk.BOTH, expand=True)
    rect = canvas.create_rectangle(0, 0, 0, 0, outline='red', width=2)

    canvas.bind("<Button-1>", on_button_press)
    canvas.bind("<B1-Motion>", on_move)
    canvas.bind("<ButtonRelease-1>", on_release)

    overlay.mainloop()

# -----------------------------
# detection helpers
# -----------------------------
def check_color_patch(x, y, target_rgb, tolerance=10):
    """Check if a pixel matches target RGB color within tolerance"""
    patch = np.array(ImageGrab.grab(bbox=(x, y, x+3, y+3)))
    diff  = np.abs(patch - target_rgb)
    return np.all(diff <= tolerance)

def check_any_color_match(x, y, color_list, tolerance=10):
    """Check if pixel matches ANY color from the list"""
    for target_rgb in color_list:
        if check_color_patch(x, y, target_rgb, tolerance):
            return True
    return False

def get_screen_polygon_mask(screen_shape):
    mask = np.zeros(screen_shape[:2], dtype=np.uint8)
    cv2.fillPoly(mask, [polygon_coords], 255)
    return mask

def toggle_running():
    global running
    running = not running
    update_overlay_status()

# -----------------------------
# status overlay window
# -----------------------------
overlay_window = None
overlay_label = None

def create_status_overlay():
    """Create semi-transparent always-on-top status window at top-middle"""
    global overlay_window, overlay_label
    
    overlay_window = tk.Toplevel()
    overlay_window.title("")
    overlay_window.overrideredirect(True)  # Remove window decorations
    overlay_window.attributes("-topmost", True)  # Always on top
    overlay_window.attributes("-alpha", 0.4)  # Semi-transparent (40%)
    
    # Get screen width to center the window
    screen_width = overlay_window.winfo_screenwidth()
    window_width = 75   # 50% smaller (was 150)
    window_height = 25  # 50% smaller (was 50)
    x_position = (screen_width - window_width) // 2
    y_position = 10  # 10 pixels from top
    
    overlay_window.geometry(f"{window_width}x{window_height}+{x_position}+{y_position}")
    overlay_window.config(bg='#1a1a1a')
    
    # Status label
    overlay_label = tk.Label(
        overlay_window,
        text="IDLE",
        font=("Arial", 10, "bold"),  # Smaller font (was 16)
        fg="#00ff00",
        bg="#1a1a1a"
    )
    overlay_label.pack(expand=True)
    
    # Make window click-through on Windows (optional)
    try:
        overlay_window.attributes("-transparentcolor", "")
    except:
        pass

def update_overlay_status():
    """Update the overlay status text and color"""
    global overlay_label
    if overlay_label:
        if running:
            overlay_label.config(text="ON", fg="#00ff00")  # Green
        else:
            # Check if we're in IDLE or OFF state
            if check_any_color_match(*start_stop_point, start_stop_colors):
                overlay_label.config(text="IDLE", fg="#ffff00")  # Yellow
            else:
                overlay_label.config(text="OFF", fg="#ff0000")  # Red

# -----------------------------
# worker thread
# -----------------------------
def worker():
    global marker_in_zone, running
    prev_trigger_state = False

    while True:
        # F9 hotkey
        if keyboard.is_pressed("F9"):
            toggle_running()
            time.sleep(0.3)

        # DUAL COLOR trigger for auto start/stop
        current_trigger_state = check_any_color_match(*start_stop_point, start_stop_colors)

        # Auto-start: color appears
        if not running and current_trigger_state and not prev_trigger_state:
            running = True
            update_overlay_status()
            print("Script started (color trigger)")

        # Auto-stop: color disappears
        elif running and not current_trigger_state and prev_trigger_state:
            running = False
            update_overlay_status()
            print("Script stopped (color trigger)")

        prev_trigger_state = current_trigger_state

        # Update overlay when idle
        if not running:
            update_overlay_status()

        if running:
            screen = np.array(ImageGrab.grab())
            mask   = get_screen_polygon_mask(screen.shape)
            hsv    = cv2.cvtColor(screen, cv2.COLOR_RGB2HSV)

            white_mask = cv2.inRange(hsv, lower_white, upper_white)
            green_mask = cv2.inRange(hsv, lower_green, upper_green)

            # FIX: dilation makes detection tolerant to small misalignments
            white_mask = cv2.dilate(white_mask, kernel, iterations=1)
            green_mask = cv2.dilate(green_mask, kernel, iterations=1)

            combined      = cv2.bitwise_and(white_mask, green_mask)
            white_in_zone = cv2.bitwise_and(combined, mask)

            if cv2.countNonZero(white_in_zone) > 0:
                if not marker_in_zone:
                    print("White marker detected in zone")
                    pyautogui.press('space')
                    marker_in_zone = True
            else:
                marker_in_zone = False

        time.sleep(0.05)

# -----------------------------
# manual window
# -----------------------------
def show_manual():
    manual_text = """MANUAL:

1. The game must be in a full-screen window without frames
2. The interaction icon (before pressing E) must be on the left side of the screen so as not to overlap the HUD mini-game elements
3. Accuracy is reduced to 98% to prevent anti-bot detection and "human" interaction.
4. If config.json is not present, it is created automatically with default coordinates. If the file exists, the coordinates are loaded from it.
5. The config.json file is created automatically when the software is started and must be changed using the tools for changing the point in the green zone on the left side of the HUD (hp bar) and the tool for determining the location of the circle with colored segments.
6. The .exe file and the config.json file must be in the same folder.

NEW FEATURES:
- Dual-color detection: Script now triggers on BOTH green (#7dc0aa) and yellow (#d8da6c) colors
- Semi-transparent status overlay: Always-on-top window at top-middle shows current status
  * IDLE (Yellow) - Waiting for trigger color
  * ON (Green) - Script is running
  * OFF (Red) - Script stopped, no trigger color detected
"""
    window = tk.Toplevel(root)
    window.title("Manual")
    window.geometry("600x400")

    text_area = scrolledtext.ScrolledText(window, wrap=tk.WORD, font=("Arial", 10))
    text_area.pack(expand=True, fill="both", padx=10, pady=10)
    text_area.insert(tk.END, manual_text)
    text_area.config(state="disabled")

# -----------------------------
# config setters (always save)
# -----------------------------
def set_start_point(x, y):
    global start_stop_point
    start_stop_point = (x, y)
    print(f"New start/stop point: {start_stop_point}")
    save_config()

def set_polygon_coords(coords):
    global polygon_coords
    x1, y1, x2, y2 = coords
    polygon_coords = np.array([
        [x1, y1], [x2, y1],
        [x2, y2], [x1, y2]
    ], np.int32).reshape((-1,1,2))
    print(f"New zone: {polygon_coords.tolist()}")
    save_config()

# -----------------------------
# GUI
# -----------------------------
root = tk.Tk()
root.title("Q5 MILK 6.13 Dual-Color + Overlay")
root.geometry("400x300")

status_text = tk.StringVar()
status_text.set("IDLE")

tk.Label(root, text="Status:").pack(pady=10)
tk.Label(root, textvariable=status_text, font=("Arial", 16)).pack()

tk.Button(root, text="Choose start/stop point",
          command=lambda: pick_start_point_overlay(set_start_point)).pack(pady=5)

tk.Button(root, text="Choose circle zone",
          command=lambda: pick_polygon_overlay(set_polygon_coords)).pack(pady=5)

tk.Button(root, text="Start/Stop (F9)", command=toggle_running).pack(pady=5)

tk.Button(root, text="Manual", command=show_manual).pack(pady=10)

# -----------------------------
# create status overlay
# -----------------------------
create_status_overlay()

# -----------------------------
# start worker thread
# -----------------------------
threading.Thread(target=worker, daemon=True).start()

root.mainloop()