import tkinter as tk
from tkinter import ttk, messagebox, scrolledtext
import subprocess
import threading
import os
import sys
import re
import shutil
import tempfile
from datetime import datetime

# =========================
# AUTOMATION SUITE LAUNCHER
# =========================

def get_base_dir():
    """
    Works both in dev (plain .py) and frozen PyInstaller .exe.
    For .exe: extracts scripts to a stable temp folder next to the .exe.
    """
    if getattr(sys, 'frozen', False):
        # Running as PyInstaller .exe
        exe_dir = os.path.dirname(sys.executable)
        work_dir = os.path.join(exe_dir, '_fwmo_scripts')
        os.makedirs(work_dir, exist_ok=True)

        # Scripts bundled inside the .exe as data files
        scripts = [
            'milk6_13.py',
            'oranges_1_0.py',
            'fishing_V2_2.py',
            'fishing_v1.py',
            'wood.py',
            'cursor.py',
        ]
        meipass = sys._MEIPASS
        for fname in scripts:
            src = os.path.join(meipass, fname)
            dst = os.path.join(work_dir, fname)
            # Only copy if source exists and dest is missing or outdated
            if os.path.exists(src):
                if not os.path.exists(dst) or \
                   os.path.getmtime(src) > os.path.getmtime(dst):
                    shutil.copy2(src, dst)

        # Also copy config.json if it doesn't exist yet (don't overwrite user config)
        cfg_src = os.path.join(meipass, 'config.json')
        cfg_dst = os.path.join(work_dir, 'config.json')
        if os.path.exists(cfg_src) and not os.path.exists(cfg_dst):
            shutil.copy2(cfg_src, cfg_dst)

        return work_dir
    else:
        # Running as plain .py — scripts are in the same folder
        return os.path.dirname(os.path.abspath(__file__))


BASE_DIR = get_base_dir()


# ─────────────────────────────────────────────
# CURSOR LOGGER CONFIG
# ─────────────────────────────────────────────
CURSOR_POINTS = {
    'MILK 6.13': [
        {
            'key':   'start_stop_point',
            'label': 'Start/Stop trigger point',
            'hint':  '🎯 Click on the green/yellow trigger pixel\n(left side of screen near HP bar)',
            'type':  'single'
        },
    ],
    'ORANGE PICKER': [
        {
            'key':   'CHECK_XY',
            'label': 'E-button trigger point',
            'hint':  '🎯 Click on the E-button icon pixel\n(trigger to start collecting)',
            'type':  'single'
        },
        {
            'key':   'STOP_XY',
            'label': 'Stop trigger point',
            'hint':  '🎯 Click on the green stop-trigger pixel\n(signals end of collecting)',
            'type':  'single'
        },
        {
            'key':   'DROP_ZONE_CENTER',
            'label': 'Drop zone center',
            'hint':  '🎯 Click on the center of the drop box\n(where oranges are dragged to)',
            'type':  'single'
        },
    ],
    'CARP v2.2': [
        {
            'key':   'point_0',
            'label': 'Point 0 — Left click trigger',
            'hint':  '🎯 Click the LEFT-CLICK trigger pixel\n(triggers left mouse click)',
            'type':  'single'
        },
        {
            'key':   'point_1',
            'label': 'Point 1 — Right click trigger',
            'hint':  '🎯 Click the RIGHT-CLICK trigger pixel\n(triggers right mouse click)',
            'type':  'single'
        },
        {
            'key':   'point_2',
            'label': 'Point 2 — Popup detection',
            'hint':  '🎯 Click the POPUP detection pixel\n(white pixel when popup appears)',
            'type':  'single'
        },
        {
            'key':   'point_3',
            'label': 'Point 3 — Red stop detection',
            'hint':  '🎯 Click the RED STOP pixel\n(red pixel that stops the script)',
            'type':  'single'
        },
    ],
    'CARP v1': [
        {
            'key':   'point_0',
            'label': 'Point 0 — Left click trigger',
            'hint':  '🎯 Click the LEFT-CLICK trigger pixel\n(triggers left mouse click)',
            'type':  'single'
        },
        {
            'key':   'point_1',
            'label': 'Point 1 — Right click trigger',
            'hint':  '🎯 Click the RIGHT-CLICK trigger pixel\n(triggers right mouse click)',
            'type':  'single'
        },
        {
            'key':   'point_2',
            'label': 'Point 2 — Popup detection',
            'hint':  '🎯 Click the POPUP detection pixel\n(white pixel when popup appears)',
            'type':  'single'
        },
        {
            'key':   'point_3',
            'label': 'Point 3 — Red stop detection',
            'hint':  '🎯 Click the RED STOP pixel\n(red pixel that stops the script)',
            'type':  'single'
        },
    ],
    'WOOD CLICKER': [
        {
            'key':   'CHECK_XY',
            'label': 'E-button trigger point',
            'hint':  '🎯 Click on the E-button icon pixel\n(trigger to start chopping)',
            'type':  'single'
        },
    ],
}


def patch_script(script_path, tool_name, captured_points):
    """Rewrite coordinate variables inside a script file."""
    with open(script_path, 'r', encoding='utf-8') as f:
        source = f.read()

    point_defs = CURSOR_POINTS[tool_name]

    for i, (x, y) in enumerate(captured_points):
        key = point_defs[i]['key']

        if tool_name in ('CARP v2.2', 'CARP v1'):
            def replace_nth_point(src, idx, nx, ny):
                m = re.search(r'(points\s*=\s*\[)(.*?)(\])', src, re.DOTALL)
                if not m:
                    return src
                before = m.group(1)
                inner  = m.group(2)
                after  = m.group(3)
                count  = [0]
                def replacer(match):
                    count[0] += 1
                    if count[0] == idx + 1:
                        return f'({nx}, {ny})'
                    return match.group(0)
                new_inner = re.sub(r'\(\s*\d+\s*,\s*\d+\s*\)', replacer, inner)
                return src[:m.start()] + before + new_inner + after + src[m.end():]
            source = replace_nth_point(source, i, x, y)

        elif key == 'start_stop_point':
            source = re.sub(
                r'start_stop_point\s*=\s*\(\s*\d+\s*,\s*\d+\s*\)',
                f'start_stop_point = ({x}, {y})',
                source
            )

        elif key == 'CHECK_XY':
            source = re.sub(
                r'CHECK_X\s*,\s*CHECK_Y\s*=\s*\d+\s*,\s*\d+',
                f'CHECK_X, CHECK_Y = {x}, {y}',
                source
            )

        elif key == 'STOP_XY':
            source = re.sub(
                r'STOP_X\s*,\s*STOP_Y\s*=\s*\d+\s*,\s*\d+',
                f'STOP_X, STOP_Y = {x}, {y}',
                source
            )

        elif key == 'DROP_ZONE_CENTER':
            source = re.sub(
                r"DROP_ZONE_CENTER\s*=\s*\{\s*'x'\s*:\s*\d+\s*,\s*'y'\s*:\s*\d+\s*\}",
                f"DROP_ZONE_CENTER = {{'x': {x}, 'y': {y}}}",
                source
            )

    with open(script_path, 'w', encoding='utf-8') as f:
        f.write(source)


# ─────────────────────────────────────────────
# TOOLTIP OVERLAY
# ─────────────────────────────────────────────
class CursorTooltip:
    def __init__(self, root, text):
        self.root = root
        self.win  = tk.Toplevel(root)
        self.win.overrideredirect(True)
        self.win.attributes('-topmost', True)
        self.win.attributes('-alpha', 0.92)
        self.win.config(bg='#1e1e2e')

        self.label = tk.Label(
            self.win, text=text,
            font=('Arial', 10, 'bold'),
            fg='#cdd6f4', bg='#1e1e2e',
            justify=tk.LEFT,
            padx=14, pady=10,
        )
        self.label.pack()
        self._follow()

    def _follow(self):
        try:
            x = self.root.winfo_pointerx() + 22
            y = self.root.winfo_pointery() + 22
            self.win.geometry(f'+{x}+{y}')
            self.win.after(30, self._follow)
        except Exception:
            pass

    def update_text(self, text):
        self.label.config(text=text)

    def destroy(self):
        try:
            self.win.destroy()
        except Exception:
            pass


# ─────────────────────────────────────────────
# CURSOR LOGGER SESSION
# ─────────────────────────────────────────────
class CursorLoggerSession:
    def __init__(self, root, tool_name, point_defs, on_done, on_cancel):
        self.root       = root
        self.tool_name  = tool_name
        self.point_defs = point_defs
        self.on_done    = on_done
        self.on_cancel  = on_cancel
        self.results    = []
        self.current    = 0

        self.overlay = tk.Toplevel(root)
        self.overlay.overrideredirect(True)
        self.overlay.attributes('-topmost', True)
        self.overlay.attributes('-alpha', 0.01)
        sw = self.overlay.winfo_screenwidth()
        sh = self.overlay.winfo_screenheight()
        self.overlay.geometry(f'{sw}x{sh}+0+0')
        self.overlay.config(cursor='crosshair')
        self.overlay.bind('<Button-1>', self._on_click)
        self.overlay.bind('<Escape>',   self._on_escape)
        self.overlay.focus_force()

        self.tooltip = CursorTooltip(self.overlay, self._hint_text())

    def _hint_text(self):
        p     = self.point_defs[self.current]
        total = len(self.point_defs)
        return (
            f"[{self.current+1}/{total}]  {p['label']}\n"
            f"{p['hint']}\n\n"
            f"  Left click — capture point\n"
            f"  ESC — cancel"
        )

    def _on_click(self, event):
        x = self.overlay.winfo_pointerx()
        y = self.overlay.winfo_pointery()
        self.results.append((x, y))
        self.current += 1
        if self.current >= len(self.point_defs):
            self._finish()
        else:
            self.tooltip.update_text(self._hint_text())

    def _on_escape(self, event):
        self._cancel()

    def _finish(self):
        self.tooltip.destroy()
        self.overlay.destroy()
        self.on_done(self.results)

    def _cancel(self):
        self.tooltip.destroy()
        self.overlay.destroy()
        self.on_cancel()


# ─────────────────────────────────────────────
# MAIN APP
# ─────────────────────────────────────────────
class AutomationLauncher:
    def __init__(self, root):
        self.root = root
        self.root.title('🤖 Quant Automation Suite - Control Center')
        self.root.geometry('1000x700')
        self.root.resizable(True, True)

        self.base_dir = BASE_DIR

        self.processes = {
            'MILK 6.13':    None,
            'ORANGE PICKER':None,
            'CARP v2.2':    None,
            'CARP v1':      None,
            'WOOD CLICKER': None,
        }

        self.script_paths = {
            'MILK 6.13':    'milk6_13.py',
            'ORANGE PICKER':'oranges_1_0.py',
            'CARP v2.2':    'fishing_V2_2.py',
            'CARP v1':      'fishing_v1.py',
            'WOOD CLICKER': 'wood.py',
        }

        self.descriptions = {
            'MILK 6.13':    'Zone-based mini-game automation\nDual-color detection with overlay',
            'ORANGE PICKER':'Object detection & drag automation\nOptimized for 2560×1440 resolution',
            'CARP v2.2':    'Multi-point pixel monitoring (v2.2)\nLightweight, 40-50 checks/sec',
            'CARP v1':      'Original CARP fishing automation\nSimple color-based triggering',
            'WOOD CLICKER': 'Rapid click automation\nColor trigger-based',
        }

        self.setup_ui()
        self.update_status()

    # ──────────────────────────────────────
    # UI SETUP
    # ──────────────────────────────────────
    def setup_ui(self):
        header_frame = ttk.Frame(self.root)
        header_frame.pack(fill=tk.X, padx=10, pady=10)
        ttk.Label(header_frame, text='🤖 Quant Automation Suite',
                  font=('Arial', 16, 'bold')).pack(side=tk.LEFT)
        ttk.Label(header_frame, text='Control Center v2.1',
                  font=('Arial', 10), foreground='gray').pack(side=tk.LEFT, padx=20)

        # Show working directory
        ttk.Label(header_frame, text=f'📁 {self.base_dir}',
                  font=('Arial', 8), foreground='#aaaaaa').pack(side=tk.RIGHT, padx=10)

        status_frame = ttk.LabelFrame(self.root, text='System Status')
        status_frame.pack(fill=tk.X, padx=10, pady=5)
        self.status_label = ttk.Label(status_frame, text='Ready', font=('Arial', 10))
        self.status_label.pack(side=tk.LEFT, padx=10, pady=5)

        self.notebook = ttk.Notebook(self.root)
        self.notebook.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

        self.create_launcher_tab()
        self.create_cursor_logger_tab()
        self.create_config_tab()
        self.create_logs_tab()
        self.create_about_tab()

    # ── Launcher tab ──────────────────────
    def create_launcher_tab(self):
        launcher_frame = ttk.Frame(self.notebook)
        self.notebook.add(launcher_frame, text='🚀 Launcher')
        tools_frame = ttk.Frame(launcher_frame)
        tools_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        self.tool_buttons       = {}
        self.tool_status_labels = {}
        for idx, (tool_name, description) in enumerate(self.descriptions.items()):
            self.create_tool_panel(tools_frame, tool_name, description, idx)

    def create_tool_panel(self, parent, tool_name, description, row):
        tool_frame = ttk.LabelFrame(parent, text=f'  {tool_name}  ', padding=10)
        tool_frame.pack(fill=tk.X, pady=5)

        left_frame = ttk.Frame(tool_frame)
        left_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        ttk.Label(left_frame, text=description,
                  font=('Arial', 9), justify=tk.LEFT,
                  foreground='#666666').pack(anchor=tk.W)

        right_frame = ttk.Frame(tool_frame)
        right_frame.pack(side=tk.RIGHT, padx=10)

        btn = ttk.Button(right_frame, text='▶ START',
                         command=lambda t=tool_name: self.toggle_tool(t))
        btn.pack(side=tk.LEFT, padx=5)
        self.tool_buttons[tool_name] = btn

        status_label = ttk.Label(right_frame, text='⚫ Idle',
                                 foreground='#666666', font=('Arial', 9, 'bold'))
        status_label.pack(side=tk.LEFT, padx=10)
        self.tool_status_labels[tool_name] = status_label

    # ── Cursor Logger tab ─────────────────
    def create_cursor_logger_tab(self):
        self.cursor_frame = ttk.Frame(self.notebook)
        self.notebook.add(self.cursor_frame, text='🖱️ Cursor Logger')
        self.notebook.bind('<<NotebookTabChanged>>', self._on_tab_changed)
        self._build_cursor_logger_ui()

    def _on_tab_changed(self, event):
        selected = self.notebook.tab(self.notebook.select(), 'text')
        if selected == '🖱️ Cursor Logger':
            self._refresh_cursor_logger_ui()

    def _build_cursor_logger_ui(self):
        ttk.Label(self.cursor_frame,
                  text='Cursor Logger — Patch script coordinates',
                  font=('Arial', 12, 'bold')).pack(pady=(15, 5))

        self.cursor_active_label = ttk.Label(
            self.cursor_frame, text='No script running',
            font=('Arial', 10), foreground='gray'
        )
        self.cursor_active_label.pack(pady=2)

        sel_frame = ttk.Frame(self.cursor_frame)
        sel_frame.pack(pady=8)
        ttk.Label(sel_frame, text='Target script:').pack(side=tk.LEFT, padx=5)
        self.cursor_script_var = tk.StringVar()
        self.cursor_script_combo = ttk.Combobox(
            sel_frame,
            textvariable=self.cursor_script_var,
            values=list(CURSOR_POINTS.keys()),
            state='readonly',
            width=20
        )
        self.cursor_script_combo.pack(side=tk.LEFT, padx=5)
        self.cursor_script_combo.bind('<<ComboboxSelected>>', self._on_script_selected)

        list_frame = ttk.LabelFrame(self.cursor_frame, text='Points to capture', padding=10)
        list_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=5)
        self.points_listbox = tk.Listbox(
            list_frame, font=('Courier', 10),
            selectmode=tk.SINGLE, height=8,
            bg='#f8f8f8', fg='#222222',
            selectbackground='#4a9eff',
        )
        self.points_listbox.pack(fill=tk.BOTH, expand=True)

        self.captured_frame = ttk.LabelFrame(self.cursor_frame,
                                              text='Captured coordinates', padding=10)
        self.captured_frame.pack(fill=tk.X, padx=20, pady=5)
        self.captured_text = tk.Text(
            self.captured_frame, height=5,
            font=('Courier', 9), bg='#1e1e2e', fg='#a6e3a1',
            state=tk.DISABLED
        )
        self.captured_text.pack(fill=tk.X)

        btn_frame = ttk.Frame(self.cursor_frame)
        btn_frame.pack(pady=10)

        self.capture_btn = ttk.Button(
            btn_frame, text='▶ Start Capture',
            command=self._start_capture
        )
        self.capture_btn.pack(side=tk.LEFT, padx=8)

        self.patch_btn = ttk.Button(
            btn_frame, text='💾 Patch Script',
            command=self._patch_script,
            state=tk.DISABLED
        )
        self.patch_btn.pack(side=tk.LEFT, padx=8)

        self.reset_btn = ttk.Button(
            btn_frame, text='🔄 Reset',
            command=self._reset_capture
        )
        self.reset_btn.pack(side=tk.LEFT, padx=8)

        self.cursor_status_var = tk.StringVar(value='Select a script to begin.')
        ttk.Label(self.cursor_frame, textvariable=self.cursor_status_var,
                  font=('Arial', 9), foreground='gray').pack(pady=(0, 10))

        self._captured_coords = []
        self._selected_tool   = None

    def _refresh_cursor_logger_ui(self):
        running_tools = [name for name, proc in self.processes.items()
                         if proc is not None and name in CURSOR_POINTS]
        if running_tools:
            self.cursor_active_label.config(
                text=f'Running: {", ".join(running_tools)}',
                foreground='#00AA00'
            )
            if not self.cursor_script_var.get() or \
               self.cursor_script_var.get() not in running_tools:
                self.cursor_script_var.set(running_tools[0])
                self._on_script_selected(None)
        else:
            self.cursor_active_label.config(
                text='No script running — you can still patch any script',
                foreground='#FF8800'
            )

    def _on_script_selected(self, event):
        tool = self.cursor_script_var.get()
        if not tool:
            return
        self._selected_tool   = tool
        self._captured_coords = []
        self.points_listbox.delete(0, tk.END)
        for p in CURSOR_POINTS[tool]:
            self.points_listbox.insert(tk.END, f'  ○  {p["label"]}')
        self._update_captured_display()
        self.patch_btn.config(state=tk.DISABLED)
        self.cursor_status_var.set(
            f'Ready to capture {len(CURSOR_POINTS[tool])} point(s) for {tool}.')

    def _start_capture(self):
        tool = self.cursor_script_var.get()
        if not tool:
            messagebox.showwarning('No script', 'Please select a script first.')
            return
        self._selected_tool   = tool
        self._captured_coords = []
        self._update_captured_display()
        self.patch_btn.config(state=tk.DISABLED)
        self.cursor_status_var.set('Capture started — follow the tooltip on screen...')
        self.log(f'🖱️ Cursor Logger: capturing {len(CURSOR_POINTS[tool])} point(s) for {tool}')
        self.root.iconify()
        self.root.after(300, lambda: self._run_session(tool, CURSOR_POINTS[tool]))

    def _run_session(self, tool, point_defs):
        CursorLoggerSession(
            self.root, tool, point_defs,
            on_done=self._on_capture_done,
            on_cancel=self._on_capture_cancel
        )

    def _on_capture_done(self, coords):
        self.root.deiconify()
        self._captured_coords = coords
        tool = self._selected_tool
        self.points_listbox.delete(0, tk.END)
        for i, p in enumerate(CURSOR_POINTS[tool]):
            x, y = coords[i]
            self.points_listbox.insert(tk.END, f'  ✓  {p["label"]}  →  ({x}, {y})')
            self.points_listbox.itemconfig(i, fg='#007700')
        self._update_captured_display()
        self.patch_btn.config(state=tk.NORMAL)
        self.cursor_status_var.set(
            f'✓ All {len(coords)} points captured. Click "Patch Script" to apply.')
        self.log(f'✓ Cursor Logger: all points captured for {tool}')
        for i, (x, y) in enumerate(coords):
            self.log(f'   [{i}] {CURSOR_POINTS[tool][i]["label"]}: ({x}, {y})')

    def _on_capture_cancel(self):
        self.root.deiconify()
        self.cursor_status_var.set('Capture cancelled.')
        self.log('⚠️ Cursor Logger: capture cancelled by user')

    def _update_captured_display(self):
        self.captured_text.config(state=tk.NORMAL)
        self.captured_text.delete(1.0, tk.END)
        if not self._captured_coords:
            self.captured_text.insert(tk.END, '  — no coordinates captured yet —')
        else:
            tool = self._selected_tool
            for i, (x, y) in enumerate(self._captured_coords):
                label = CURSOR_POINTS[tool][i]['label']
                self.captured_text.insert(tk.END, f'  [{i}] {label}\n       x={x}, y={y}\n')
        self.captured_text.config(state=tk.DISABLED)

    def _patch_script(self):
        tool = self._selected_tool
        if not tool or not self._captured_coords:
            return
        script_rel  = self.script_paths.get(tool)
        script_path = os.path.join(self.base_dir, script_rel)
        if not os.path.exists(script_path):
            messagebox.showerror('Error', f'Script not found:\n{script_path}')
            return
        expected = len(CURSOR_POINTS[tool])
        if len(self._captured_coords) != expected:
            messagebox.showerror('Error',
                f'Expected {expected} points, got {len(self._captured_coords)}.')
            return
        try:
            patch_script(script_path, tool, self._captured_coords)
            self.cursor_status_var.set(f'✅ Script patched: {script_rel}')
            self.log(f'💾 Patched {script_rel} with new coordinates for {tool}')
            messagebox.showinfo('Done', f'Script patched successfully:\n{script_path}')
        except Exception as e:
            messagebox.showerror('Patch Error', f'Failed to patch script:\n{e}')
            self.log(f'❌ Patch error for {tool}: {e}')

    def _reset_capture(self):
        self._captured_coords = []
        tool = self.cursor_script_var.get()
        if tool:
            self.points_listbox.delete(0, tk.END)
            for p in CURSOR_POINTS[tool]:
                self.points_listbox.insert(tk.END, f'  ○  {p["label"]}')
        self._update_captured_display()
        self.patch_btn.config(state=tk.DISABLED)
        self.cursor_status_var.set('Reset. Ready to capture again.')

    # ── Config tab ────────────────────────
    def create_config_tab(self):
        config_frame = ttk.Frame(self.notebook)
        self.notebook.add(config_frame, text='⚙️ Configuration')
        info_text = """
TOOL CONFIGURATIONS
═════════════════════════════════════════════════════════════

MILK 6.13:
  • Start/Stop Point: set via Cursor Logger
  • Zone: Click "Choose circle zone" inside the tool GUI
  • F9: Toggle start/stop
  • Colors: Dual-color detection (green + yellow)

ORANGE PICKER:
  • 3 points: E-trigger, Stop-trigger, Drop zone — set via Cursor Logger
  • Detection Zone: x=40, width=1710 (fixed, no point needed)
  • F9: Manual toggle

CARP v2.2 (Recommended):
  • 4 monitor points — set via Cursor Logger
  • Hotkeys: 9=start, 0=stop

CARP v1:
  • 4 monitor points — set via Cursor Logger
  • Same hotkeys as v2.2

WOOD CLICKER:
  • 1 trigger point — set via Cursor Logger
  • Color: RGB(254, 188, 32) — edit in script if needed

═════════════════════════════════════════════════════════════

HOW TO USE CURSOR LOGGER:
  1. Switch to 🖱️ Cursor Logger tab
  2. Select the target script from dropdown
  3. Click "▶ Start Capture"  (window minimizes automatically)
  4. Follow the tooltip floating near your cursor
  5. Left-click each point when you see the right pixel
  6. Click "💾 Patch Script" to write coordinates to file
  7. Restart the script to apply changes

ESC cancels capture at any time.
        """
        text_widget = scrolledtext.ScrolledText(config_frame, wrap=tk.WORD,
                                                font=('Courier', 9))
        text_widget.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        text_widget.insert(tk.END, info_text)
        text_widget.config(state=tk.DISABLED)

    # ── Logs tab ──────────────────────────
    def create_logs_tab(self):
        logs_frame = ttk.Frame(self.notebook)
        self.notebook.add(logs_frame, text='📋 Logs')
        button_frame = ttk.Frame(logs_frame)
        button_frame.pack(fill=tk.X, padx=10, pady=5)
        ttk.Button(button_frame, text='Clear Logs',
                   command=self.clear_logs).pack(side=tk.LEFT, padx=5)
        ttk.Button(button_frame, text='Export Logs',
                   command=self.export_logs).pack(side=tk.LEFT, padx=5)
        self.log_text = scrolledtext.ScrolledText(logs_frame,
                                                   font=('Courier', 8),
                                                   bg='#f0f0f0')
        self.log_text.pack(fill=tk.BOTH, expand=True, padx=10, pady=5)
        self.log(f'[{self.get_time()}] System started')
        self.log(f'[{self.get_time()}] Base directory: {self.base_dir}')
        self.log(f'[{self.get_time()}] Frozen (EXE): {getattr(sys, "frozen", False)}')
        self.log(f'[{self.get_time()}] Quant Automation Suite v2.1 ready')

    # ── About tab ─────────────────────────
    def create_about_tab(self):
        about_frame = ttk.Frame(self.notebook)
        self.notebook.add(about_frame, text='ℹ️ About')
        about_text = """
QUANT AUTOMATION SUITE v2.1
═══════════════════════════════════════════════════════════════

🎯 QUICK START:
  1. Switch to 🖱️ Cursor Logger tab
  2. Select script → capture coordinates → patch
  3. Start the tool with ▶ START in Launcher tab
  4. Use hotkeys to control

📦 TOOLS:
  • MILK 6.13      - Mini-game zone automation
  • ORANGE PICKER  - Object detection & dragging
  • CARP v2.2      - Multi-point fishing automation
  • CARP v1        - Classic fishing automation
  • WOOD CLICKER   - Click spam automation

🔧 HOTKEYS:
  F9   - Start/Stop (MILK, ORANGE, WOOD)
  9    - Start (CARP)
  0    - Stop  (CARP)
  ESC  - Cancel cursor capture

⚠️  Move mouse to TOP-LEFT corner = emergency stop (PyAutoGUI failsafe)

═══════════════════════════════════════════════════════════════
Version: 2.1  |  Author: NDLegion  |  Status: Stable ✓
        """
        text_widget = scrolledtext.ScrolledText(about_frame, wrap=tk.WORD,
                                                font=('Arial', 9))
        text_widget.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        text_widget.insert(tk.END, about_text)
        text_widget.config(state=tk.DISABLED)

    # ──────────────────────────────────────
    # TOOL LAUNCH / STOP
    # ──────────────────────────────────────
    def toggle_tool(self, tool_name):
        if self.processes[tool_name] is None:
            self.start_tool(tool_name)
        else:
            self.stop_tool(tool_name)

    def start_tool(self, tool_name):
        script_rel  = self.script_paths.get(tool_name)
        script_path = os.path.join(self.base_dir, script_rel)

        if not script_rel or not os.path.exists(script_path):
            self.log(f'❌ ERROR: Script not found: {script_path}')
            messagebox.showerror('Error', f'Script not found:\n{script_path}')
            return

        try:
            self.processes[tool_name] = subprocess.Popen(
                [sys.executable, script_path],
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                universal_newlines=True,
                cwd=self.base_dir
            )
            self.log(f'✓ {tool_name} started (PID: {self.processes[tool_name].pid})')
            self.log(f'  └─ {script_path}')
            self.tool_buttons[tool_name].config(text='⏹ STOP')
            self.tool_status_labels[tool_name].config(text='🟢 Running',
                                                       foreground='#00AA00')
            threading.Thread(target=self.monitor_tool, args=(tool_name,),
                             daemon=True).start()
        except Exception as e:
            self.log(f'❌ ERROR starting {tool_name}: {e}')
            messagebox.showerror('Launch Error', f'Failed to start {tool_name}:\n{e}')

    def stop_tool(self, tool_name):
        if self.processes[tool_name] is not None:
            try:
                self.processes[tool_name].terminate()
                self.processes[tool_name].wait(timeout=3)
                self.log(f'⏹ {tool_name} stopped')
            except Exception as e:
                self.log(f'⚠️ Error stopping {tool_name}: {e}')
                try:
                    self.processes[tool_name].kill()
                except Exception:
                    pass
            finally:
                self.processes[tool_name] = None
                self.tool_buttons[tool_name].config(text='▶ START')
                self.tool_status_labels[tool_name].config(text='⚫ Idle',
                                                          foreground='#666666')

    def monitor_tool(self, tool_name):
        process = self.processes[tool_name]
        if process is None:
            return
        try:
            process.wait()
            if self.processes[tool_name] is not None:
                self.log(f'ℹ️ {tool_name} ended')
                self.processes[tool_name] = None
                self.root.after(0, lambda: self.tool_buttons[tool_name].config(text='▶ START'))
                self.root.after(0, lambda: self.tool_status_labels[tool_name].config(
                    text='⚫ Idle', foreground='#666666'))
        except Exception:
            pass

    # ──────────────────────────────────────
    # STATUS / LOGS
    # ──────────────────────────────────────
    def update_status(self):
        running_count = sum(1 for p in self.processes.values() if p is not None)
        if running_count == 0:
            self.status_label.config(text='🟢 Ready - No tools running',
                                     foreground='#00AA00')
        elif running_count == 1:
            self.status_label.config(text='🟡 Active - 1 tool running',
                                     foreground='#FF8800')
        else:
            self.status_label.config(text=f'🟠 Active - {running_count} tools running',
                                     foreground='#FF0000')
        self.root.after(1000, self.update_status)

    def log(self, message):
        self.log_text.config(state=tk.NORMAL)
        self.log_text.insert(tk.END, message + '\n')
        self.log_text.see(tk.END)
        self.log_text.config(state=tk.DISABLED)

    def clear_logs(self):
        self.log_text.config(state=tk.NORMAL)
        self.log_text.delete(1.0, tk.END)
        self.log_text.config(state=tk.DISABLED)
        self.log(f'[{self.get_time()}] Logs cleared')

    def export_logs(self):
        try:
            filename = os.path.join(
                self.base_dir,
                f"automation_logs_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt"
            )
            with open(filename, 'w', encoding='utf-8') as f:
                f.write(self.log_text.get(1.0, tk.END))
            self.log(f'✓ Logs exported to {filename}')
            messagebox.showinfo('Success', f'Logs exported to:\n{filename}')
        except Exception as e:
            messagebox.showerror('Export Error', f'Failed to export logs:\n{e}')

    def get_time(self):
        return datetime.now().strftime('%H:%M:%S')

    def on_closing(self):
        running = [name for name, proc in self.processes.items() if proc is not None]
        if running:
            if messagebox.askyesno('Confirm',
                                   f'Stop running tools?\n{", ".join(running)}'):
                for tool_name in running:
                    self.stop_tool(tool_name)
        self.root.destroy()


# =========================
# MAIN
# =========================
if __name__ == '__main__':
    root = tk.Tk()
    try:
        root.iconbitmap(default='')
    except Exception:
        pass
    app = AutomationLauncher(root)
    root.protocol('WM_DELETE_WINDOW', app.on_closing)
    root.mainloop()