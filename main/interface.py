import curses
import time

import config
import save_passwords
import wifi
from config import PALETTE_KEYS, THEMES

PAIR_PREVIEW_BASE = 13

HELP = " ↑/↓ или j/k — навигация   Enter — выбрать   q — выход "
HELP_THEMES = " ↑/↓ или j/k — навигация   Enter — применить   Esc — назад "


def safe_add(scr, y, x, s, attr=0):
    h, w = scr.getmaxyx()
    if y < 0 or y >= h or x >= w - 1:
        return
    n = min(len(s), w - 1 - x)
    if n > 0:
        try:
            scr.addnstr(y, x, s[:n], n, attr)
        except curses.error:
            pass


class App:
    def __init__(self, stdscr):
        self.stdscr = stdscr
        self.dev = wifi.wifi_device()
        self.nets = []
        self.current = None
        self.items = []
        self.theme_items = []
        self.sel = 0
        self.theme_sel = 0
        self.offset = 0
        self.status = ""
        self.error = ""
        self.progress = ""
        self.screen = "wifi"
        self.theme_idx = config.load_theme_idx()
        self.hascolor = False
        self.advices = True

        if self.dev:
            self.reload()

    def apply_theme(self):
        if not self.hascolor:
            return
        theme = THEMES[self.theme_idx]
        for i, key in enumerate(PALETTE_KEYS, start=1):
            try:
                curses.init_pair(i, theme[key], -1)
            except curses.error:
                pass
        for i, t in enumerate(THEMES, start=PAIR_PREVIEW_BASE):
            try:
                curses.init_pair(i, t["title"], -1)
            except curses.error:
                pass

    def cattr(self, key, extra=0):
        pair = PALETTE_KEYS.index(key) + 1
        a = curses.color_pair(pair) if self.hascolor else 0
        return a | extra

    def reload(self):
        self.nets = wifi.scan(self.dev)
        cur_ssid = wifi.active_ssid(self.dev)
        self.current = self._find(cur_ssid)

        self.items = []
        if self.current:
            self.items.append(("cur", self.current))
            self.items.append(("sep", None))
        for n in self.nets:
            if n is not self.current:
                self.items.append(("net", n))
        self.items.append(("sep", None))
        self.items.append(("nav", "Change theme"))
        self.items.append(("toggle", None))

        self.sel = min(self.sel, max(0, len(self.items) - 1))
        self.skip_sep()

    def build_theme_menu(self):
        self.theme_items = [("theme", i) for i in range(len(THEMES))]
        self.theme_items.append(("sep", None))
        self.theme_items.append(("nav", "Назад"))

    def _find(self, ssid):
        if ssid:
            for n in self.nets:
                if n["ssid"] == ssid:
                    n["in_use"] = True
                    return n
        return next((n for n in self.nets if n["in_use"]), None)

    @property
    def selected(self):
        return self.items[self.sel] if self.items else (None, None)

    def move(self, delta):
        items = self.theme_items if self.screen == "themes" else self.items
        if not items:
            return
        sel = self.theme_sel if self.screen == "themes" else self.sel
        idx = sel
        while True:
            idx += delta
            if idx < 0 or idx >= len(items):
                return
            if items[idx][0] != "sep":
                break
        if self.screen == "themes":
            self.theme_sel = idx
        else:
            self.sel = idx

    def skip_sep(self):
        if self.items and self.items[self.sel][0] == "sep":
            self.move(1 if self.sel + 1 < len(self.items) else -1)

    def read_key(self):
        ch = self.stdscr.getch()
        if 0x80 <= ch < 0x100:
            bs = bytes([ch])
            for _ in range(3):
                nxt = self.stdscr.getch()
                if nxt == curses.ERR:
                    return curses.ERR
                bs += bytes([nxt])
                try:
                    return ord(bs.decode("utf-8"))
                except UnicodeDecodeError:
                    continue
            return curses.ERR
        return ch

    def _top_area(self, scr, h, w):
        head = "Wifi Manager by "
        safe_add(scr, 0, 2, head, self.cattr("title", curses.A_BOLD))
        safe_add(scr, 0, 2 + len(head), "odept",
                 self.cattr("muted", curses.A_BOLD | curses.A_DIM))
        row = 2
        if self.error:
            safe_add(scr, row, 2, self.error,
                     self.cattr("error", curses.A_BOLD))
            row += 1
        elif self.progress:
            safe_add(scr, row, 2, self.progress, self.cattr("status"))
            row += 1
        return row

    def draw_menu(self, status=None):
        scr = self.stdscr
        scr.erase()
        h, w = scr.getmaxyx()
        top = self._top_area(scr, h, w)

        self.status = status if status is not None else self.status
        if self.status:
            safe_add(scr, h - 2, 2, self.status,
                     self.cattr("status", curses.A_DIM))
        if self.advices:
            help_text = HELP_THEMES if self.screen == "themes" else HELP
            safe_add(scr, h - 1, 2, help_text, curses.A_REVERSE)

        bottom = h - 3
        visible = max(1, bottom - top + 1)

        if self.screen == "wifi":
            self._draw_wifi_list(scr, top, h, w, visible)
        else:
            self._draw_themes(scr, top, h, w, visible)

        scr.refresh()

    def _draw_wifi_list(self, scr, top, h, w, visible):
        items, sel = self.items, self.sel
        if sel >= len(items):
            sel = 0
        if sel < self.offset:
            self.offset = sel
        elif sel >= self.offset + visible:
            self.offset = sel - visible + 1
        self.offset = max(0, min(self.offset, max(0, len(items) - visible)))

        for row, idx in enumerate(range(self.offset, len(items))):
            if row >= visible:
                break
            kind, data = items[idx]
            y = top + row
            if kind == "sep":
                safe_add(scr, y, 0, "─" * w, self.cattr("sep", curses.A_DIM))
                continue
            chosen = idx == sel
            cursor = "▸" if chosen else " "
            if kind == "cur":
                marker = "[✓]"
                sec = data["sec"] or "откр."
                name = data["ssid"]
                marker_attr = self.cattr("cur", curses.A_BOLD)
                name_attr = self.cattr("ssid", curses.A_BOLD)
            elif kind == "nav":
                marker = "[0]"
                sec = ""
                name = data
                marker_attr = self.cattr("menu", curses.A_DIM)
                name_attr = self.cattr("menu", curses.A_DIM)
            elif kind == "toggle":
                marker = "[✓]" if self.advices else "[✗]"
                sec = ""
                name = "Hide advices" if self.advices else "Show advices"
                marker_attr = self.cattr("bracket", curses.A_DIM)
                name_attr = self.cattr("bracket", curses.A_DIM)
            else:
                marker = "[ ]"
                sec = data["sec"] or "откр."
                name = data["ssid"]
                marker_attr = self.cattr("bracket", curses.A_DIM)
                name_attr = self.cattr("ssid", curses.A_BOLD if chosen else 0)
            sec_x = 7 + min(len(name), max(0, w - 9))
            sec = "  " + sec if sec else ""

            safe_add(scr, y, 0, cursor,
                     self.cattr("cursor", curses.A_BOLD) if chosen
                     else self.cattr("sec", curses.A_DIM))
            safe_add(scr, y, 2, marker, marker_attr)
            safe_add(scr, y, 7, name, name_attr)
            if sec:
                safe_add(scr, y, sec_x, sec, self.cattr("sec", curses.A_DIM))

    def _draw_themes(self, scr, top, h, w, visible):
        items, sel = self.theme_items, self.theme_sel
        sel = min(sel, len(items) - 1)
        self.theme_sel = sel

        safe_add(scr, top - 1, 2, "Change Theme Menu",
                 self.cattr("menu", curses.A_BOLD))
        line_y = top
        safe_add(scr, line_y, 0, "─" * w, self.cattr("sep"))

        start = line_y + 1
        for row, (kind, data) in enumerate(items):
            y = start + row
            if y >= h - 2:
                break
            if kind == "sep":
                safe_add(scr, y, 0, "─" * w, self.cattr("sep"))
                continue
            chosen = row == sel
            cursor = "▸" if chosen else " "
            if kind == "theme":
                active = data == self.theme_idx
                marker = "[✓]" if active else "[ ]"
                name = THEMES[data]["name"]
                name_pair = PAIR_PREVIEW_BASE + data
                name_attr = (curses.color_pair(name_pair)
                             if self.hascolor else 0)
            else:
                marker = "[ ]"
                name = data
                name_attr = self.cattr("sec")
            safe_add(scr, y, 0, cursor,
                     self.cattr("cursor", curses.A_BOLD) if chosen
                     else self.cattr("sec"))
            safe_add(scr, y, 2, marker, name_attr)
            safe_add(scr, y, 7, name, name_attr)

    def prompt_password(self, ssid):
        scr = self.stdscr
        password = ""
        curses.curs_set(1)
        try:
            while True:
                scr.erase()
                h, w = scr.getmaxyx()
                safe_add(scr, 0, 0, ssid, curses.A_BOLD)
                safe_add(scr, 1, 0, "=" * len(ssid), curses.A_BOLD)
                safe_add(scr, 3, 0, "Введите пароль: " + "•" * len(password))
                x = min(16 + len(password), w - 1)
                try:
                    scr.move(3, x)
                except curses.error:
                    pass
                safe_add(scr, h - 1, 2, " Enter — подключить   Esc — отмена ",
                         curses.A_REVERSE)
                scr.refresh()

                ch = self.read_key()
                if ch in (10, 13):
                    return password
                if ch == 27:
                    return None
                if ch in (curses.KEY_BACKSPACE, 127, 8):
                    password = password[:-1]
                elif ch in (curses.KEY_RESIZE,):
                    continue
                elif ch >= 32 and ch < 0x110000:
                    password += chr(ch)
        finally:
            curses.curs_set(0)

    def _try_connect(self, net, password):
        self.progress = f"Подключение к «{net['ssid']}»…"
        self.draw_menu()
        rc, _, err = wifi.connect(net["ssid"], password)
        self.progress = ""
        return rc

    def _connected(self, net):
        self.status = f"Подключено к «{net['ssid']}»"
        self.error = ""
        self.reload()

    def _restore_previous(self, prev_profile):
        if prev_profile:
            self.progress = "Восстановление прежней сети…"
            self.draw_menu()
            wifi.nmcli("connection", "up", prev_profile, timeout=30)
            self.progress = ""

    def act_connect(self, net):
        prev_profile = wifi.active_profile(self.dev)
        rc = None

        if net["sec"]:
            saved = save_passwords.get_saved_password(net["ssid"])
            if saved is not None:
                rc = self._try_connect(net, saved)
                if rc == 0:
                    self._connected(net)
                    return
                save_passwords.forget_password(net["ssid"])

            pw = self.prompt_password(net["ssid"])
            if pw is None:
                if rc is not None:
                    self._restore_previous(prev_profile)
                return
            rc = self._try_connect(net, pw)
            if rc == 0:
                save_passwords.save_password(net["ssid"], pw)
        else:
            rc = self._try_connect(net, None)

        if rc == 0:
            self._connected(net)
            return

        self._restore_previous(prev_profile)
        self.error = ("Неправильный пароль" if net["sec"]
                      else "Не удалось подключиться")
        self.status = ""
        self.reload()

    def act_disconnect(self, net):
        self.progress = f"Отключение от «{net['ssid']}»…"
        self.draw_menu()
        if wifi.disconnect(self.dev) == 0:
            self.status = f"Отключено от «{net['ssid']}»"
            self.error = ""
        else:
            self.status = "Не удалось отключиться"
        self.progress = ""
        self.reload()

    def act_theme_choice(self):
        kind, data = self.theme_items[self.theme_sel]
        if kind == "theme":
            self.theme_idx = data
            self.apply_theme()
            config.save_theme_idx(data)
            self.status = f"Тема: {THEMES[data]['name']}"
            self.error = ""
        else:
            self.screen = "wifi"
            self.status = ""

    def handle_key(self, key):
        if key in (ord("q"), ord("Q")):
            return "quit"

        if self.screen == "themes" and key == 27:
            self.screen = "wifi"
            self.status = ""
            return None
        if key == 27 and self.screen == "wifi":
            return "quit"

        if key in (ord("j"), ord("о"), curses.KEY_DOWN):
            self.move(1)
        elif key in (ord("k"), ord("л"), curses.KEY_UP):
            self.move(-1)
        elif key in (10, 13, curses.KEY_ENTER):
            if self.screen == "wifi":
                kind, data = self.selected
                if kind == "net":
                    self.act_connect(data)
                elif kind == "cur":
                    self.act_disconnect(data)
                elif kind == "nav":
                    self.build_theme_menu()
                    self.theme_sel = self.theme_idx
                    self.screen = "themes"
                elif kind == "toggle":
                    self.advices = not self.advices
                    self.status = ""
            else:
                self.act_theme_choice()
        return None

    def run(self):
        scr = self.stdscr
        scr.keypad(True)
        curses.curs_set(0)
        curses.noecho()

        self.hascolor = curses.has_colors()
        if self.hascolor:
            curses.start_color()
            curses.use_default_colors()
        self.apply_theme()

        if not self.dev:
            scr.erase()
            safe_add(scr, 0, 0, "Wi-Fi адаптер не найден.")
            safe_add(scr, 1, 0, "Нажмите любую клавишу для выхода.")
            scr.refresh()
            scr.getch()
            return

        wifi.rescan(self.dev)
        self.draw_menu()

        scr.timeout(500)
        last_scan = time.time()
        while True:
            key = self.read_key()
            if key == curses.ERR:
                if time.time() - last_scan >= 10:
                    last_scan = time.time()
                    wifi.rescan(self.dev)
                    self.reload()
                    self.draw_menu()
                continue
            if self.handle_key(key) == "quit":
                return
            self.draw_menu()
