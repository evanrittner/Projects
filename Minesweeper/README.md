# Minesweeper

<p align="middle">
  <img src="/Minesweeper/images/solver.gif" width="1000"/>
</p>

For this project, I implemented [Minesweeper](https://en.wikipedia.org/wiki/Minesweeper_(video_game)) as a command line based game in Python and ncurses. My main goals here were to first, gain familiarity with ncurses in Python, and second and more importantly, to design interesting algorithms for running the game and solving it.

The application as it currently stands, has finished core functionality, but is missing some more superficial features, and is not yet finely polished. However, I'm publishing it here now, since I know how unlikely it is I'll end up totally completing it in any reasonable amount of time.

## Gameplay
To run the game, simply run the main file `minesweeper.py` with a Python interpreter in your terminal of choice. In general, the game can handle interaction both via WASD keyboard controls, the arrow keys, or with mouse clicks. The main menu, shown below, has the three standard presets, an interface to play with custom settings, and three other options that are currently not fully implemented (Keybindings, Statistics, and Settings).

<p align="middle">
  <img src="/Minesweeper/images/menu.jpg" width="600"/>
</p>

When playing, WASD or arrow keys move the cursor; 'R' or left click reveals the tile, and 'F' or right click flags the tile. 'X' pauses, and while paused, you can hit 'R' to resume, 'X' to quit, 'N' to start a new game with the same settings, or 'B' to reveal all the remaining bombs. Beside these controls, the gameplay is much the same as in standard minesweeper. There are also features related to cheating, or solving the board automatically. I'll discuss these below, in the next section.

## Features

<img align="right" width="600" src="/Minesweeper/images/custom_game_menu.jpg">

* In the custom mode, the bomb density and an approximate difficulty rating are provided when configuring the game (see the image on the right)
* The first click always 'chords', or reveals a region of tiles (almost never just a single tile)
* Properly random bomb generation: unlike in the original Minesweeper, all squares have a uniform probability of being mines
* Support for very small terminals and very large games: if the game board does not fit on the screen, it will allow the user to move around it, viewing as much as can fit on the screen at once. (This is hard to show in screenshots, so you'll have to play the game to see exactly how this works.) Also, since the minimum-size UI supports terminals as small as 7x20, any size game can be played on a terminal as small as 7 characters high by 20 characters wide.

### Solver
I've included a number of cheats or assists in the game. The first, and mildest, reflects how the other algorithms 'view' the board, as well as how I think about it in my head while playing. I'm calling it "Reduced mode", since it simplifies the board down to only the currently-relevant information. First, it hides all tiles that are not near the hidden-revealed boarder: tiles that are still hidden, but are far away from any revealed tiles, cannot be solved yet, since they're too far away from all the information from the revealed tiles. Also, tiles that are deep within other revealed tiles are not useful, since they aren't near enough to any hidden tiles to provide any information. In Reduced mode, the only tiles shown are revealed tiles that neighbor hidden tiles, and hidden tiles that neighbor revealed tiles. Finally, since some of these remaining revealed tiles might neighbor flagged locations that were hidden, I subtract off the number of flagged tiles any revealed tiles are already neighboring. (You can think of this quantity as the tile's "bomb deficit".) To hopefully make this more clear, the image on the left is the board regularly, and on the right, it's in Reduced mode.

<center> <img align="right" width="4050" src="/Minesweeper/images/normal.jpg">
<img align="right" width="400" src="/Minesweeper/images/reduced.jpg"> </center>

Now, onto the actual cheats. I first have a cheat that executes all "simple" moves. There are two situations that I've defined to yield "simple" moves:

1. When a revealed tile (one with a number) has an equal number of neighboring flags to its number, any hidden neighbors it has can safely be revealed
2. If a revealed tile has exactly enough neighboring hidden tiles to satisfy its count, all those nieghbors must be bombs, and can be flagged

With just these two very simple rules, my "simple" solver can usually beat the Beginner and Intermediate presets. Pressing "K" will perform one simple move automatically (if any exist); pressing "J" will perform any and all simple moves repeatedly, until the game is won, or until there are no more simple moves. I should note that if the player flags any tiles incorrectly, neither this solver or the "smart" one I'll describe in a minute will catch it, and they'll probably both lose the game be revealing a bomb.

This simple solver works pretty well, but it doesn't stand a chance with the Expert preset. To handle this, I wrote what I'm calling the "smart" solver.


### To-Do List
* Support for modifications of almost all keybindings, without restarting the game: core functionality finished, just need to make the menu UI
* Logging and display of game statistics, like number of wins, number of games played, win streaks, win percentages on each preset, etc. The core logging of data is finished, but the UI is not. I could certainly also add more tracked stats
* Rework the pause menu/screen during the game, including making the options more clear
* Many small improvements to the smart solver, including better endgame behavior (like being able to reveal tiles that cannot be a bomb, or must be a bomb, deducible due to the remaining bomb count).
* Modify the 'smart' solver to allow the user to only get a single move as help, instead of the computer 'taking over' when in this solving mode
* Use the 'smart' solver to allow the user to play only solvable boards: the computer should only configure the board in ways that do not require any guessing in this mode. Maybe pre-generate suitable boards, instead of doing it while the user is playing?

