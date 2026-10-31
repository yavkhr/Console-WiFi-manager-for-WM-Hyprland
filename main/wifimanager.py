
import curses
import locale

from interface import App


def main():
    try:
        locale.setlocale(locale.LC_ALL, "")
        curses.wrapper(lambda stdscr: App(stdscr).run())
    except KeyboardInterrupt:
        pass


if __name__ == "__main__":
    main()
