<div align="center">

# 🤖 Quant Automation Suite

### Game automation toolkit for RageMP / GTA V RP

![Version](https://img.shields.io/badge/version-1.2-blue)
![Python](https://img.shields.io/badge/python-3.8%2B-yellow)
![Platform](https://img.shields.io/badge/platform-Windows%2010%2F11-lightgrey)
![Resolution](https://img.shields.io/badge/resolution-2560×1440-green)

[🇬🇧 English](#english) • [🇺🇦 Українська](#ukrainian)

</div>

---

<a name="english"></a>
# 🇬🇧 English

## What is this?

Quant Automation Suite is a set of Python automation scripts for RageMP / GTA V RP servers, managed through a single **Control Center** GUI. It handles repetitive in-game tasks like fishing, collecting items, and mini-games.

## 📦 Tools included

| Tool | Description |
|------|-------------|
| **MILK 6.13** | Mini-game zone automation with dual-color trigger and overlay |
| **Orange Picker** | HSV object detection + drag-to-box automation |
| **CARP v2.2** | Multi-point pixel fishing bot (50 checks/sec) |
| **CARP v1** | Classic single-point fishing automation |
| **Wood Clicker** | E-button detection + click spam |
| **Cursor Logger** | Built-in coordinate calibration tool |

## ⬇️ Download

> Choose the option that works for you:

### Option A — Single EXE (recommended, no Python needed)

1. Go to [**Releases**](../../releases/latest)
2. Download `QuantAutomationSuite.exe`
3. Double-click and run

> ⚠️ Windows Defender may warn you because the app simulates keyboard/mouse input.
> Click **More info → Run anyway**, or add an exclusion for the file.

### Option B — Python source (for developers)

1. Go to [**Releases**](../../releases/latest)
2. Download `FWMO_source.zip`
3. Extract anywhere
4. Install Python 3.8+ from [python.org](https://python.org)
5. Open terminal in the extracted folder and run:
```
pip install -r requirements.txt
python control_center.py
```

## 🎯 First-time setup

All scripts use pixel coordinates that depend on your screen layout. You need to calibrate them once using the built-in **Cursor Logger**.

1. Launch the app
2. Switch to **🖱️ Cursor Logger** tab
3. Select a script from the dropdown
4. Click **▶ Start Capture** — window minimizes automatically
5. Follow the tooltip floating near your cursor
6. Left-click each point on screen as instructed
7. Click **💾 Patch Script** to save coordinates
8. Restart the script

## 🖥️ System requirements

- Windows 10 / 11
- Resolution: **2560×1440** (recalibrate if different)
- Game in fullscreen or windowed fullscreen

## 🔧 Hotkeys

| Key | Action | Scripts |
|-----|--------|---------|
| `F9` | Start / Stop | MILK, Orange Picker, Wood Clicker |
| `9` | Start | CARP v1, CARP v2.2 |
| `0` | Stop | CARP v1, CARP v2.2 |
| Mouse → top-left corner | Emergency stop | All scripts |

## 🛠️ Troubleshooting

**Script not found error**
→ Make sure all `.py` files are in the same folder as `control_center.py`

**Script does nothing**
→ Recalibrate coordinates using Cursor Logger

**EXE blocked by antivirus**
→ Add file/folder to Windows Defender exclusions

**ModuleNotFoundError**
→ Run `pip install -r requirements.txt`

**CARP stops immediately**
→ Point 3 (red stop) is miscalibrated — recalibrate to a pixel that is only red when the stop condition is met

---

<a name="ukrainian"></a>
# 🇺🇦 Українська

## Що це таке?

Quant Automation Suite — набір Python скриптів для автоматизації рутинних дій на RageMP / GTA V RP серверах. Керується через єдиний **Control Center** з графічним інтерфейсом.

## 📦 Інструменти

| Інструмент | Опис |
|-----------|------|
| **MILK 6.13** | Автоматизація міні-гри з подвійним кольоровим тригером та оверлеєм |
| **Orange Picker** | HSV детекція об'єктів + перетягування в зону збору |
| **CARP v2.2** | Багатоточковий рибальський бот (50 перевірок/сек) |
| **CARP v1** | Класична рибалка за кольором пікселя |
| **Wood Clicker** | Детекція E-кнопки + клікер |
| **Cursor Logger** | Вбудований інструмент калібрування координат |

## ⬇️ Завантаження

### Варіант A — Один EXE файл (рекомендовано, Python не потрібен)

1. Перейди в [**Releases**](../../releases/latest)
2. Завантаж `QuantAutomationSuite.exe`
3. Запусти подвійним кліком

> ⚠️ Windows Defender може попередити про запуск, бо програма симулює введення з клавіатури/миші.
> Натисни **Детальніше → Все одно запустити**, або додай файл у виключення.

### Варіант B — Вихідний код Python (для розробників)

1. Перейди в [**Releases**](../../releases/latest)
2. Завантаж `FWMO_source.zip`
3. Розпакуй у будь-яке місце
4. Встанови Python 3.8+ з [python.org](https://python.org)
5. Відкрий термінал у розпакованій папці та виконай:
```
pip install -r requirements.txt
python control_center.py
```

## 🎯 Перше налаштування

Скрипти використовують координати пікселів, що залежать від розташування елементів на твоєму екрані. Потрібно один раз відкалібрувати через вбудований **Cursor Logger**.

1. Запусти програму
2. Перейди у вкладку **🖱️ Cursor Logger**
3. Вибери скрипт зі списку
4. Натисни **▶ Start Capture** — вікно згортається автоматично
5. Слідуй підказці що плаває поруч з курсором
6. Клікни лівою кнопкою на кожну точку на екрані
7. Натисни **💾 Patch Script** щоб зберегти координати
8. Перезапусти скрипт

### Які точки потрібні для кожного скрипта

**MILK 6.13** — 1 точка:
- Тригерний піксель (зелений або жовтий біля HP бару)

**Orange Picker** — 3 точки:
- Піксель E-кнопки
- Піксель зупинки (зелений)
- Центр зони скидання

**CARP v2.2 / v1** — 4 точки:
- Точка 0 — тригер лівого кліку
- Точка 1 — тригер правого кліку
- Точка 2 — детекція попапу (білий піксель)
- Точка 3 — зупинка (червоний піксель)

**Wood Clicker** — 1 точка:
- Піксель E-кнопки

## 🖥️ Системні вимоги

- Windows 10 / 11
- Роздільна здатність: **2560×1440** (потрібно перекалібрувати якщо інша)
- Гра у повноекранному або віконному повноекранному режимі

## 🔧 Гарячі клавіші

| Клавіша | Дія | Скрипти |
|---------|-----|---------|
| `F9` | Старт / Стоп | MILK, Orange Picker, Wood Clicker |
| `9` | Старт | CARP v1, CARP v2.2 |
| `0` | Стоп | CARP v1, CARP v2.2 |
| Миша → верхній лівий кут | Аварійна зупинка | Всі скрипти |

## 🛠️ Вирішення проблем

**"Script not found" помилка**
→ Переконайся що всі `.py` файли лежать в одній папці з `control_center.py`

**Скрипт запускається але нічого не робить**
→ Перекалібруй координати через Cursor Logger

**EXE блокує антивірус**
→ Додай файл або папку у виключення Windows Defender

**ModuleNotFoundError**
→ Виконай `pip install -r requirements.txt`

**CARP зупиняється одразу після старту**
→ Точка 3 (червона зупинка) неправильно відкалібрована — вибери піксель який стає червоним тільки при умові зупинки

---

<div align="center">

**Version 1.2** • Author: Andriy (NDLegion)

</div>
