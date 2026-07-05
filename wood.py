import pydirectinput as pyautogui
import time
import keyboard
from PIL import ImageGrab

# === Налаштування ===
CHECK_X, CHECK_Y = 1268, 1256
TARGET_COLOR = (254, 188, 32)
TOLERANCE = 10

CLICK_COUNT = 10
DELAY_BEFORE_CLICK = 1.5
DELAY_BETWEEN_CLICKS = 1.5

running = False
busy = False

pyautogui.FAILSAFE = False
pyautogui.PAUSE = 0

def is_color_match(c1, c2, tol):
    return all(abs(a - b) <= tol for a, b in zip(c1, c2))

def get_pixel(x, y):
    img = ImageGrab.grab()
    return img.getpixel((x, y))

def toggle():
    global running
    running = not running
    print("RUNNING:", running)

keyboard.add_hotkey("F9", toggle)

print("F9 - старт / стоп")

while True:
    if not running:
        time.sleep(0.1)
        continue

    if busy:
        time.sleep(0.1)
        continue

    pixel = get_pixel(CHECK_X, CHECK_Y)

    if is_color_match(pixel, TARGET_COLOR, TOLERANCE):
        print("Знайдено E")
        busy = True

        # Натискаємо E
        pyautogui.press('e')

        time.sleep(DELAY_BEFORE_CLICK)

        for i in range(CLICK_COUNT):

            # 🔴 ДАЄМО МОЖЛИВІСТЬ СТОПУ
            if not running:
                print("Зупинено під час кліків")
                break

            # 🔥 Замість click()
            pyautogui.mouseDown()
            time.sleep(0.05)
            pyautogui.mouseUp()

            print(f"Клік {i+1}")

            # ще одна перевірка перед сном
            for _ in range(int(DELAY_BETWEEN_CLICKS * 10)):
                if not running:
                    break
                time.sleep(0.1)

            if not running:
                break

        print("Цикл завершено")
        busy = False
        time.sleep(0.3)

    time.sleep(0.05)