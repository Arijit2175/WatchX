# 🚀 WatchX

## 🧠 Overview

WatchX provides a live, interactive view of your system’s performance directly in the terminal.
It combines system-level insights, process tracking, and a visually rich interface to deliver a developer-friendly monitoring experience.

---

## ✨ Features

### 📊 Real-Time System Monitoring
- Live CPU, memory, and disk usage with visual bars
- Per-core CPU usage breakdown
- Network totals and real-time up/down speed
- Disk I/O read/write statistics
- GPU utilization support (when GPUtil is available)
- Lightweight trend indicators for CPU and network activity

### 🧩 Advanced Process Management
- Interactive process table with PID, name, CPU %, and memory %
- Click or keyboard selection with stable PID tracking
- Process kill action directly from the UI
- Search processes by PID or name
- Sort processes by CPU, memory, name, or PID
- Pagination support for handling large process lists

### 🖥️ Modern Multi-Pane TUI
- Split layout with:
	- Main monitoring + process workspace
	- Dedicated selected-process details panel
- Focus switching between panes (table/details/search)
- Mouse + keyboard navigation support
- Responsive, non-blocking updates for smoother interaction

### 🧭 Launcher Command Shell
- Animated WatchX title landing screen
- Built-in command prompt interface (`watchx>`) with commands:
	- `start` / `run` / `monitor`
	- `help`
	- `health`
	- `about`
	- `clear`
	- `quit` / `exit`

### 🩺 Health & Alerts
- `health` command to check:
	- Python runtime details
	- Dependency availability
	- Terminal capability indicators
- CPU/MEM/DISK threshold-based alert line in monitor
- Optional audible alert toggle for warning transitions

### ⚡ Performance-Focused Design
- Async/background metric collection to avoid UI blocking
- Interaction-aware refresh throttling
- Cached process detail rendering
- Diff-based table redraw optimization to reduce flicker and overhead

---

## 🛠️ Tech Stack

- **Language:** Python 3
- **TUI Framework:** Textual
- **Terminal Rendering:** Rich
- **System Metrics:** psutil
- **GPU Metrics:** GPUtil
- **ASCII Title Rendering:** pyfiglet
- **Input Utilities:** pynput

---

## 🗂️ Project Structure

```
WatchX/
├── src/
│   ├── app.py
│   ├── bars.py
│   ├── dashboard.py
│   └── stats.py
├── tests/
│   └── test_bars.py
├── main.py
├── requirements.txt
├── .gitignore
└── README.md
```

---

## ⚙️ Functionality

WatchX works in two layers: a launcher shell and the monitoring TUI.

### 1) Launcher Flow
- Running `python main.py` opens the WatchX command shell.
- The shell accepts commands like `start`, `help`, `health`, `about`, `clear`, and `quit`.
- `start` launches the live monitor interface.

### 2) Live Metrics Pipeline
- WatchX gathers system stats using `psutil` (CPU, memory, disk, network, process data).
- GPU stats are collected via `GPUtil` when available.
- Metrics refresh asynchronously to keep the UI responsive.

### 3) Monitoring UI Behavior
- The top area displays system metrics with progress bars and trend indicators.
- The process table supports sorting, filtering, pagination, and row selection.
- A details panel shows rich information about the currently selected process.

### 4) Process Control
- You can select a process using keyboard or mouse.
- `k` sends a terminate signal to the selected PID.
- Selection tracking is PID-based so it remains stable while rows reorder.

### 5) Alerts & Feedback
- CPU, memory, and disk thresholds trigger visual warning states.
- Optional alert beep can be toggled for threshold transitions.
- Footer/status lines provide action feedback and navigation context.

---

## 👀 Preview

### Launcher Shell
![WatchX Launcher](./screenshots/launcher.png)

### Live Monitor Dashboard
![WatchX Dashboard](./screenshots/dashboard.png)

---


