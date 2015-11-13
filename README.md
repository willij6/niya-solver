# niya-solver
This is an oracle for the boardgame
[Niya](https://boardgamegeek.com/boardgame/125311/niya),
a simple abstract strategy game based on Tic-Tac-Toe.

I originally intended to write a program that plays Niya
well, to try and learn about strategy in the game.

However, the game is small enough that positions can be
analyzed completely using the usual methods (alpha-beta
pruning with move sorting).

I then added a GUI, using Tkinter.

The whole thing is written in Python.  **The main program is niya_solver.py**

## Controls
Eventually, a toolbar will be added, but for now,
the controls are as follows:

* `t` toggles between two modes
  * Editing mode, where pieces can be dragged freely.
    Indicated by a gray background.
  * Analysis/Play mode, which will analyze any legal position.
    Dragging pieces emulates the game, and most pieces are locked down.
    Indicated by a white background.
* `w` toggles whose turn it is.
* `z` undoes the previous action
* `ESC` clears the board
* `Space` randomly fills the board

The status bar at the bottom of the screen reveals information about
the current position, especially during Analysis/Play mode.

