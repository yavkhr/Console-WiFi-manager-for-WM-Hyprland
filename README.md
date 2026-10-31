# Console Wi-Fi Manager for Hyprland

<p align="center">
  A lightweight, keyboard-driven Wi-Fi manager for Linux desktops — built for terminal workflows and Hyprland setups.
</p>

<p align="center">
  <strong>Python</strong> · <strong>curses TUI</strong> · <strong>NetworkManager / nmcli</strong>
</p>

---

## Overview

**Console Wi-Fi Manager** is a terminal-based interface for discovering nearby wireless networks, connecting to them, and disconnecting from the current network — without leaving your keyboard.

It uses **NetworkManager's `nmcli`** command-line interface and Python's built-in `curses` module. The interface is designed to stay simple, fast, and comfortable to use in a tiling-window-manager environment such as **Hyprland**.

## Features

- **Network discovery** — lists available Wi-Fi networks and refreshes the scan automatically.
- **Connection status** — shows the currently connected network at the top of the list.
- **Connect and disconnect** — connect to secured or open networks, or disconnect from the active one.
- **Remembered passwords** — saves passwords locally so known networks can be reconnected without entering the password every time.
- **Theme selection** — includes five built-in color themes: Classic, Ocean, Neon, Sunset, and Forest.
- **Custom themes** — define your own colors in `customization/theme.json`.
- **Keyboard-first controls** — navigate the interface with arrow keys or Vim-style `j` / `k` keys.
- **No extra Python packages** — the application uses Python's standard library.

## Requirements

Make sure your system has:

- Linux with **NetworkManager** running.
- **`nmcli`** installed and available in your `PATH`.
- **Python 3**.
- A terminal with `curses` support and a Unicode-capable font.

> The application manages Wi-Fi through NetworkManager. It will not work with a wireless interface that is not managed by NetworkManager.

## Installation

Clone the repository:

```bash
git clone https://github.com/yavkhr/Console-WiFi-manager-for-WM-Hyprland.git
cd Console-WiFi-manager-for-WM-Hyprland
```

No third-party Python dependencies are required.

## Usage

Run the application from the repository root:

```bash
python3 main/wifimanager.py
```

The program detects a Wi-Fi device through NetworkManager and displays the available networks. If no Wi-Fi device is found, it displays a message and exits after a key press.

### Keyboard shortcuts

| Key | Action |
| --- | --- |
| `↑` / `↓` | Move through the list |
| `j` / `k` | Move down / up |
| `Enter` | Select a network or menu item |
| `Esc` | Go back from the theme menu; exit from the main screen |
| `q` | Quit |
| `Enter` (password prompt) | Submit the password |
| `Esc` (password prompt) | Cancel the connection attempt |

### Connecting to a network

1. Select a network from the list.
2. Press `Enter`.
3. For a secured network, enter its password and press `Enter`.
4. The manager saves the password locally after a successful connection.

Open networks can be selected directly. Select the currently connected network and press `Enter` to disconnect.

The network list is refreshed automatically while the application is idle (approximately every 10 seconds).

## Themes and customization

Select **Change theme** in the main menu to switch between the five built-in themes. Your selected theme is saved and restored on the next launch.

To create or edit themes, modify:

```text
customization/theme.json
```

The file contains a `themes` array. Each theme has a display `name` and color values for the interface elements:

| Key | Used for |
| --- | --- |
| `title` | Application title |
| `muted` | Secondary title text |
| `ssid` | Network names |
| `sec` | Security information |
| `cur` | Currently connected network |
| `bracket` | Network markers |
| `cursor` | Selected row indicator |
| `sep` | Separators |
| `menu` | Menu items |
| `help` | Help bar |
| `status` | Status messages |
| `error` | Error messages |

Supported color names are:

```text
black, red, green, yellow, blue, magenta, cyan, white
```

Example theme:

```json
{
  "themes": [
    {
      "name": "Midnight",
      "title": "cyan",
      "muted": "blue",
      "ssid": "white",
      "sec": "blue",
      "cur": "green",
      "bracket": "cyan",
      "cursor": "yellow",
      "sep": "blue",
      "menu": "cyan",
      "help": "white",
      "status": "green",
      "error": "red"
    }
  ]
}
```

Keep the same color-key structure when adding themes. Invalid color names fall back to white.

## Project structure

```text
.
├── customization/
│   └── theme.json          # Theme definitions
└── main/
    ├── config.py           # Theme and configuration loading
    ├── interface.py        # Curses-based user interface
    ├── save_passwords.py   # Local password storage
    ├── wifi.py             # NetworkManager / nmcli operations
    └── wifimanager.py      # Application entry point
```

## Security note

Saved Wi-Fi passwords are stored in `customization/.env`. The application Base64-encodes the SSID and password values and sets the file permissions to owner read/write (`0600`) where supported.

**Base64 is encoding, not encryption.** Anyone who can read this file can recover the saved passwords. Keep your user account secure and do not share or commit this file. The repository's `.gitignore` excludes `customization/.env`.

## Contributing

Contributions, bug reports, and suggestions are welcome.

1. Fork the repository.
2. Create a branch for your change.
3. Make and test your changes on a NetworkManager-based Linux system.
4. Open a pull request with a clear description.

## License

No license file is currently included in this repository. Until a license is added, the project should be treated as having **no explicit open-source reuse license**.

---

<p align="center">
  Made for keyboard-driven Linux workflows.
</p>
