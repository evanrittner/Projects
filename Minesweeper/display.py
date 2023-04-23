# type: ignore
import curses
import _curses
from dataclasses import dataclass
from enum import IntEnum
import time
from typing import Tuple
from game import Game, Tile
from keybindings import KeyConfig


class Result(IntEnum):
    WIN = 1
    QUIT = 0
    LOSS = -1
    RESUME = 2

class Next(IntEnum):
    MENU = 0
    EXIT = 1
    REPLAY = 2

@dataclass
class GameInfo:
    result: Result
    todo: Next = Next.MENU
    cheats_used: bool = True
    time: int = -1


class Display:
    """Attributes:
    game: the Game object currently being displayed/played
    board_r/board_c: the size of the game board (not just the displayed portion) in tile units
    term_h/term_w: the size of the terminal window in char units
    cursor: (r, c) of the cursor on the board (tile units)
    show_cursor: bool, whether or not the cursor is shown
    show_reduced: bool, whether to display the board in reduced mode or normal mode
    view_r/view_c: the size of the view/display window, in tile units
    view_h/view_w: the size of the view/display window, in char units
    disp_r/disp_c: the first row/col of the board displayed in the view window, in tile units
    view_y/view_x: the coordinate on stdscr of the top-left corner of the view/display window, in char units
    term_win: the window object for the entire terminal screen (stdscr)
    view_win: the window object for the view/display portion of the screen
    start_t: time at the start of the game (seconds since unix epoch)
    cheats_used: whether the cheat functionality was used during the game
    n_bombs: the total number of bombs (constant)
    stop_t: time when game was paused/stopped, or -1 if the game hasn't been stopped yet
    keys: the KeyConfig object dictating keybindings
    """
    def __init__(self, stdscr, board_shape: Tuple[int, int], n_bombs: int, keys: KeyConfig):
        ## Board, shape, view sizes and positions
        self.term_win = stdscr
        self.term_win.clear()

        self.board_r, self.board_c = board_shape  # tile units
        self.term_h, self.term_w = stdscr.getmaxyx()  # char units

        self.cursor = [board_shape[0] // 2, board_shape[1] // 2]
        self.show_cursor = True
        self.show_reduced = False
        self.cheats_used = False

        self.n_bombs = n_bombs

        if self.term_h < 7 or self.term_w < 20:  # absolute minimum terminal size
            raise RuntimeError(f"terminal is too small: {self.term_h} x {self.term_w}. Minimum is 7 x 20")

        self.start_t = int(time.time())
        self.stop_t = -1
        
        self.keys = keys

        ## View sizing and positioning
        # can the game board fit entirely within the terminal?
        if (self.board_r <= self.term_h - 4) and (self.board_c <= (self.term_w - 3) // 2):
            self.view_r = self.board_r
            self.view_c = self.board_c
            self.disp_r = 0
            self.disp_c = 0

        else:  # it can't; we can only show a subset
            # is the terminal large enough to add a border?
            if self.term_h >= 20 and self.term_w >= 75:  # arbitrary thresholds
                self.view_r = min(self.term_h - 6, self.board_r)
                self.view_c = min((self.term_w - 7) // 2, self.board_c)
            else:
                self.view_r = min(self.term_h - 4, self.board_r)
                self.view_c = min((self.term_w - 3) // 2, self.board_c)
            
            # center around the cursor
            self.disp_r = min(max(self.cursor[0] - self.view_r//2, 0), self.board_r - self.view_r)
            self.disp_c = min(max(self.cursor[1] - self.view_c//2, 0), self.board_c - self.view_c)

        self.view_h = self.view_r          # r and c are tile units;
        self.view_w = 2 * self.view_c + 1  # h and w are char units

        self.view_y = (self.term_h - self.view_h) // 2
        self.view_x = (self.term_w - self.view_w) // 2

        self.view_win = self.term_win.subwin(self.view_h, self.view_w, self.view_y, self.view_x)        

    def play(self) -> GameInfo:
        """Run the main game loop; return GameInfo containing win/loss/quit,
        what to do now, other stats and info
        """
        cont, pre_flagged = self.get_first_click(self.n_bombs)
        if not cont:
            return GameInfo(Result.QUIT, Next.MENU, False, 0)
            
        self.game = Game((self.board_r, self.board_c), self.n_bombs, self.cursor)

        for tile in pre_flagged:
            self.game.flag(tile)

        return self.game_loop()

    def draw_game_text(self, time=0, bomb_count=0):
        self.term_win.addstr(
            self.view_y - 2,
            self.view_x,
            f"{time // 60: 2}:{time % 60:02}"
        )
        if hasattr(self, "game"):
            self.term_win.addstr(
                self.view_y - 2,
                self.view_x + self.view_w - len(str(self.game.total_bombs)),
                str(bomb_count).rjust(len(str(self.game.total_bombs)))
            )
        else:
            self.term_win.addstr(
                self.view_y - 2,
                self.view_x + self.view_w - len(str(bomb_count)),
                str(bomb_count)
            )
        self.term_win.addstr(
            self.view_y + self.view_h + 1,
            self.view_x,
            "Help: h"
        )
        self.term_win.addstr(
            self.view_y + self.view_h + 1,
            self.view_x + self.view_w - 7,
            "Exit: x"
        )
        self.term_win.refresh()

    def draw_game_border(self, top=True, left=True, bottom=True, right=True):
        # top edge
        self.term_win.addstr(
            self.view_y - 1,
            self.view_x,
            ('─'*self.view_w) if top else ("╴╶"*(self.view_w // 2) + '╴'*(self.view_w % 2))
        )

        # sides
        for i in range(self.view_h):
            self.term_win.addch(
                self.view_y + i,
                self.view_x - 1,
                '│' if left else '╷'
            )
            self.term_win.addch(
                self.view_y + i,
                self.view_x + self.view_w,
                '│' if right else '╷'
            )
        
        # bottom
        self.term_win.addstr(
            self.view_y + self.view_h,
            self.view_x,
            ('─'*self.view_w) if bottom else ("╴╶"*(self.view_w // 2) + '╴'*(self.view_w % 2))
        )

        # corners
        self.term_win.addch(self.view_y - 1,           self.view_x - 1,           '┌')
        self.term_win.addch(self.view_y - 1,           self.view_x + self.view_w, '┐')
        self.term_win.addch(self.view_y + self.view_h, self.view_x - 1,           '└')
        self.term_win.addch(self.view_y + self.view_h, self.view_x + self.view_w, '┘')

        self.term_win.refresh()

    def draw_board(self, reveal=False):
        """reveal: display bombs at the end of the game"""
        if self.show_reduced and not reveal:
            reduced = self.game.reduce()
        
        for r in range(self.disp_r, self.disp_r + self.view_r):
            for c in range(self.disp_c, self.disp_c + self.view_c):
                attr = 0

                if self.show_reduced and not reveal:
                    if reduced[r, c] == Tile.INACTIVE:
                        ch = ' '
                    elif reduced[r, c] == Tile.HIDDEN:
                        ch = '.'
                    else:
                        ch = str(reduced[r, c])
                        if reduced[r, c] == 0:
                            attr = curses.color_pair(21)
                        elif reduced[r, c] < 0:
                            ch = '?'
                            attr = curses.color_pair(3)
                        else:
                            attr = curses.color_pair(reduced[r, c])

                else:  # normal, non-reduced mode
                    if self.game.disp[r, c] == Tile.HIDDEN:
                        if reveal and self.game.board[r, c] == Tile.BOMB:
                            ch = '\u2b24' #'\u2737'
                        else:
                            ch = '.'

                    elif self.game.disp[r, c] == Tile.FLAGGED:
                        ch = '\u2691'
                        if reveal and not self.game.board[r, c] == Tile.BOMB:
                            attr = curses.color_pair(3)

                    else:  # revealed
                        if self.game.board[r, c] == Tile.BOMB:
                            ch = '\u2b24' #'\u2737'
                            attr = curses.color_pair(3)
                        elif self.game.board[r, c] == Tile.EMPTY:
                            ch = ' '
                        else:
                            ch = f'{self.game.board[r, c]}'
                            attr = curses.color_pair(self.game.board[r, c])
                
                if (r, c) == tuple(self.cursor) and self.show_cursor and not reveal:
                    attr = curses.color_pair(20)

                self.view_win.addch(r - self.disp_r, 2*(c - self.disp_c)+1, ch, attr)
        self.view_win.refresh()

    def move(self, ch):
        if ch == self.keys.UP:
            if self.cursor[0] > self.disp_r:  # move the cursor up
                self.cursor[0] -= 1
                self.show_cursor = True

            elif self.disp_r > 0:        # move the view window up
                self.cursor[0] -= 1
                self.disp_r -= 1
                self.show_cursor = True
        
        elif ch == self.keys.LEFT:
            if self.cursor[1] > self.disp_c:  # cursor left
                self.cursor[1] -= 1
                self.show_cursor = True

            elif self.disp_c > 0:        # view window left
                self.cursor[1] -= 1
                self.disp_c -= 1
                self.show_cursor = True

        elif ch == self.keys.DOWN:
            if self.cursor[0] < self.disp_r + self.view_r - 1:   # cursor down
                self.cursor[0] += 1
                self.show_cursor = True

            elif self.disp_r + self.view_r < self.board_r:  # view window down
                self.cursor[0] += 1
                self.disp_r += 1
                self.show_cursor = True

        elif ch == self.keys.RIGHT:
            if self.cursor[1] < self.disp_c + self.view_c - 1:   # cursor right
                self.cursor[1] += 1
                self.show_cursor = True

            elif self.disp_c + self.view_c < self.board_c:  # view window right
                self.cursor[1] += 1
                self.disp_c += 1
                self.show_cursor = True

        # move the view, while keeping the cursor at the same place on the
        # board, unless it's on the edge of the view, then move it with the view
        elif ch == self.keys.BOARD_UP:
            if self.disp_r > 0:
                self.disp_r -= 1
                if self.cursor[0] >= self.disp_r + self.view_r:
                    self.cursor[0] -= 1

        elif ch == self.keys.BOARD_LEFT:
            if self.disp_c > 0:
                self.disp_c -= 1
                if self.cursor[1] >= self.disp_c + self.view_c:
                    self.cursor[1] -= 1

        elif ch == self.keys.BOARD_DOWN:
            if self.disp_r + self.view_r < self.board_r:
                self.disp_r += 1
                if self.cursor[0] < self.disp_r:
                    self.cursor[0] += 1

        elif ch == self.keys.BOARD_RIGHT:
            if self.disp_c + self.view_c < self.board_c:
                self.disp_c += 1
                if self.cursor[1] < self.disp_c:
                    self.cursor[1] += 1

    def get_first_click(self, n_bombs):
        # Draw a blank board
        # Allow the user to move around, flag, and reveal
        # Once the player clicks to reveal, we're done

        pre_flagged = list()  # tiles (in board coords) that were flagged before revealing anything
        
        curses.halfdelay(5)  # error after each sec w/o input to keep timer updated

        while True:
            self.draw_game_text(int(time.time() - self.start_t), n_bombs - len(pre_flagged))
            self.draw_game_border(
                self.disp_r == 0,  # is the top border solid?
                self.disp_c == 0,  # left border
                self.disp_r + self.view_r == self.board_r,  # bottom
                self.disp_c + self.view_c == self.board_c   # right
            )

            # draw the board
            for r in range(self.disp_r, self.disp_r + self.view_r):
                for c in range(self.disp_c, self.disp_c + self.view_c):
                    if (r, c) in pre_flagged:
                        ch = '\u2691'
                    else:
                        ch = '.'
                
                    if (r, c) == tuple(self.cursor) and self.show_cursor:
                        attr = curses.color_pair(20)
                    else:
                        attr = 0

                    self.view_win.addch(r - self.disp_r, 2*(c - self.disp_c)+1, ch, attr)
            self.view_win.refresh()

            # get input, but error after each sec to keep timer updated
            try:
                ch = self.term_win.getkey()
            except _curses.error:
                continue

            if ch == "KEY_MOUSE":
                _, click_x, click_y, _, click_type = curses.getmouse()

                self.cursor[0] = click_y - self.view_y
                self.cursor[1] = (click_x - self.view_x - 1) // 2

                if not (0 <= self.cursor[0] < self.view_r) or not (0 <= self.cursor[1] < self.view_c):
                    continue

                if click_type == curses.BUTTON1_CLICKED: # left click
                    self.show_cursor = False
                    return True, pre_flagged

                elif click_type == curses.BUTTON3_CLICKED: # right click
                    self.show_cursor = False
                    if tuple(self.cursor) in pre_flagged:
                        pre_flagged.remove(tuple(self.cursor))
                    else:
                        pre_flagged.append(tuple(self.cursor))

            elif ch == self.keys.EXIT_MENU:
                # turn off the error-if-no-input thing
                curses.nocbreak()
                curses.cbreak()
                return False, pre_flagged
            
            elif ch == self.keys.QUIT:
                # turn off the error-if-no-input thing
                curses.nocbreak()
                curses.cbreak()
                return False, pre_flagged

            elif ch == self.keys.FLAG:
                self.show_cursor = True
                if tuple(self.cursor) in pre_flagged:
                    pre_flagged.remove(tuple(self.cursor))

                else:
                    pre_flagged.append(tuple(self.cursor))

            elif ch == self.keys.REVEAL:
                self.show_cursor = True
                return True, pre_flagged
            
            else:  # try to use the general movement calls
                self.move(ch)

    def game_loop(self) -> GameInfo:
        while True:  # TODO: handle KEY_RESIZE or at least error out
            self.draw_game_text(int(time.time() - self.start_t), self.game.bombs_remaining)
            self.draw_game_border(
                self.disp_r == 0,  # is the top border solid?
                self.disp_c == 0,  # left border
                self.disp_r + self.view_r == self.board_r,  # bottom
                self.disp_c + self.view_c == self.board_c   # right
            )
            self.draw_board()

            if self.game.check_win():
                return self.end_game(False)

            # get input, but error after each sec to keep timer updated
            try:
                ch = self.term_win.getkey()
            except _curses.error:
                continue

            if ch == "KEY_MOUSE":
                _, click_x, click_y, _, click_type = curses.getmouse()

                self.cursor[0] = click_y - self.view_y
                self.cursor[1] = (click_x - self.view_x - 1) // 2

                if not (0 <= self.cursor[0] < self.view_r) or not (0 <= self.cursor[1] < self.view_c):
                    continue

                if click_type == curses.BUTTON1_CLICKED: # left click
                    self.show_cursor = False
                    if self.game.disp[tuple(self.cursor)] == Tile.REVEALED:  # try to quick reveal
                        if self.game.quick_reveal(self.cursor):
                            return self.end_game(loss=True)

                    elif self.game.reveal(self.cursor, bomb_check=False):  # otherwise, just regular reveal
                        return self.end_game(loss=True)

                elif click_type == curses.BUTTON3_CLICKED: # right click
                    self.show_cursor = False
                    self.game.flag(self.cursor)

            elif ch == self.keys.PAUSE:  # allow user to pause and resume
                info = self.end_game(loss=False)
                if info.result != Result.RESUME:
                    return info
            
            elif ch == self.keys.QUIT: # instant end-of game; no handling
                return GameInfo(
                    Result.QUIT,
                    Next.EXIT,
                    self.cheats_used, 
                    time.time() - self.start_t
                )

            elif ch == self.keys.FLAG:
                self.game.flag(self.cursor)
                self.show_cursor = True

            elif ch == self.keys.REVEAL:
                self.show_cursor = True
                if self.game.disp[tuple(self.cursor)] == Tile.HIDDEN:
                    if self.game.reveal(self.cursor, bomb_check=False):
                        return self.end_game(loss=True)
                elif self.game.disp[tuple(self.cursor)] == Tile.REVEALED:
                    if self.game.quick_reveal(self.cursor):
                        return self.end_game(loss=True)
            
            elif ch == self.keys.CHEAT_MILD:  # one set of moves only
                info = self.cheat(simple=True, once=True)
                if info.result != Result.RESUME:
                    return info
            
            elif ch == self.keys.CHEAT_SEVERE:  # automatically make as many moves as possible
                info = self.cheat(simple=True, once=False)
                if info.result != Result.RESUME:
                    return info
            
            elif ch == 'i':  # one set of hard solves
                info = self.cheat(simple=False, once=True)
                if info.result != Result.RESUME:
                    return info
            
            elif ch == 'u':  # hardcore solver
                info = self.cheat(simple=False, once=False)
                if info.result != Result.RESUME:
                    return info

            elif ch == self.keys.REDUCED:
                self.show_reduced = not self.show_reduced
            
            else:  # try to use the general movement calls
                self.move(ch)

    def cheat(self, simple, once) -> GameInfo:
        self.cheats_used = True
        self.show_cursor = True
        while True:
            if simple:
                moves = self.game.easy_moves()  # TODO: use the generator, don't move it into a set first
            else:
                moves = self.game.solve()
            # if not len(moves):
            #     break

            any_moves = False

            for m in moves:
                any_moves = True
                t1 = time.time()
                self.cursor[:] = m[0]
                if m[1] == Tile.REVEALED and self.game.disp[m[0]] == Tile.HIDDEN:
                    if self.game.reveal(m[0], bomb_check=False):
                        return self.end_game(loss=True)
                elif m[1] == Tile.FLAGGED and self.game.disp[m[0]] == Tile.HIDDEN:
                    self.game.flag(m[0])
                else:
                    continue

                # redraw between moves
                self.draw_game_text(int(time.time() - self.start_t), self.game.bombs_remaining)
                self.draw_game_border(
                    self.disp_r == 0,  # is the top border solid?
                    self.disp_c == 0,  # left border
                    self.disp_r + self.view_r == self.board_r,  # bottom
                    self.disp_c + self.view_c == self.board_c   # right
                )
                self.draw_board()

                curses.napms(max(0, int(50 - 1000*(time.time() - t1))))
            
            if not any_moves or once:
                break
        
        # reset cursor to a visible position
        self.cursor[0] = max(self.disp_r, min(self.disp_r + self.view_h - 1, self.cursor[0]))
        self.cursor[1] = max(self.disp_c, min(self.disp_c + self.view_w - 1, self.cursor[1]))
        
        return GameInfo(Result.RESUME)

    def end_game(self, loss) -> GameInfo:
        # turn off the error-if-no-input thing
        curses.nocbreak()
        curses.cbreak()

        self.term_win.addstr(  # TODO: revamp this
            self.view_y + self.view_h + 1,
            self.view_x,
            "Menu: m"
        )

        self.stop_t = time.time()
        stats = (  # can add more statistics here, instead of nine separate times below
            self.cheats_used,
            self.stop_t - self.start_t
        )

        if loss or self.game.check_win():
            result = Result.WIN if self.game.check_win() else Result.LOSS
            
            curses.beep()
            self.draw_board(reveal=True)

            while True:
                ch = self.term_win.getkey()
                if ch == self.keys.QUIT:
                    return GameInfo(result, Next.EXIT, *stats)
                elif ch == self.keys.RETURN_MENU:
                    return GameInfo(result, Next.MENU, *stats)
                elif ch == self.keys.NEW_GAME:
                    return GameInfo(result, Next.REPLAY, *stats)

        else:  # quit in the middle of the game
            while True:
                ch = self.term_win.getkey()
                if ch == self.keys.QUIT:
                    return GameInfo(Result.QUIT, Next.EXIT, *stats)
                elif ch == self.keys.RETURN_MENU:
                    return GameInfo(Result.QUIT, Next.MENU, *stats)
                elif ch == self.keys.NEW_GAME:
                    return GameInfo(Result.QUIT, Next.REPLAY, *stats)

                # two additional options: resume game and reveal bombs
                elif ch == self.keys.RESUME:
                    self.start_t += (time.time() - self.stop_t)
                    curses.halfdelay(5)  # resume the error-if no input thing
                    return GameInfo(Result.RESUME)
                
                elif ch == self.keys.REVEAL_BOARD:
                    self.draw_board(reveal=True)
                    return self.end_game(loss=True)


def main(stdscr, size=(16, 16), n_bombs=40):
    stdscr.clear()
    stdscr.leaveok(True)
    curses.curs_set(0)
    curses.mousemask(curses.BUTTON1_CLICKED | curses.BUTTON3_CLICKED)
    set_colors()

    Display(stdscr, size, n_bombs).play()


if __name__ == "__main__":
    from sys import argv
    from minesweeper import set_colors

    if len(argv) >= 4:
        size = (int(argv[1]), int(argv[2]))
        n_bombs = int(argv[3])
        curses.wrapper(main, size, n_bombs)
    else:
        curses.wrapper(main)
