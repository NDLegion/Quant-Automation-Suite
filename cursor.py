import pyautogui
from pynput import mouse

# Функція, котра буде викликана якщо натиснути ліву кнопку миші
def on_click(x, y, button, pressed):
    if pressed and button == mouse.Button.left:
        print('Натиснута ліва кнопка миші в точці (x={}, y={})'.format(x, y))
    if pressed and button == mouse.Button.right:
        print('Натиснута права кнопка миші в точці (x={}, y={})'.format(x, y))
# Прослуховування натискання миші
with mouse.Listener(on_click=on_click) as listener:
    listener.join()
