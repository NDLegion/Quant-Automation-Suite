import pyautogui
import cv2
import numpy as np
from PIL import ImageGrab
import time
import keyboard

# ===== TRIGGER CONFIG =====
CHECK_X, CHECK_Y = 1242, 1254
E_BUTTON_COLORS = [(253, 202, 49), (255, 175, 17), (254, 188, 32)]
TOLERANCE = 15

# ===== STOP TRIGGER =====
STOP_X, STOP_Y = 1585, 1334
STOP_COLOR = (164, 210, 65)
STOP_TOLERANCE = 10

# ===== ZONES (2560x1440) =====
DETECTION_ZONE = {'x': 40, 'y': 0, 'width': 1710, 'height': 1440}
DROP_ZONE_CENTER = {'x': 2060, 'y': 920}

# ===== ORANGE DETECTION =====
ORANGE_LOWER = np.array([10, 140, 120])
ORANGE_UPPER = np.array([25, 255, 255])
MIN_ORANGE_AREA = 1500
MAX_ORANGE_AREA = 40000

DETECTION_PAUSE = 0.03
BLACKOUT_AFTER_DRAG = 0.15

# ===== MEMORY =====
recent_oranges = []
POSITION_TOLERANCE = 100
MEMORY_TIME = 2.0

running = False

# ===== HELPERS =====
def check_trigger_color():
    try:
        patch = np.array(ImageGrab.grab(bbox=(CHECK_X, CHECK_Y, CHECK_X+3, CHECK_Y+3)))
        for row in patch:
            for pixel in row:
                for target in E_BUTTON_COLORS:
                    if np.all(np.abs(pixel - target) <= TOLERANCE):
                        return True
        return False
    except:
        return False

def check_stop_color():
    try:
        patch = np.array(ImageGrab.grab(bbox=(STOP_X, STOP_Y, STOP_X+3, STOP_Y+3)))
        for row in patch:
            for pixel in row:
                if np.all(np.abs(pixel - STOP_COLOR) <= STOP_TOLERANCE):
                    return True
        return False
    except:
        return False

def capture_detection_zone():
    img = ImageGrab.grab(bbox=(
        DETECTION_ZONE['x'], DETECTION_ZONE['y'],
        DETECTION_ZONE['x'] + DETECTION_ZONE['width'],
        DETECTION_ZONE['y'] + DETECTION_ZONE['height']
    ))
    return cv2.cvtColor(np.array(img), cv2.COLOR_RGB2BGR)

def find_oranges(img):
    hsv = cv2.cvtColor(img, cv2.COLOR_BGR2HSV)
    mask = cv2.inRange(hsv, ORANGE_LOWER, ORANGE_UPPER)
    mask = cv2.GaussianBlur(mask, (7,7), 0)
    kernel = np.ones((5,5), np.uint8)
    mask = cv2.morphologyEx(mask, cv2.MORPH_OPEN, kernel)
    mask = cv2.morphologyEx(mask, cv2.MORPH_CLOSE, kernel)

    contours, _ = cv2.findContours(mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    result = []

    for c in contours:
        area = cv2.contourArea(c)
        if area < MIN_ORANGE_AREA or area > MAX_ORANGE_AREA:
            continue

        perimeter = cv2.arcLength(c, True)
        if perimeter == 0:
            continue
        circularity = 4 * np.pi * area / (perimeter * perimeter)
        if circularity < 0.65:
            continue

        x, y, w, h = cv2.boundingRect(c)
        if y < 50:  # ignore top UI
            continue
        aspect_ratio = w / float(h)
        if aspect_ratio < 0.7 or aspect_ratio > 1.3:
            continue

        cx = x + w//2
        cy = y + h//2
        result.append((cx, cy, area))

    return result

def is_new_orange(pos):
    """FIXED: Check first, cleanup after"""
    global recent_oranges
    now = time.time()
    
    # Check FIRST (against all entries, including those about to expire)
    for (p, t) in recent_oranges:
        if now - t < MEMORY_TIME:  # Only check non-expired entries
            distance = np.sqrt((pos[0]-p[0])**2 + (pos[1]-p[1])**2)
            if distance < POSITION_TOLERANCE:
                return False
    
    # Clean up AFTER checking
    recent_oranges = [(p, t) for (p, t) in recent_oranges if now - t < MEMORY_TIME]
    return True

def drag_orange_to_box(pos):
    global running
    abs_x = DETECTION_ZONE['x'] + pos[0]
    abs_y = DETECTION_ZONE['y'] + pos[1]

    pyautogui.moveTo(abs_x, abs_y)
    if not running: return False
    pyautogui.mouseDown()
    if not running:
        pyautogui.mouseUp()
        return False
    pyautogui.moveTo(DROP_ZONE_CENTER['x'], DROP_ZONE_CENTER['y'], duration=0.06)
    if not running:
        pyautogui.mouseUp()
        return False
    pyautogui.mouseUp()

    blackout_remaining = BLACKOUT_AFTER_DRAG
    chunk_size = 0.02
    while blackout_remaining > 0 and running:
        time.sleep(min(chunk_size, blackout_remaining))
        blackout_remaining -= chunk_size

    return running

# ===== MAIN =====
def main():
    global running, recent_oranges
    prev_trigger = False
    cycle_count = 0
    no_orange_counter = 0  # To reduce spam

    print("="*60)
    print("ORANGE PICKER - 2K Resolution (Optimized)")
    print("="*60)
    print(f"DETECTION_ZONE: {DETECTION_ZONE}")
    print(f"DROP_ZONE_CENTER: {DROP_ZONE_CENTER}")
    print(f"MEMORY_TIME: {MEMORY_TIME}s, POSITION_TOLERANCE: {POSITION_TOLERANCE}px")
    print("\nCONFIG:")
    print("  F9 - Start/Stop (manual)")
    print("  E button - Autostart")
    print("  Green point - Autostop")
    print("="*60)
    print("\n[IDLE] Waiting E or F9...\n")

    while True:
        if keyboard.is_pressed("F9"):
            running = not running
            if running:
                print("[F9] START - script working")
                recent_oranges = []
            else:
                print(f"[F9] STOP - collected {cycle_count} oranges")
                cycle_count = 0
                recent_oranges = []
                print("[IDLE] Waiting E or F9...")
            time.sleep(0.3)

        trigger = check_trigger_color()
        if not running and trigger and not prev_trigger:
            print("🟡 Finded E → press")
            pyautogui.press('e')
            time.sleep(0.8)
            running = True
            recent_oranges = []
            cycle_count = 0
            print("[ON] Start collecting\n")
        prev_trigger = trigger

        if running and check_stop_color():
            print(f"\n[STOP] Green trigger → collected {cycle_count} oranges")
            running = False
            cycle_count = 0
            recent_oranges = []
            print("[IDLE] Waiting E or F9...\n")
            time.sleep(0.5)
            continue

        if running:
            image = capture_detection_zone()
            oranges = find_oranges(image)
            
            # Only print when count changes to reduce spam
            if len(oranges) > 0:
                no_orange_counter = 0
                
            oranges.sort(key=lambda x: x[2], reverse=True)
            
            found_new = False
            for orange in oranges:
                pos = (orange[0], orange[1])
                if is_new_orange(pos):
                    cycle_count += 1
                    print(f"[{cycle_count}] Orange at {pos} → checked")
                    completed = drag_orange_to_box(pos)
                    if completed:
                        recent_oranges.append((pos, time.time()))
                        print(f"[{cycle_count}] ✓ OK (memory: {len(recent_oranges)})")
                    else:
                        cycle_count -= 1
                        print(f"❌ Stopped")
                    found_new = True
                    break
            
            if not found_new:
                no_orange_counter += 1
                if no_orange_counter % 20 == 1:  # Print every 20 attempts
                    print(f"Search... (find {len(oranges)}, all in memory)")
                time.sleep(DETECTION_PAUSE)
        else:
            time.sleep(0.05)

if __name__ == "__main__":
    pyautogui.FAILSAFE = True
    main()