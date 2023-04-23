# type: ignore
import curses
from dataclasses import dataclass, field
import json
from math import exp
from typing import Dict, Tuple
from display import Display, Result, Next
from keybindings import KeyConfig


def set_colors():
    C_OFF = 50
    
    curses.init_pair(1,  curses.COLOR_BLUE,   curses.COLOR_BLACK)
    curses.init_pair(2,  curses.COLOR_GREEN,  curses.COLOR_BLACK)
    curses.init_pair(3,  curses.COLOR_RED,    curses.COLOR_BLACK)
    curses.init_pair(4,  curses.COLOR_YELLOW, curses.COLOR_BLACK)
    curses.init_pair(20, curses.COLOR_BLACK,  curses.COLOR_WHITE)

    if curses.can_change_color():
        curses.init_color(C_OFF    , 500, 340,  42)  # brown
        curses.init_color(C_OFF + 1,   0, 666, 595)  # teal
        curses.init_color(C_OFF + 2, 964, 671, 472)  # tan
        curses.init_color(C_OFF + 3, 600,   0, 570)  # purple
        curses.init_color(C_OFF + 4, 400, 400, 400)  # gray

        curses.init_pair(5,  C_OFF    , curses.COLOR_BLACK)
        curses.init_pair(6,  C_OFF + 1, curses.COLOR_BLACK)
        curses.init_pair(7,  C_OFF + 2, curses.COLOR_BLACK)
        curses.init_pair(8,  C_OFF + 3, curses.COLOR_BLACK)
        curses.init_pair(21, C_OFF + 4, curses.COLOR_BLACK)

    else:
        curses.init_pair(5, curses.COLOR_MAGENTA, curses.COLOR_BLACK)
        curses.init_pair(6, curses.COLOR_MAGENTA, curses.COLOR_BLACK)
        curses.init_pair(7, curses.COLOR_MAGENTA, curses.COLOR_BLACK)
        curses.init_pair(8, curses.COLOR_MAGENTA, curses.COLOR_BLACK)
        curses.init_pair(21,  curses.COLOR_WHITE, curses.COLOR_BLACK)


class Minesweeper():
    """Attributes:
    term_win: the window object for the entire terminal (stdscr)
    term_h/term_w: the size of the terminal window in char units
    data_fp: file path to the data file
    data: the dict from the data file
    """
    def __init__(self, stdscr, data_fp="data.json"):
        stdscr.clear()
        stdscr.leaveok(True)
        curses.curs_set(0)
        curses.mousemask(curses.BUTTON1_CLICKED | curses.BUTTON3_CLICKED)
        set_colors()

        self.term_win = stdscr
        self.term_h, self.term_w = stdscr.getmaxyx()  # char units

        if self.term_h < 7 or self.term_w < 20:  # absolute minimum terminal size
            raise RuntimeError(f"terminal is too small: {self.term_h} x {self.term_w}. Minimum is 7 x 20")
        
        self.data_fp = data_fp
        with open(self.data_fp, "r") as f:
            self.data = json.load(f)

        self.keys = KeyConfig(self.data["controls"])

        self.main_menu()

    def main_menu(self):
        opt = MainMenu(
            self.term_win,
            (self.term_h, self.term_w), 
            self.data["presets"],
            self.keys
        ).run()
        
        # TODO: 4-6, each additional screen
        if opt == 0:
            todo, (height, width, n_bombs) = CustomGame(
                self.term_win,
                (self.term_h, self.term_w),
                self.data["presets"],
                self.keys
            ).run()

            if todo == Next.REPLAY:
                self.data["presets"][0] = [height, width, n_bombs]
                with open(self.data_fp, "w") as f:
                    json.dump(self.data, f)
                
                self.run_game(0, (height, width), n_bombs)

            elif todo == Next.MENU:
                self.main_menu()

        elif 1 <= opt <= 3:
            self.run_game(
                opt,
                tuple(self.data["presets"][opt][:2]), 
                self.data["presets"][opt][2]
            )
        
        elif opt == 4:
            KeybindingMenu(self.term_win, (self.term_h, self.term_w), self.data_fp).run()

    @classmethod
    def draw_border(self, win, ymin, ymax, xmin, xmax):
        win.hline(ymin, xmin + 1, curses.ACS_HLINE, xmax - xmin - 1)
        win.hline(ymax, xmin + 1, curses.ACS_HLINE, xmax - xmin - 1)
        win.vline(ymin + 1, xmin, curses.ACS_VLINE, ymax - ymin - 1)
        win.vline(ymin + 1, xmax, curses.ACS_VLINE, ymax - ymin - 1)

        win.addch(ymin, xmin, curses.ACS_ULCORNER)
        win.addch(ymin, xmax, curses.ACS_URCORNER)
        win.addch(ymax, xmin, curses.ACS_LLCORNER)
        win.addch(ymax, xmax, curses.ACS_LRCORNER)

    def run_game(self, opt, shape, n_bombs):
        info = Display(self.term_win, shape, n_bombs, self.keys).play()

        # TODO: more stats (like avg time, fastest time, streaks, etc.)
        if info.result != Result.QUIT and not info.cheats_used:  # save the result to the file
            self.data["statistics"]["total_games_played"] += 1
            if 1 <= opt <= 3:
                self.data["statistics"][f"pre{opt}_games_played"] += 1

            if info.result == Result.WIN:
                self.data["statistics"]["total_wins"] += 1
                if 1 <= opt <= 3:
                    self.data["statistics"][f"pre{opt}_wins"] += 1
            else:
                self.data["statistics"]["total_losses"] += 1
                if 1 <= opt <= 3:
                    self.data["statistics"][f"pre{opt}_losses"] += 1

            #print(info.time)  # TODO: incorporate into stats

            with open(self.data_fp, "w") as f:
                json.dump(self.data, f)

        if info.todo == Next.MENU:
            self.main_menu()
        elif info.todo == Next.REPLAY:
            self.run_game(opt, shape, n_bombs)


class MainMenu():
    def __init__(self, win, shape, presets, keys):
        self.win = win
        self.term_h, self.term_w = shape
        self.presets = presets
        self.keys = keys

    def run(self) -> int:
        menu_options = (  # each option has its string and its draw location
            ["New Custom Game", [-1, -1]],
            [f"{self.presets[1][1]}x{self.presets[1][0]}, {self.presets[1][2]} Bombs", [-1, -1]],
            [f"{self.presets[2][1]}x{self.presets[2][0]}, {self.presets[2][2]} Bombs", [-1, -1]],
            [f"{self.presets[3][1]}x{self.presets[3][0]}, {self.presets[3][2]} Bombs", [-1, -1]],
            ["Keybindings", [-1, -1]],
            ["Statistics", [-1, -1]],
            ["Settings", [-1, -1]]
        )

        selected = 0
        while True:
            ## Draw menu and options
            self.win.clear()

            if self.term_h < 9 or self.term_w < 21:  # smallest layout option
                # note: here we always start at row 0; if the screen was large enough for
                # that to put us off-center, we'd be using the larger layout option
                for i, line in enumerate(menu_options):
                    start_x = (self.term_w - len(line[0])) // 2
                    menu_options[i][1] = [i, start_x]
                    self.win.addstr(
                        i,
                        start_x,
                        line[0], 
                        curses.A_STANDOUT if i == selected else 0
                    )
                    
            elif self.term_h < 15 or self.term_w < 45:  # middle layout option
                start_y = (self.term_h - 7) // 2
                bbox_x = (self.term_w - 19) // 2

                Minesweeper.draw_border(self.win, start_y - 1, start_y + 7, bbox_x - 1, bbox_x + 19)

                # draw menu options
                for i, line in enumerate(menu_options):
                    start_x = (self.term_w - len(line[0])) // 2
                    menu_options[i][1] = [i + start_y, start_x]
                    self.win.addstr(
                        i + start_y,
                        start_x,
                        line[0],
                        curses.A_STANDOUT if i == selected else 0
                    )

            else:  # largest layout option
                Minesweeper.draw_border(self.win, 1, self.term_h - 2, 4, self.term_w - 5)  # 4 char buffer on sides, 1 char on top/bottom

                start_y = (self.term_h - 9) // 2
                Minesweeper.draw_border(self.win, start_y - 2, start_y + 10, (self.term_w - 27) // 2, (self.term_w - 27) // 2 + 27)

                # draw menu options
                for i, line in enumerate(menu_options):
                    if i == selected:
                        start_y += 1
                    
                    if i == selected + 1:
                        start_y += 1

                    start_x = (self.term_w - len(line[0])) // 2
                    menu_options[i][1] = [i + start_y, start_x]
                    self.win.addstr(
                        i + start_y,
                        start_x,
                        line[0],
                        curses.A_UNDERLINE | curses.A_BOLD if i == selected else 0
                    )

            ## Get user input
            ch = self.win.getkey()

            if ch == self.keys.EXIT_MENU or ch == self.keys.QUIT:
                return -1

            elif ch == self.keys.CONFIRM:
                return selected

            elif len(ch) == 1 and ord('1') <= ord(ch) <= ord('7'):
                return int(ch) - 1
            
            elif ch == self.keys.UP or ch == self.keys.BOARD_UP:
                selected = (selected - 1) % 7

            elif ch == self.keys.DOWN or ch == self.keys.BOARD_DOWN:
                selected = (selected + 1) % 7

            elif ch == "KEY_MOUSE":
                _, click_x, click_y, _, click_type = curses.getmouse()
                if click_type != curses.BUTTON1_CLICKED:
                    continue

                for i in range(7):
                    text_y = menu_options[i][1][0]
                    text_xmin = menu_options[i][1][1]
                    text_xmax = text_xmin + len(menu_options[i][0])
                    if click_y == text_y and text_xmin <= click_x <= text_xmax:
                        return i


class CustomGame():  # TODO: allow left click
    def __init__(self, win, term_shape, presets, keys):
        self.win = win
        self.term_h, self.term_w = term_shape
        self.presets = presets
        self.keys = keys
    
    def run(self) -> Tuple[Next, Tuple[int, int, int]]:
        height, width, n_bombs = self.presets[0]
        cursor = 0
        # The draw locations for editable portions of the display
        edit_locs = {
            "height":     [-1, -1],
            "width":      [-1, -1],
            "n_bombs":    [-1, -1],
            "density":    [-1, -1],
            "difficulty": [-1, -1],
            "start":      [-1, -1],
            "invalid":    [-1, -1]
        }

        ## Draw base (so only numbers need to be re-drawn in a loop)
        self.win.clear()

        if self.term_h < 13 or self.term_w < 43:  # small display option
            start_y = (self.term_h >= 9)
            lines = (
                MenuLine(0, "Custom Game"),
                MenuLine(1, "Width:   xxxx", {"width": 9}),
                MenuLine(2, "Height:  xxxx", {"height": 9}),
                MenuLine(3, "Bombs:   xxxx", {"n_bombs": 9}),
                MenuLine(4, "Bomb Density:  xx.x %", {"density": 15}),
                MenuLine(5, "Difficulty: x.x / 10", {"difficulty": 12}),
                MenuLine(6, "Invalid settings", {"start": 3, "invalid": 0})
            )
            
        else:  # large display option
            start_y = (self.term_h - 11) // 2
            start_x = (self.term_w - 43) // 2
            Minesweeper.draw_border(self.win, start_y - 1, start_y + 11, start_x - 1, start_x + 43)

            lines = (
                MenuLine(1, "Custom Game"),
                MenuLine(3, "Width: xxxx     Height: xxxx", {"width": 7, "height": 24}),
                MenuLine(4, "Number of Bombs:  xxxx", {"n_bombs": 18}),
                MenuLine(6, "Bomb density:  xx.x %", {"density": 15}),
                MenuLine(7, "Approximate difficulty:  x.x / 10", {"difficulty": 25}),
                MenuLine(9, "Invalid settings", {"start": 3, "invalid": 0})
            )

        # Draw the constant portion of the menu
        for line in lines:
            start_x = (self.term_w - len(line.text)) // 2

            for id, offset in line.editable.items():
                if id in edit_locs.keys():
                    edit_locs[id] = [start_y + line.row, start_x + offset]

            self.win.addstr(
                start_y + line.row,
                start_x,
                line.text
            )
            
        cursor = 0
        while True:
            # Check for validity
            valid = not (height == 0 or width == 0 or n_bombs >= (width*height - 1))

            # Width, height, n_bombs:
            for i, id, val in zip(
                    range(3),
                    ("width", "height", "n_bombs"),
                    (width, height, n_bombs)
                ):
                if cursor == i:
                    self.win.addstr(*edit_locs[id], ' '*(4 - len(str(val))))
                    self.win.addstr(str(val), curses.A_STANDOUT)
                else:
                    self.win.addstr(*edit_locs[id], f"{val:4d}")

            if valid:
                self.win.addstr(*edit_locs["density"], f"{100*n_bombs/(width*height):4.1f}")
                self.win.addstr(*edit_locs["difficulty"], f"{self.difficulty_func(width*height, n_bombs):3.1f}")

                # clear bkgd (no highlight), then print "Start Game"
                self.win.addstr(*edit_locs["invalid"], ' '*len("Invalid settings"), 0)
                self.win.addstr(*edit_locs["start"], "Start Game", curses.A_STANDOUT if cursor == 3 else 0)

            else:
                self.win.addstr(*edit_locs["density"], " N/A")
                self.win.addstr(*edit_locs["difficulty"], "N/A")
                self.win.addstr(*edit_locs["invalid"], "Invalid settings", curses.A_STANDOUT if cursor == 3 else 0)                

            self.win.refresh()

            ## Get user input
            ch = self.win.getkey()

            if ch == self.keys.EXIT_MENU:
                return (Next.MENU, (-1, -1, -1))
            elif ch == self.keys.QUIT:
                return (Next.EXIT, (-1, -1, -1))
            elif ch == self.keys.CONFIRM and valid:  # save the settings and start the game
                return (Next.REPLAY, (height, width, n_bombs))
            elif ch in (self.keys.DOWN, self.keys.RIGHT, self.keys.BOARD_DOWN, self.keys.BOARD_RIGHT):
                cursor = (cursor + 1) % 4
            elif ch in (self.keys.UP, self.keys.LEFT, self.keys.BOARD_UP, self.keys.BOARD_LEFT):
                cursor = (cursor - 1) % 4
            elif len(ch) == 1 and ord('0') <= ord(ch) <= ord('9'):
                if cursor == 0 and width < 100:
                    width = 10*width + int(ch)
                elif cursor == 1 and height < 100:
                    height = 10*height + int(ch)
                elif n_bombs < 100:
                    n_bombs = 10*n_bombs + int(ch)
            elif ch == self.keys.DELETE:
                if cursor == 0:
                    width //= 10
                elif cursor == 1:
                    height //= 10
                else:
                    n_bombs //= 10

    @staticmethod
    def difficulty_func(size, n_bombs):
        density = n_bombs / size
        p1 = 1 / (1 + exp(-0.0055*size + 1.5))
        
        if density < 0.062:
            p2 = 0
        elif density > 0.25:
            p2 = 1
        else: 
            p2 = 5.31915 * density - 0.32979
        
        return p1 + 9 * p2


class KeybindingMenu():
    def __init__(self, win, term_shape, data_fp):
        self.win = win
        self.term_h, self.term_w = term_shape
        self.compact = (self.term_w < 44)
        
        self.data_fp = data_fp
        with open(self.data_fp, "r") as f:
            self.key_dict = json.load(f)["controls"]

    def run(self) -> None:        
        # Create the lines
        index = 0
        lines = list()
        for cat_name, category in self.key_dict.items():
            if index != 0:
                index += 2*(self.compact)  # gap between categories
            lines.append(MenuLine(index, cat_name))
            index += 1

            for id, (key, descrip) in category.items():
                if self.compact:
                    index += 1
                    lines.append(MenuLine(index, descrip))
                    index += 1
                    lines.append(MenuLine(index, '"' + key + '"', {id: 0}))
                else:
                    n_sp = (38 - len(descrip) - 8 - len(key)) // 2  # minumum of 6 spaces, plus 2 uncounted quote chars
                    lines.append(MenuLine(
                        index, 
                        descrip + ' '*n_sp + '"' + key + '"',
                        {id: len(descrip) + 6}  # where the editable portion starts: after space for descrip, plus 6 spaces
                    ))
                index += 1

        first_row = 0
        cursor = 0

        while True:
            ## Draw window
            if self.compact:  # small option
                pass

            else:  # large option
                pass

            ## Get user input


@dataclass
class MenuLine():
    row: int
    text: str
    # each entry in editable is a portion on the line that can be modified
    # the key is its 'ID', e.g. "height"; the key is its x-offset from the start of the row
    editable: Dict[str, int] = field(default_factory=dict)


if __name__ == "__main__":
    curses.wrapper(Minesweeper)
