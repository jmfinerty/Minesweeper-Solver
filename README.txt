This is a project which uses multiple processes to solve a generated mindsweeper board.

    Firstly, what I have called "monkey" solve--simple logic.
    This is, for example, when a '2' tile has two covered squares around it, and no flags.
    These covered squares must be mines.
    Similarly, suppose a '2' tile had 2 flags around it.
    All other tiles around the '2' must be safe.

    Secondly, gaussian elimination. This process treats each tile and its surrounding 
    tiles like a matrix. This matrix, through the gaussian elimination algorithm,
    is then reduced into a reduced row echelon form, or as close to it as possible,
    and the result is interpreted to decide flag placement and tile opening.

    The monkey process is applied until the board state is no longer changing,
    implying that, without more insight, it has finished.
    At this point, the gaussian algorithm is applied, hoping to gain more information.
    Each of these repeat until the board, as a whole, is unchanging.
    At this point, it is printed if the game was won or lost, 
    and how much of the board was explored if lost.

When main.py is run, it will ask for user input settings. 
These settings define the difficulty of the board, as well as
some settings which determine how the board state is printed.

If any of the default settings are chosen, 
the board's 'solution' is printed,
followed by the current state of the game,
at each iteration.

In the solution board, X represents a bomb, and numbers
represent the number which Minesweeper would display on that tile.
In the game state board, F represents where flags have been placed, and
numbers represent the same as before.