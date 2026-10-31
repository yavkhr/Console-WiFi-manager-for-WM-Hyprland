import curses
import json
import os
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parents[1]
CUSTOMIZATION_DIR = BASE_DIR / "customization"
THEME_FILE = CUSTOMIZATION_DIR / "theme.json"
PASSWORD_FILE = CUSTOMIZATION_DIR / ".env"

COLOR_NAMES = {
    "black": curses.COLOR_BLACK,
    "red": curses.COLOR_RED,
    "green": curses.COLOR_GREEN,
    "yellow": curses.COLOR_YELLOW,
    "blue": curses.COLOR_BLUE,
    "magenta": curses.COLOR_MAGENTA,
    "cyan": curses.COLOR_CYAN,
    "white": curses.COLOR_WHITE,
}

PALETTE_KEYS = [
    "title", "muted", "ssid", "sec", "cur", "bracket",
    "cursor", "sep", "menu", "help", "status", "error",
]

DEFAULT_THEMES = [
    {
        "name": "Классика",
        "title": "white", "muted": "white", "ssid": "white", "sec": "white",
        "cur": "green", "bracket": "white", "cursor": "yellow",
        "sep": "white", "menu": "white", "help": "white",
        "status": "yellow", "error": "red",
    },
    {
        "name": "Океан",
        "title": "cyan", "muted": "cyan", "ssid": "blue", "sec": "cyan",
        "cur": "cyan", "bracket": "cyan", "cursor": "white",
        "sep": "cyan", "menu": "cyan", "help": "cyan",
        "status": "yellow", "error": "red",
    },
    {
        "name": "Неон",
        "title": "magenta", "muted": "magenta", "ssid": "white",
        "sec": "magenta", "cur": "green", "bracket": "magenta",
        "cursor": "yellow", "sep": "magenta", "menu": "green",
        "help": "magenta", "status": "green", "error": "red",
    },
    {
        "name": "Закат",
        "title": "yellow", "muted": "yellow", "ssid": "red", "sec": "yellow",
        "cur": "yellow", "bracket": "red", "cursor": "red",
        "sep": "red", "menu": "yellow", "help": "yellow",
        "status": "yellow", "error": "red",
    },
    {
        "name": "Лес",
        "title": "green", "muted": "green", "ssid": "green", "sec": "white",
        "cur": "yellow", "bracket": "green", "cursor": "green",
        "sep": "green", "menu": "green", "help": "green",
        "status": "green", "error": "red",
    },
]


def _parse_theme(raw):
    theme = {"name": str(raw.get("name") or "Без названия")}
    for key in PALETTE_KEYS:
        color = str(raw.get(key, "white")).strip().lower()
        theme[key] = COLOR_NAMES.get(color, curses.COLOR_WHITE)
    return theme


def _write_default_theme_file():
    data = {"themes": DEFAULT_THEMES}
    try:
        THEME_FILE.write_text(
            json.dumps(data, ensure_ascii=False, indent=2) + "\n",
            encoding="utf-8",
        )
    except OSError:
        pass


def load_themes():
    if not THEME_FILE.exists():
        _write_default_theme_file()
    try:
        data = json.loads(THEME_FILE.read_text(encoding="utf-8"))
        raw_themes = data.get("themes") if isinstance(data, dict) else data
        themes = [_parse_theme(t) for t in raw_themes if isinstance(t, dict)]
        if themes:
            return themes
    except (OSError, ValueError, TypeError):
        pass
    return [_parse_theme(t) for t in DEFAULT_THEMES]


THEMES = load_themes()


def load_theme_idx():
    try:
        for line in PASSWORD_FILE.read_text(encoding="utf-8").splitlines():
            if line.startswith("WIFI_THEME_INDEX="):
                idx = int(line.partition("=")[2].strip())
                if 0 <= idx < len(THEMES):
                    return idx
    except (OSError, ValueError):
        return 0
    return 0


def save_theme_idx(idx):
    try:
        lines = []
        if PASSWORD_FILE.exists():
            lines = PASSWORD_FILE.read_text(encoding="utf-8").splitlines()
        setting = f"WIFI_THEME_INDEX={idx}"
        for pos, line in enumerate(lines):
            if line.startswith("WIFI_THEME_INDEX="):
                lines[pos] = setting
                break
        else:
            lines.append(setting)
        PASSWORD_FILE.parent.mkdir(parents=True, exist_ok=True)
        PASSWORD_FILE.write_text("\n".join(lines) + "\n", encoding="utf-8")
        os.chmod(PASSWORD_FILE, 0o600)
    except OSError:
        pass
