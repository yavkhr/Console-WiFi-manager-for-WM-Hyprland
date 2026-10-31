# Console Wi-Fi Manager for Hyprland

A simple terminal-based Wi-Fi manager written in Python using `curses` and NetworkManager.

### Features
- Scan available Wi-Fi networks
- Connect and disconnect
- Save Wi-Fi passwords
- 5 built-in color themes
- Keyboard navigation (`↑` / `↓`, `j` / `k`)

### Requirements
- Linux
- NetworkManager (`nmcli`)
- Python 3

### Installation

```bash
git clone https://github.com/yavkhr/Console-WiFi-manager-for-WM-Hyprland.git
cd Console-WiFi-manager-for-WM-Hyprland
python3 main/wifimanager.py
```

### Controls

| Key | Action |
|---|---|
| `↑` / `↓` | Navigate |
| `j` / `k` | Navigate |
| `Enter` | Select |
| `Esc` | Back / Exit |
| `q` | Quit |

### Note

Saved Wi-Fi passwords are stored in `customization/.env` using Base64 encoding. This is not encryption.
