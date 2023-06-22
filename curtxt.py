#!/bin/env python
from math import trunc, ceil
from fileinput import input as f_input
from sys import argv
import os
import curses


class main_window:
    MARGIN_X = 4
    MARGIN_Y = 8

    def __init__(self):
        self.height = curses.LINES - main_window.MARGIN_Y
        self.output_raw = self.__get_raw_output()
        self.longest_line_len = len(max(self.output_raw, key=len)) or 80
        self.page_count = self.__get_page_count()
        self.width = (self.longest_line_len + 1) * self.page_count + 3
        self.start_x = trunc((curses.COLS - self.longest_line_len * self.page_count) / 2)
        self.start_y = trunc(main_window.MARGIN_Y / 2)
        self.pages = self.__fill_pages()
        self.current_page = 0
        self.__create_window()

    def __fill_pages(self):
        pages = list()
        page_len_rows = self.height - 2
        text_pages_count = ceil(len(self.output_raw) / (self.height - 2))
        for i in range(0, text_pages_count):
            pages.append(self.output_raw[i * page_len_rows: i * page_len_rows + page_len_rows])
        return pages

    def __get_raw_output(self):
        raw_data = list()
        max_len_available = curses.COLS - main_window.MARGIN_X * 2 - 2
        try:
            for line in f_input():
                line_st = line.rstrip()
                if (len(line_st) > max_len_available):
                    raw_data.append(line_st[0:max_len_available])
                    raw_data.append(line_st[max_len_available + 1: len(line_st)])
                    continue
                raw_data.append(line_st)
        except FileNotFoundError:
            curses.endwin()
            print(f'File {argv[1]} not found')
            exit()
        if (len(raw_data) == 0):
            exit()
        return raw_data

    def __get_page_count(self):
        try:
            term_pages_count = trunc(
                (curses.COLS - main_window.MARGIN_X / 2) / self.longest_line_len)
        except ZeroDivisionError:
            term_pages_count = 1
        text_pages_count = ceil(len(self.output_raw) / (self.height - 2))  # 2 - borders
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
        return self.current_page

    def get_text_page_count(self):
        return len(self.pages)


class bar:
    def __init__(self, page_count):
        self.width = curses.COLS
        self.height = 1
        self.start_x = 0
        self.start_y = curses.LINES - 1
        self.filename = argv[1] if len(argv) > 1 else "stdin"
        self.current_page = 1
        self.page_count = page_count
        self.bar_visible = True
        self.__create_window()

    def __create_window(self):
        self.window = curses.newwin(self.height, self.width, self.start_y, self.start_x)
        self.window.bkgd(" ", curses.color_pair(2))
        self.__draw_window_content()

    def __draw_window_content(self):
        if (not self.bar_visible):
            self.window.bkgd(" ", curses.color_pair(1))
            self.window.deleteln()
            self.window.refresh()
            return
        progress_str = f'{ceil(self.current_page / self.page_count * 100)}% [{self.current_page}/{self.page_count}]'
        self.window.bkgd(" ", curses.color_pair(2))
        self.window.addstr(0, 1, self.filename)
        self.window.addstr(0, self.width - len(progress_str) - 1, progress_str)
        self.window.refresh()

    def update_bar(self, current_page):
        self.current_page = current_page + 1
        self.__draw_window_content()

    def toggle_bar(self):
        self.bar_visible = not self.bar_visible
        self.__draw_window_content()


def main(scr):
    if os.isatty(0) and (len(argv) == 1):
        exit()
    curses.init_pair(1, curses.COLOR_WHITE, curses.COLOR_BLUE)
    curses.init_pair(2, curses.COLOR_BLACK, curses.COLOR_WHITE)
    curses.init_pair(3, curses.COLOR_WHITE, curses.COLOR_BLACK)
    curses.curs_set(0)
    scr.bkgd(" ", curses.color_pair(1))
    scr.refresh()
    window = main_window()
    bar_win = bar(window.get_text_page_count())
    term = open("/dev/tty")
    os.dup2(term.fileno(), 0)
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
                exit()
            case "B" | "b":
                bar_win.toggle_bar()
        scr.refresh()


curses.wrapper(main)
