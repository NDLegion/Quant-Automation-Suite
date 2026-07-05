# Changelog

All notable changes to Quant Automation Suite are documented here.

---

## [1.2] — 2026-07-05

### Added
- **Cursor Logger** tab built into Control Center
  - Floating tooltip near cursor with step-by-step instructions
  - One-click coordinate capture per point
  - Direct script patching — no manual file editing needed
  - ESC to cancel capture at any time
- **PyInstaller EXE support** — single `QuantAutomationSuite.exe`, no Python required
  - Scripts extracted to `_fwmo_scripts` folder next to EXE on first run
  - User coordinates preserved between updates
- Working directory now always resolves to launcher's own folder
  - Fixes "script not found" error when launching from different locations
- `build.bat` — one-click EXE builder with dependency check
- `build.spec` — PyInstaller spec with all scripts bundled as data files

### Changed
- Control Center tab layout: Cursor Logger added between Launcher and Configuration
- `start_tool()` now uses `cwd=base_dir` — scripts find their own resources correctly
- `export_logs()` saves to launcher folder instead of random working directory
- Status bar now shows current base directory path

### Fixed
- Script path resolution broken when launching via shortcut or from different folder
- `monitor_tool()` UI updates now use `root.after()` — no more threading crashes

---

## [1.1] — 2026-06-21

### Added
- MILK 6.13: dual-color trigger support (green `#7dc0aa` + yellow `#d8da6c`)
- MILK 6.13: semi-transparent always-on-top status overlay (ON / IDLE / OFF)
- Orange Picker: memory system — prevents re-picking same orange (2s / 100px tolerance)
- Orange Picker: STOP trigger via green pixel detection
- CARP v2.2: single screenshot per cycle for efficiency (~50 checks/sec)
- CARP v2.2: DEBUG flag for verbose logging

### Changed
- Orange Picker: memory check runs before cleanup to fix race condition
- MILK: config.json auto-created on first run with default coordinates

### Fixed
- Orange Picker: drag interrupted mid-move when script stopped
- CARP: popup detection now re-checks red condition before pressing key 1

---

## [1.0] — 2026-06-20

### Initial release

- Control Center launcher GUI
- MILK 6.13 — zone-based mini-game automation
- Orange Picker — HSV contour detection + drag
- CARP v2.2 — multi-point pixel monitoring
- CARP v1 — classic fishing automation
- Wood Clicker — E-button + click spam
- Cursor Logger — standalone coordinate utility
