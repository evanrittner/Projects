from enum import IntEnum
from itertools import product
import numpy as np
import random
from typing import Generator, Sequence, Tuple, Set, Literal, Optional

import pickle


class Tile(IntEnum):
    BOMB = -1
    EMPTY = 0
    HIDDEN = 10
    REVEALED = 20
    FLAGGED = 40
    INACTIVE = 80

coord = Sequence[int]
move = Tuple[coord, Literal[Tile.REVEALED, Tile.FLAGGED]]


def log(s):
    return
    with open("log.txt", "a") as f:
        f.write(s + '\n')


class Game:

    GEN_THRESH = int(1e4)
    MAX_SEARCH_DEPTH = 4

    def __init__(self, shape: coord, n_bombs: int, first: coord):
        # with open("seed.pkl", "wb") as f:
        #     pickle.dump(random.getstate(), f)
        # with open("seed.pkl", "rb") as f:
        #     random.setstate(pickle.load(f))
        
        shape = tuple(shape)
        first = tuple(first)

        # Input validation
        if len(shape) != 2:
            raise ValueError(
                f"shape parameter must be two-dimensional. invalid: {shape}"
            )
        
        if len(first) != 2:
            raise ValueError(
                f"first click parameter must be two-dimensional. invalid: {first}"
            )
        
        if (shape[0] <= 0) or (shape[1] <= 0):
            raise ValueError(
                f"board dimensions must be positive. invalid: {shape}"
            )

        if n_bombs >= shape[0] * shape[1]:
            raise ValueError(
                f"too many bombs; maximum number for board shape {shape} is {shape[0] * shape[1] - 1}"
            )

        if not (0 <= first[0] < shape[0] and 0 <= first[1] < shape[1]):
            raise ValueError(
                f"first click location {first} is not within board dimensions {shape}"
            )

        self.total_bombs = n_bombs
        self.bombs_remaining = n_bombs
        self.board = np.empty(shape=shape, dtype=int)
        self.disp = np.full_like(self.board, Tile.HIDDEN, dtype=int)

        # Generate bomb locations
        for _ in range(self.GEN_THRESH):  # try to find a 'vein'
            self.board[:, :] = Tile.EMPTY
            bomb_idx = random.sample(
                range(self.board.shape[0] * self.board.shape[1]), self.total_bombs
            )
            self.board.flat[bomb_idx] = Tile.BOMB

            # if none of the neighbors (or the start tile itself) are bombs
            if self.board[first] != Tile.BOMB and all(
                self.board[neighbor] != Tile.BOMB
                for neighbor in self.adj(first)
            ):
                break

        else:  # otherwise, just find a non-bomb
            for _ in range(self.GEN_THRESH):
                self.board[:, :] = Tile.EMPTY
                bomb_idx = random.sample(
                    range(self.board.shape[0] * self.board.shape[1]), self.total_bombs
                )
                self.board.flat[bomb_idx] = Tile.BOMB

                if self.board[first] != Tile.BOMB:
                    break
            else:
                raise RuntimeError(
                    f"unable to generate bomb layout with selected number of bombs ({self.total_bombs})"
                )

        # Number the tiles
        for tile in product(range(self.board.shape[0]), range(self.board.shape[1])):
            if self.board[tile] != Tile.BOMB:
                total = 0
                for neighbor in self.adj(tile):
                    if self.board[neighbor] == Tile.BOMB:
                        total += 1

                self.board[tile] = total

        # Reveal the tile selected
        self.reveal(first)

    def adj(self, loc: coord, board: Optional[np.ndarray] = None) -> Generator[Tuple[int, int], None, None]:
        neighbors = (
            (-1, -1),
            (-1, 0),
            (-1, 1),
            (0, -1),
            (0, 1),
            (1, -1),
            (1, 0),
            (1, 1),
        )

        if board is None:
            board = self.board
        
        for offset in neighbors:
            r = loc[0] + offset[0]
            c = loc[1] + offset[1]

            if (0 <= r < board.shape[0]) and (0 <= c < board.shape[1]):
                yield (r, c)

    def reveal(self, loc: coord, bomb_check: bool = True) -> bool:
        """Reveals a tile. Handles the 'vein' functionality. If bomb_check,
        throws an exception if a bomb is revealed. Otherwise, returns a boolean,
        whether or not a bomb is revealed"""
        
        assert len(loc) == 2
        if not (0 <= loc[0] < self.board.shape[0] and 0 <= loc[1] < self.board.shape[1]):
            raise ValueError(
                f"reveal location {loc} is not within board dimensions {self.board.shape}"
            )
        loc = tuple(loc)

        if self.disp[loc] != Tile.HIDDEN:
            return False

        if bomb_check and self.board[loc] == Tile.BOMB:
            raise RuntimeError(f"bomb unexpectedly revealed at loc {loc}")

        self.disp[loc] = Tile.REVEALED

        bomb_found = self.board[loc] == Tile.BOMB

        if self.board[loc] == Tile.EMPTY:
            to_reveal = [loc]

            # recursive vein functionality: reveal all non-revealed neighbors
            while len(to_reveal):
                loc = to_reveal.pop()

                self.disp[loc] = Tile.REVEALED
                bomb_found = bomb_found or self.board[loc] == Tile.BOMB

                if self.board[loc] == Tile.EMPTY:
                    for neighbor in self.adj(loc):
                        if (self.disp[neighbor] == Tile.HIDDEN and neighbor not in to_reveal):
                            to_reveal.insert(0, neighbor)

        return bomb_found

    def flag(self, loc: coord):
        assert len(loc) == 2
        if not (0 <= loc[0] < self.board.shape[0] and 0 <= loc[1] < self.board.shape[1]):
            raise ValueError(
                f"reveal location {loc} is not within board dimensions {self.board.shape}"
            )
        loc = tuple(loc)
        
        if self.disp[loc] == Tile.HIDDEN:
            self.disp[loc] = Tile.FLAGGED
            self.bombs_remaining -= 1

        elif self.disp[loc] == Tile.FLAGGED:
            self.disp[loc] = Tile.HIDDEN
            self.bombs_remaining += 1

    def quick_reveal(self, loc: coord) -> bool:
        """Call with a revealed tile loc. If the number of neighbors flagged
        matches the tile number, reveal all remaining hidden neighbors. Return
        whether or not a bomb was revealed"""
        
        assert len(loc) == 2
        if not (0 <= loc[0] < self.board.shape[0] and 0 <= loc[1] < self.board.shape[1]):
            raise ValueError(
                f"reveal location {loc} is not within board dimensions {self.board.shape}"
            )
        loc = tuple(loc)

        if self.disp[loc] != Tile.REVEALED:
            return False

        n_flags = 0
        for neighbor in self.adj(loc):
            if self.disp[neighbor] == Tile.FLAGGED:
                n_flags += 1

        loss = False
        if n_flags == self.board[loc]:
            for neighbor in self.adj(loc):
                if self.disp[neighbor] == Tile.HIDDEN:
                    loss = self.reveal(neighbor, False) or loss

        return loss

    def check_win(self, board: Optional[np.ndarray] = None, disp: Optional[np.ndarray] = None) -> bool:
        assert (board is None) == (disp is None), "if providing one of board or disp, must provide both"
        if board is None:
            board = self.board
        if disp is None:
            disp = self.disp
        
        # the player has won if all non-bomb tiles have been revealed
        for tile in product(range(board.shape[0]), range(board.shape[1])):
            if (board[tile] != Tile.BOMB) != (disp[tile] == Tile.REVEALED):
                return False
        return True

    def reduce(self, board: Optional[np.ndarray] = None, disp: Optional[np.ndarray] = None) -> np.ndarray:
        """Return a copy of the board array with:
          - all tiles outside of 'the strip' are INACTIVE
          - all flagged tiles in 'the strip' are INACTIVE
          - all revealed and numbered tiles are 'reduced'
        'The strip' is any revealed tile neighboring a hidden tile plus any
        hidden tile neighboring a revealed tile
        """
        assert (board is None) == (disp is None), "if providing one of board or disp, must provide both"
        if board is None:
            board = self.board
        if disp is None:
            disp = self.disp
        
        out = np.empty_like(board)

        for loc in product(range(board.shape[0]), range(board.shape[1])):
            if disp[loc] == Tile.FLAGGED:
                out[loc] = Tile.INACTIVE
            
            elif disp[loc] == Tile.REVEALED:
                bomb_count = 0
                make_inactive = True
                for neighbor in self.adj(loc, board):
                    if (disp[neighbor] == Tile.FLAGGED or (disp[neighbor] == Tile.REVEALED and board[loc] == Tile.BOMB)):
                        bomb_count += 1
                    elif disp[neighbor] == Tile.HIDDEN:
                        make_inactive = False

                if make_inactive:
                    out[loc] = Tile.INACTIVE
                else:
                    out[loc] = board[loc] - bomb_count
            
            else: # hidden
                for neighbor in self.adj(loc, board):
                    if disp[neighbor] == Tile.REVEALED:
                        out[loc] = Tile.HIDDEN
                        break
                else:
                    out[loc] = Tile.INACTIVE
        
        return out

    def easy_moves(self, reduced: Optional[np.ndarray] = None) -> Generator[move, None, None]:
        """Generator finding two types of 'trivial' moves: either there's a number tile
        with the number of hidden neighbors equal to its number (in which case,
        yield each neighbor); or second, there's a numbered tile with all the flags
        it needs, and all its hidden neighbors can be revealed"""

        if reduced is None:
            reduced = self.reduce()

        for loc in product(range(reduced.shape[0]), range(reduced.shape[1])):
            if reduced[loc] == 0:
                for neighbor in self.adj(loc, reduced):
                    if reduced[neighbor] == Tile.HIDDEN:
                        yield (neighbor, Tile.REVEALED)
            elif 1 <= reduced[loc] <= 8:
                hidden_neighbor_count = 0
                for neighbor in self.adj(loc, reduced):
                    if reduced[neighbor] == Tile.HIDDEN:
                        hidden_neighbor_count += 1
                
                if hidden_neighbor_count == reduced[loc]:
                    for neighbor in self.adj(loc, reduced):
                        if reduced[neighbor] == Tile.HIDDEN:
                            yield (neighbor, Tile.FLAGGED)

    def solve(self) -> Generator[move, None, None]:
        """
        1. Try to execute any simple moves
        2. Pick a hidden square (from the reduced board). Split into two branches, one where we assume it's a bomb, one where we assume it's clear
        3. For each branch, 'execute' simple moves until either:
            A: there's a contradiction, in which case this branch is wrong, and the other one is correct. Implement that branch's moves and start again
            B: a dead-end is reached. Continue this checklist
        4. Both branches have dead ends. First, see if any of the assumed moves agree (i.e. both say you can reveal a certain square). If so, execute that and start again
        5. Both branches have dead ends, and they don't agree on any moves. For each, begin this process again on step 2, except agreement to reveal/flag a square needs to be unanimous across all 4 branches, not just two like before
        6. At a certain depth (some number of assumptions / branching points), give up
        7. Try this all again, picking a different initial square to make an assumption about. However, don't pick any of the squares involved in any previous assumption paths of logic
        8. If all hidden tiles on the reduced board have been involved in assumptions, and none of those assumptions lead to conclusions, we're stuck
        """
        tries = 0
        involved = set()  # all the hidden tiles that have been involved in assumptions or their paths of logic

        while True:
            while True:
                simple_moves = set(self.easy_moves())
                if not len(simple_moves):
                    break
                
                for m in simple_moves:
                    yield m

            reduced = self.reduce()

            all_hidden = set()
            for loc in product(range(reduced.shape[0]), range(reduced.shape[1])):
                if reduced[loc] == Tile.HIDDEN:
                    all_hidden.add(loc)
            
            log(f"All hidden: {all_hidden}")

            if not len(all_hidden - involved):
                log("all tiles (supposedly) covered by assumptions")
                return  # go until there are no hidden tiles in reduced form; either the game's over or we need to guess

            assumption_coord = (all_hidden - involved).pop()
            log(f"assumption, top level: {assumption_coord}")

            branch1 = self._explore_branch(
                (assumption_coord, Tile.FLAGGED),
                reduced.copy(),
                all_hidden,
                set(),
                0,
                self.total_bombs - self.bombs_remaining
            )
            branch2 = self._explore_branch(
                (assumption_coord, Tile.REVEALED),
                reduced.copy(),
                all_hidden,
                set(),
                0,
                self.total_bombs - self.bombs_remaining
            )

            if not len(involved.intersection((branch1[1] & branch2[2]) | (branch1[1] & branch2[2]))):  # TODO: review logic here
                tries += 1
                if tries >= 50:
                    log("ran out of tries")
                    return  # last set of branching didn't do anything new
            else:
                tries = 0
            
            log(f"new involved: {((branch1[1] & branch2[2]) | (branch1[1] & branch2[2])) - involved}")
            involved.update((branch1[1] & branch2[2]) | (branch1[1] & branch2[2]))  # if a tile has been considered both flagged and cleared, no use in including it in a future assumption

            if branch1[0] and not branch2[0]:  # branch 1 has a contradiction but 2 doesn't; yield the moves from 2
                log("assumption must be clear\n")
                for m in branch2[1]:
                    yield (m, Tile.FLAGGED) 
                for m in branch2[2]:
                    yield (m, Tile.REVEALED)

            elif not branch1[0] and branch2[0]:  # branch 2 has a contradiction but 1 doesn't; yield the moves from 1
                log("assumption must be a bomb\n")
                for m in branch1[1]:
                    yield (m, Tile.FLAGGED) 
                for m in branch1[2]:
                    yield (m, Tile.REVEALED)
            
            else:  # both branches hit dead ends; yield the intersection of their moves
                log("both possibilities are dead ends\n")
                for m in (branch1[1] & branch2[1]):
                    yield (m, Tile.FLAGGED) 
                for m in (branch1[2] & branch2[2]):
                    yield (m, Tile.REVEALED)


    def _explore_branch(self, assumption: move, reduced: np.ndarray, all_hidden: Set[coord], involved: Set[coord], depth: int, n_bombs) -> Tuple[bool, Set[coord], Set[coord]]:
        """
        Arguments:
        - the current reduced board, with the assumption already implemented
        - the all_hidden set (read only)
        - the involved set (to be added to)

        Does:
        - 'implements' simple moves by performing them on an internal model of the board (i.e. the reduced board), and recording which tiles get flagged and cleared
        - after implementing each, check for contradictions. If found, return immediately
        - once there are no more simple moves to make (and no contradictions were found), pick a new assumption (TODO: how), and make two new recursive branches
        - if both branches return contradictions, this branch is also a contradiction; return immediately
        - if one is a contradiction and one is not, 'implement' all the moves from the one that is valid, and return that as a dead end
        - if both are just dead ends, look through the moves they made. implement any moves they agree on, and return
        - in any case, collect all the locations affected by either branch and mark them as affected in the overall set TODO: should this only be tiles affected in both branches?

        Returns: 
        - bool, whether or not a contradiction was encountered. If not, the other outcome is that a dead end was reached
        - two sets of moves: to_flag and to_clear
        """
        to_flag = set()
        to_clear = set()

        moves = {assumption}
            
        while len(moves):  # until there are no more easy moves (but no contradictions either); go spawn new branches
            # implement simple moves, and check for contradictions
            # three types of contradictions:
            # - tiles with too many bomb neighbors
            # - tiles with too few hidden neighbors to allow them sufficient bombs
            # - more bombs flagged on the board than the total bomb count
            for m in moves:
                reduced[m[0]] = Tile.INACTIVE
                if m[1] == Tile.FLAGGED:
                    # adjust the reduced count of neighbors, since this is a bomb (we're assuming)
                    for loc in self.adj(m[0], reduced):
                        if reduced[loc] == 0:
                            # CONTRADICTION: loc has too many bombs neighboring it
                            return (True, set(), set())
                        elif 0 < reduced[loc] <= 8:
                            reduced[loc] -= 1
                    
                    to_flag.add(m[0])
                else:
                    # no need to adjust neighbors since this tile is (assumed) clear
                    to_clear.add(m[0])
                
            # check for tiles with too few hidden neighbors
            for loc in product(range(reduced.shape[0]), range(reduced.shape[1])):
                if 0 < reduced[loc] <= 8:
                    hidden_neighbor_count = 0
                    for neighbor in self.adj(loc, reduced):
                        if reduced[neighbor] == Tile.HIDDEN:
                            hidden_neighbor_count += 1
                    
                    if hidden_neighbor_count < reduced[loc]:
                        # CONTRADICTION: loc has too few hidden neighbors
                        return (True, set(), set())
            
            # check total bomb count
            if self.total_bombs < n_bombs + len(to_flag):
                # CONTRADICTION: more flags placed than available bombs   
                return (True, set(), set())   # TODO: need to be able to clear squares based on bomb count as well
                    
            # get new simple moves (end of loop)
            moves = set(self.easy_moves(reduced))

        # if there are no hidden moves remaining, we've reached a dead end, but there's no need to branch
        involved.add(assumption[0])  # is this correct?
        involved.update(to_flag | to_clear)
        if len(all_hidden - involved) == 0:
            return (False, to_flag, to_clear)

        if depth >= self.MAX_SEARCH_DEPTH:
            return (False, to_flag, to_clear)

        # make a new assumption, spawn new branches, and handle what they return
        assumption_coord = (all_hidden - involved).pop()
        branch1 = self._explore_branch(
            (assumption_coord, Tile.FLAGGED),
            reduced.copy(),
            all_hidden,
            involved.copy(),
            depth + 1,
            n_bombs + len(to_flag)
        )
        branch2 = self._explore_branch(
            (assumption_coord, Tile.REVEALED),
            reduced.copy(),
            all_hidden,
            involved.copy(),
            depth + 1,
            n_bombs + len(to_flag)
        )

        if branch1[0] and branch2[0]:  # both branches are contradictions; so is this one
            return (True, set(), set())

        elif branch1[0] and not branch2[0]:  # branch 1 has a contradiction but 2 doesn't; return the moves from 2 (and this func's)
            return (False, branch2[1] | to_flag, branch2[2] | to_clear)

        elif not branch1[0] and branch2[0]:  # branch 2 has a contradiction but 1 doesn't; return the moves from 1 (and this func's)
            return (False, branch1[1] | to_flag, branch1[2] | to_clear)
        
        else:  # both branches hit dead ends; return the intersection of their moves (plus this func's)
            # TODO: I don't think I'm properly adding tiles to the "involved" set when they get explored within branches
            return (False, (branch1[1] & branch2[1]) | to_flag, (branch1[2] & branch2[2]) | to_clear)



if __name__ == "__main__":
    g = Game((9, 9), 10, (4, 4))
