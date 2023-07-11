#!/bin/env python
from math import trunc, ceil
from sys import argv, stdin
from hashlib import md5
import yaml
import os
import curses
import signal
import re


class main_window:
    # SUMS of both left and right margins
    MARGINS_X = 4
    MARGINS_Y = 8

    def __init__(self):
        # COLS and LINES count from 1, height and width count from 1
        self.height = curses.LINES - main_window.MARGINS_Y if curses.LINES > 40 else curses.LINES - 4
        self.input_raw = self.__get_raw_input()
        self.hash = md5("".join(self.input_raw).encode("UTF-8")).hexdigest()
        self.output_lines = self.__get_output_lines()
        self.longest_line_len = len(max(self.output_lines, key=len)) or 80
        # The number of pages that fit on the screen
        self.page_count = self.__get_page_count()
        self.width = (self.longest_line_len + 1) * self.page_count + 3
        self.start_x = trunc((curses.COLS - self.longest_line_len * self.page_count - 4) / 2)
        self.start_y = trunc(main_window.MARGINS_Y / 2) if curses.LINES > 40 else 2
        # The actual pages with text. len() them for actual page count
        self.pages = self.__fill_pages()
        self.current_page = 0
        del self.output_lines
        self.__create_window()

    def resize(self):
        self.height = curses.LINES - main_window.MARGINS_Y if curses.LINES > 40 else curses.LINES - 4
        self.output_lines = self.__get_output_lines()
        self.longest_line_len = len(max(self.output_lines, key=len)) or 80
        self.page_count = self.__get_page_count()
        self.width = (self.longest_line_len + 1) * self.page_count + 3
        self.start_x = trunc((curses.COLS - self.longest_line_len * self.page_count - 4) / 2)
        self.start_y = trunc(main_window.MARGINS_Y / 2) if curses.LINES > 40 else 2
        self.pages = self.__fill_pages()
        del self.output_lines
        self.__create_window()

    def __get_raw_input(self):
        # How are you going to resize if you keep it inside of the class?
        if (len(argv) > 1) and not (os.path.exists(argv[1])):
            curses.endwin()
            print(f'File {argv[1]} not found')
            exit()
        if (len(argv) > 1):
            with open(argv[1]) as file:
                return file.readlines()
        if not (os.isatty(0)):
            return stdin.readlines()
        else:
            print("What happened here?")

    def __fill_pages(self):
        pages = list()
        page_len_rows = self.height - 2
        text_pages_count = ceil(len(self.output_lines) / (self.height - 2))
        for i in range(0, text_pages_count):
            pages.append(self.output_lines[i * page_len_rows: i * page_len_rows + page_len_rows])
        return pages

    def __get_output_lines(self):
        raw_data = list()
        max_len_available = curses.COLS - main_window.MARGINS_X - 4
        for line in self.input_raw:
            line_st = line.rstrip()
            if (len(line_st) > max_len_available):
                for i in range(0, len(line_st) - 1, max_len_available):
                    raw_data.append(line_st[i:i + max_len_available])
                continue
            raw_data.append(line_st)
        return raw_data

    def __get_page_count(self):
        if (self.longest_line_len == 0):
            return 1
        term_pages_count = trunc((curses.COLS - main_window.MARGINS_X / 2) / self.longest_line_len)
        text_pages_count = ceil(len(self.output_lines) / (self.height - 2))  # 2 - borders
        if (term_pages_count <= 0):
            term_pages_count = 1
        if (text_pages_count > term_pages_count):
            return term_pages_count
        return text_pages_count

    def __create_window(self):
        self.window = curses.newwin(self.height, self.width, self.start_y, self.start_x)
        self.window.bkgd(" ", curses.color_pair(2))
        self.__draw_window_content()

    def __draw_window_content(self):
        self.window.erase()
        self.window.border()
        cursor_y = 1
        cursor_x = 2
        for page in self.pages[self.current_page: self.current_page + self.page_count]:
            for line in page:
                self.window.addstr(cursor_y, cursor_x, line)
                cursor_y += 1
            cursor_x += self.longest_line_len + 1
            cursor_y = 1
        self.window.refresh()

    def page_up(self):
        if (self.current_page == 0):
            return
        self.current_page -= self.page_count
        self.__draw_window_content()

    def page_down(self):
        if (self.current_page >= len(self.pages) - self.page_count):
            return
        self.current_page += self.page_count
        self.__draw_window_content()

    def get_current_page(self):
        # Pages are expected to be counted from 1
        return self.current_page + 1

    def get_text_page_count(self):
        return len(self.pages)

    def go_to_page(self, page_num):
        self.current_page = page_num - 1
        if (self.current_page < 0):
            self.current_page = 0
        elif (self.current_page > len(self.pages) - 1):
            self.current_page = len(self.pages) - 1
        self.__draw_window_content()

    def get_current_line(self):
        return self.current_page * (self.height - 2)

    def go_to_line(self, line_num):
        self.current_page = trunc(line_num / (self.height - 2))
        self.__draw_window_content()

    def get_last_page(self):
        return len(self.pages)


class bar:
    def __init__(self, page_count, current_page):
        self.width = curses.COLS
        self.height = 1
        self.start_x = 0
        self.start_y = curses.LINES - 1
        self.filename = argv[1] if len(argv) > 1 else "stdin"
        self.current_page = current_page
        self.page_count = page_count
        self.bar_visible = True
        self.__create_window()

    def __create_window(self):
        self.window = curses.newwin(self.height, self.width, self.start_y, self.start_x)
        self.window.bkgd(" ", curses.color_pair(2))
        self.__draw_window_content()

    def __draw_window_content(self):
        self.window.deleteln()
        if (not self.bar_visible):
            self.window.bkgd(" ", curses.color_pair(1))
            self.window.refresh()
            return
        progress_str = f'{ceil(self.current_page / self.page_count * 100)}% [{self.current_page}/{self.page_count}]'
        self.window.bkgd(" ", curses.color_pair(2))
        if (len(self.filename) + len(progress_str) > curses.COLS):
            filename = self.filename[0:curses.COLS - len(progress_str) - 3 - 1 - 1].strip() + "..."
        else:
            filename = self.filename
        self.window.addstr(0, 1, filename)
        self.window.addstr(0, self.width - len(progress_str) - 1, progress_str)
        self.window.refresh()

    def update_bar(self, current_page):
        self.current_page = current_page
        self.__draw_window_content()

    def toggle_bar(self):
        self.bar_visible = not self.bar_visible
        self.__draw_window_content()


def main(scr):
    def save_and_exit(signal, frame):
        hist_yaml[window.hash]["line"] = window.get_current_line()
        with open(f'{os.environ["HOME"]}/.local/share/curtxt-reader/history', "w") as file:
            file.write(yaml.dump(hist_yaml))
        exit()
    curses.init_pair(1, curses.COLOR_WHITE, curses.COLOR_BLUE)
    curses.init_pair(2, curses.COLOR_BLACK, curses.COLOR_WHITE)
    curses.init_pair(3, curses.COLOR_WHITE, curses.COLOR_BLACK)
    curses.curs_set(0)
    hist_yaml = get_history()
    scr.bkgd(" ", curses.color_pair(1))
    scr.refresh()
    window = main_window()
    if (window.hash in hist_yaml):
        window.go_to_line(hist_yaml[window.hash]["line"])
    else:
        hist_yaml[window.hash] = {"line": 0}
    bar_win = bar(window.get_text_page_count(), window.get_current_page())
    term = open("/dev/tty")
    os.dup2(term.fileno(), 0)
    signal.signal(signal.SIGINT, save_and_exit)
    while True:
        char = scr.getkey()
        match char:
            case "KEY_DOWN":
                window.page_down()
                bar_win.update_bar(window.get_current_page())
            case "KEY_UP":
                window.page_up()
                bar_win.update_bar(window.get_current_page())
            case "Q" | "q":
                hist_yaml[window.hash]["line"] = window.get_current_line()
                with open(f'{os.environ["HOME"]}/.local/share/curtxt-reader/history', "w") as file:
                    file.write(yaml.dump(hist_yaml))
                exit()
            case "B" | "b":
                bar_win.toggle_bar()
            case "KEY_HOME":
                window.go_to_line(0)
                bar_win.update_bar(window.get_current_page())
            case "KEY_END":
                window.go_to_page(window.get_last_page())
                bar_win.update_bar(window.get_current_page())
            case "KEY_RESIZE":
                if (curses.is_term_resized(curses.LINES, curses.COLS)):
                    y, x = scr.getmaxyx()
                    curses.resizeterm(y, x)
                    scr.clear()
                    scr.refresh()
                    window.resize()
                    del bar_win
                    bar_win = bar(window.get_text_page_count(), window.get_current_page())
            case _:
                if (re.match(r"\d+", char)):
                    page_num = [char]
                    while (not char.lower() == "g"):
                        char = scr.getkey()
                        if (re.match(r"\d+", char)):
                            page_num.append(char)
                        elif (char.lower() == "g"):
                            window.go_to_page(int("".join(page_num)))
                            bar_win.update_bar(window.get_current_page())
        scr.refresh()


def get_history():
    path = f'{os.environ["HOME"]}/.local/share/curtxt-reader'
    histfile_path = f'{path}/history'
    if (not os.path.exists(path)):
        os.mkdir(path)
    if (os.path.isfile(histfile_path)):
        return yaml.load(open(histfile_path).read(), yaml.SafeLoader) or {}
    open(histfile_path, "x").close()
    return {}


def init():
    help_text = """Curses txt reader
Usage:
    command | curtxt
    curtxt file
Options:
    -h, --help - pring this message and exit
    -v, --version - print version number and exit
    -c, --clear - clear history file"""
    if os.isatty(0) and (len(argv) == 1):
        print(help_text)
        exit()
    match argv[1]:
        case "--version" | "-v":
            print("Version 1.1.2")
            exit()
        case "--help" | "-h":
            print(help_text)
            exit()
        case "--clear" | "-c":
            path = f'{os.environ["HOME"]}/.local/share/curtxt-reader/history'
            if (os.path.exists(path)):
                os.remove(path)
                print("Cleared history")
            exit()
    curses.wrapper(main)


if __name__ == "__main__":
    init()
