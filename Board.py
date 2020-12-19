from Tile import *
from random import randint
import time


class Board:

    def __init__(self, rows, cols, num_mines):
        self.cols = cols            # Number of columns in the game matrix
        self.rows = rows            # Number of rows in the game matrix
        self.num_mines = num_mines  # Number of mines in the game matrix
        self.is_solved = False      # Is the game finished yet?

        self.mined = set()          # Set of Tile()s from matrix that contain mines
        self.flagged = set()        # Set of Tile()s from matrix with flags on them
        self.opened = set()         # Set of Tile()s from matrix which are opened

        # 2-D array.
        # The minesweeper map/matrix.
        # TODO: Should name be m, M, or matrix
        self.M = [[Tile() for c in range(cols)] for r in range(rows)]

        # 2-D array which stores lists. 3-D?
        # At each coordinate (r,c), a list of coordinates is stored.
        # This list contains the coordinates of the 8 tiles around (r,c).
        self.nbds = [[None for c in range(cols)] for r in range(rows)]

        self.tracker = list()  # keep track of solve processes used, just for fun

    ############################## PRINTS ##############################

    # Prints complete revealed board on the left,
    #   with Xs marking mines, and all numbers including 0s shown.
    # Prints the current state of the board on the right,
    #   with #s marking covered tiles, and Fs marking flags. 0s shown as -s.
    #   Bombs are not marked. This printing is what a game player would see.

    def print(self):
        for r in range(self.rows):
            for c in range(self.cols):
                if self.M[r][c].is_mined:
                    print("X", end=' ')
                else:
                    print(self.M[r][c].number, end=' ')
            print("          ", end='')
            for c in range(self.cols):
                if self.M[r][c].is_flagged:
                    print("F", end=' ')
                elif self.M[r][c].is_opened:
                    if self.M[r][c].is_mined:
                        print("X", end=' ')
                    elif self.M[r][c].number == 0:
                        print("-", end=' ')
                    else:
                        print(self.M[r][c].number, end=' ')
                else:
                    print("#", end=' ')
            print("\n")


    # Prints only current state of board using special characters
    # Flag emoijis denote flags, solid squares are covered tiles, and zeroes are empty
    def print_pretty(self):
        for r in range(self.rows):
            for c in range(self.cols):
                if self.M[r][c].is_flagged:
                    #print("F", end = ' ')
                    print(chr(128681), end=' ')  # flag
                elif self.M[r][c].is_opened:
                    if self.M[r][c].is_mined:
                        print("X", end='  ')
                    elif self.M[r][c].number == 0:
                        #print("-", end = ' ')
                        print(" ", end='  ')
                    else:
                        print(self.M[r][c].number, end='  ')
                else:
                    # print("#", end=' ')
                    print(chr(9608), end='  ')  # square
            print("\n")

    ############################## GAME SETUP ##############################

    # Stores the neighborhood coordinates of
    # every tile for future lookup
    # Originally had a nbd(r,c) function which would
    # find and return the nbd of a tile. It was used frequently
    # enough that it was beneficial to just store its results.
    def fill_nbds(self):
        for r in range(self.rows):
            for c in range(self.cols):
                n = list()
                for rshift in (-1, 0, 1):
                    for cshift in (-1, 0, 1):
                        if not (rshift == 0 and cshift == 0):
                            srow = r+rshift
                            scol = c+cshift
                            if (srow >= 0) and (scol >= 0) and (srow < self.rows) and (scol < self.cols):
                                n.append([srow, scol])
                self.nbds[r][c] = n


    # Places the mines at random distinct positions,
    # numbers all the tiles accordingly,
    # then opens the tile at start row/col.
    # Starting tile is guaranteed to be a 0 tile.
    def start(self, row, col):
        self.fill_nbds()
        start_nbd = self.nbds[row][col]
        self.M[row][col].number = 0
        placed_mines = 0
        while placed_mines < self.num_mines:
            r = randint(0, self.rows - 1)
            c = randint(0, self.cols - 1)
            if (not self.M[r][c].is_mined) and ([r, c] not in start_nbd) and ([r, c] != [row, col]):
                self.mine_tile(r, c)
                placed_mines += 1
        for r in range(self.rows):
            for c in range(self.cols):
                nbd_bombs = 0
                if self.M[r][c] not in self.mined:
                    n = self.nbds[r][c]
                    for coord in n:
                        if self.M[coord[0]][coord[1]].is_mined:
                            nbd_bombs += 1
                self.M[r][c].number = nbd_bombs
                self.M[r][c].xy = [r, c]
        self.tracker.append("start")
        self.open_tile(row, col)

    ############################## TILE CHANGES ##############################

    # Opens a tile.
    # Add tile to set of opened tiles.
    # If tile is 0, opens its surroundings like in a regular game.
    # This used to be heavily recursive, but would hit the limit for large maps.
    #   I removed calling open_tile() on already opened tiles, and
    #   I also chose to open zeroes and their nbds using a queue instead of recursion.

    def open_tile(self, row, col):
        if not self.M[row][col].is_opened:
            self.M[row][col].is_opened = True
            tile = self.M[row][col]
            self.opened.add(tile)

            if tile.number == 0:
                zeroes = self.nbd_unopened_unflagged(row, col)
                while zeroes:
                    z = zeroes.pop(0)
                    self.opened.add(self.M[z[0]][z[1]])
                    self.M[z[0]][z[1]].is_opened = True
                    if self.M[z[0]][z[1]].number == 0:
                        n = self.nbd_unopened_unflagged(z[0], z[1])
                        for coords in n:
                            if (coords not in zeroes):
                                zeroes.append(coords)


    # Mark tile as flagged.
    # Add tile to set of flagged tiles.
    def flag_tile(self, row, col):
        self.M[row][col].is_flagged = True
        self.flagged.add(self.M[row][col])


    # Set tile as mined.
    # Add tile to set of mine tiles.
    def mine_tile(self, row, col):
        self.M[row][col].is_mined = True
        self.mined.add(self.M[row][col])

    ############################## CHECKS ##############################

    # Return true and set is_solved to true if board is solved.

    def board_check(self):
        if self.flagged != self.mined:  # mines unflagged
            return False
        elif self.opened.intersection(self.mined):  # opened mines
            return False
        elif len(self.opened) != ((self.rows * self.cols)-self.num_mines):  # unopened tiles
            return False
        self.is_solved = True
        return True


    # Returns true if tile has all its flags
    # and has no covered tiles in radius
    def tile_check(self, row, col):
        if self.tile_flag_check(row, col) and not self.nbd_unopened_unflagged(row, col):
            return True
        return False


    # returns true if a tile has all its flags
    def tile_flag_check(self, row, col):
        if self.tile_flag_count(row, col) == self.M[row][col].number:
            return True
        return False


    # returns number of flags in tile's radius
    def tile_flag_count(self, row, col):
        flag_count = 0
        for coords in self.nbds[row][col]:
            if self.M[coords[0]][coords[1]].is_flagged:
                flag_count += 1
        return flag_count

    ############################## FETCH ##############################

    # Returns a list of the coordinates surrounding a tile
    # which are covered yet not flagged

    def nbd_unopened_unflagged(self, row, col):
        result = list()
        for coords in self.nbds[row][col]:
            t = self.M[coords[0]][coords[1]]
            if (not t.is_opened) and (not t.is_flagged):
                result.append(t.xy)
        return result


    # Returns a list of coordinates of opened number tiles in nbd
    # (border coords in nbd of tile)
    def nbd_numbers(self, row, col):
        result = list()
        if (not self.M[row][col].is_opened) and (not self.M[row][col].is_flagged):
            for coords in self.nbds[row][col]:
                tile = self.M[coords[0]][coords[1]]
                if (tile.is_opened) and (tile.number != 0) and (tile.xy != [row, col]):
                    result.append([coords[0], coords[1]])
        return result


    # Returns list of "border tile" coordinates meaning:
    # numbered, nonzero, open tiles
    def border_coords(self):
        result = list()
        for r in range(self.rows):
            for c in range(self.cols):
                tile = self.M[r][c]
                if (tile.is_opened) and (tile.number != 0):
                    result.append(tile.xy)
        return result


    # Returns list of unsolved "border tile" coordinates, meaning:
    # numbered, nonzero, opened tiles
    # with unopened, unflagged tiles in their radius
    def border_coords_unsolved(self):
        result = list()
        for coords in self.border_coords():
            if self.nbd_unopened_unflagged(coords[0], coords[1]):
                result.append([coords[0], coords[1]])
        return result


    # Returns list of coordinates representing
    # the border made up of covered tiles
    def border_coords_covered(self):
        bcc = list()
        for bc in self.border_coords_unsolved():
            for nc in self.nbd_unopened_unflagged(bc[0], bc[1]):
                if nc not in bcc:
                    bcc.append(nc)
        return bcc


    def all_covered(self):
        ac = list()
        for r in range(self.rows):
            for c in range(self.cols):
                if (not self.M[r][c].is_opened) and (not self.M[r][c].is_flagged):
                    ac.append([r, c])
        return ac

    ############################## SOLVING ##############################

    # Simplest form of solving.
    # Returns number of changes it made.
    # If the tile has all its flags, yet still has covered tiles around it,
    #   those covered tiles must all be safe. Open them.
    # If the number on a tile is equal to the number of covered tiles around it,
    #   those covered tiles must all be flags. Flag them.
    # Repeat monkey() until a repetition finishes without making any changes,
    #   meaning monkey() has done all it can.
    # This function originally used recursion, but would hit the recursion limit
    #   for reasons I could not discover. It was simplified by using the change count.

    def monkey(self, print_progress=False, print_pretty=True, print_delay=1, print_clear=True):
        changes = 0
        prev_changes = -1
        while (changes != prev_changes):

            prev_changes = changes

            if (print_progress):
                if (print_clear):
                    print(chr(27) + "[2J")  # clear terminal
                else:
                    print(chr(27))  # escape character, push old print back
                if (print_pretty):
                    self.print_pretty()
                else:
                    self.print()
                time.sleep(print_delay)

            # if a border tile has all its flags...
            for bcu in self.border_coords_unsolved():
                if self.M[bcu[0]][bcu[1]].number - self.tile_flag_count(bcu[0], bcu[1]) == 0:
                    for coords in self.nbd_unopened_unflagged(bcu[0], bcu[1]):
                        self.open_tile(coords[0], coords[1])
                        changes += 1
                # if a border tile's number == covered tiles in its nbd
                nbd = self.nbd_unopened_unflagged(bcu[0], bcu[1])
                if len(nbd) == self.M[bcu[0]][bcu[1]].number - self.tile_flag_count(bcu[0], bcu[1]):
                    for coords in nbd:
                        self.flag_tile(coords[0], coords[1])
                        changes += 1

            # if remaining covered tiles = remaining mines, open them all
            ac = self.all_covered()
            if (len(self.mined) == len(self.flagged)):
                for coords in ac:
                    self.tracker.append("all_covered")
                    self.open_tile(coords[0], coords[1])
                    changes += 1
            if len(ac) == (len(self.mined) - len(self.flagged)):
                for coords in ac:
                    self.tracker.append("all_covered")
                    self.flag_tile(coords[0], coords[1])
                    changes += 1

        self.tracker.append(str("monkey "+str(changes)))
        return changes


    # Place flags based on solutions to a reduced matrix
    # formed from border tiles and the covered tiles around them.
    # like a contraint problem.
    # Returns the number of changes it made.
    def gauss(self):
        # for example: in a simple board        1   2   x
        # where x represents a covered tile:    x   2   1
        # The matrix row representing the bottom "2" should be: 
        #  1x_1 + 1x_2 = 2 --> 1 1 2.
        # The matrix row representing the left "1" should be 
        #  1x_1 + 0x_2 = 1 --> 1 0 1.
        #   as x_2 is not in this "1"'s radius, 
        #   it doesn't contribute to the "1" tile's value.
        # x values can be either a 1 or a 0 -- a mine or a safe tile.
        g = []
        bcs_covered = self.border_coords_covered()  # covered tiles on border
        for bc in self.border_coords_unsolved():  # unfinished opened tiles on border
            row = [0 for _ in range(len(bcs_covered)+1)]
            row[-1] = self.M[bc[0]][bc[1]].number - \
                self.tile_flag_count(bc[0], bc[1])   # tile value at end of row
            bc_nbd = self.nbd_unopened_unflagged(bc[0], bc[1])
            for i in range(len(bcs_covered)):
                if bcs_covered[i] in bc_nbd:
                    row[i] = 1
            g.append(row)

        # Reduce matrix into reduced row echelon form.
        # This can be interpreted to determine where to put flags.
        # For example, a row "0 1 0 0 1" tells us that x_2 would be a 1/mine,
        #   as x_2=1 is the only solution to 0x_1 + 1x_2 + 0x_3 + 0x_4 = 1.
        # Similarly, a row 1 0 -1 1 tells us that x_1 is a mine and x_3 is clear,
        #   as x_1=1 x_3=0 is the only solution to 1x_1 + 0x_2 + -1x_3 = 1.
        # And so on.
        # Based on pseudocode from Wikipedia.
        try:
            lead_var = 0  # lead variable is first nonzero value in row when in RREF
            g_rows = len(g)
            g_cols = len(g[0])

            for r in range(g_rows):
                if g_cols <= lead_var:
                    raise Exception  # stop
                i = r
                while g[i][lead_var] == 0:  # move forward until first nonzero entry in row
                    i += 1
                    if g_rows == i:
                        i = r
                        lead_var += 1
                        if g_cols == lead_var:  # went through whole row
                            raise Exception  # stop

                # switch row with found i row
                temp = g[r]
                g[r] = g[i]
                g[i] = temp

                # if lead nonzero (so, if row is nonzero)
                if g[r][lead_var] != 0:
                    div = g[r][lead_var]  # divide row by lead value
                    for j in range(len(g[r])):
                        g[r][j] = g[r][j] / div

                for i in range(g_rows):
                    if i != r:
                        sub = g[i][lead_var]  # subtract lead*g[r][j] from row
                        for j in range(len(g[i])):
                            g[i][j] = g[i][j] - (sub * g[r][j])

                lead_var += 1
        except Exception:  # if we hit a "stop" in the reduction algorithm
            pass

        mines = list()
        clear = list()
        for row in g:   # make a list of the nonzero elements of the list
            coeffs = list()
            coeff_indices = list()
            value = row[-1]  # last value in row
            for i in range(len(row[:-1])):
                if abs(row[i]) > 0:
                    coeffs.append(row[i])
                    coeff_indices.append(i)

            # comparing the sum of pos/neg coeffs to the value at end of row
            # is easier than considering each coeff individually
            # If either of pos/neg coeffs add up to value at end of row,
            # those pos/neg coeffs must be mines (x=1) and the neg/pos coeffs must be clear (x=1).
            sum_pos = 0  # sum positive coefficients
            sum_neg = 0  # sum negative coefficients
            for c in coeffs:    # find sums
                if c > 0:
                    sum_pos += c
                if c < 0:
                    sum_neg += c
            if value == sum_pos:    # if positive coeffs add up to row value,
                # look at spaces in row instead of coeffs, so we can "map" to bcs_covered
                for r in range(len(row)-1):
                    if row[r] > 0:  # pos coeffs represent bomb tiles
                        mines.append(bcs_covered[r])
                    if row[r] < 0:  # neg coeffs represent clear tiles
                        clear.append(bcs_covered[r])
            if value == sum_neg:    # vice versa
                for r in range(len(row)-1):
                    if row[r] < 0:
                        mines.append(bcs_covered[r])
                    if row[r] > 0:
                        clear.append(bcs_covered[r])
            '''newmines = list()   # make mines list all entries in mines that aren't in not_mines
            for b in mines:     # maybe this step can be eliminated?
                if b not in clear:
                    newmines.append(b)
            mines = newmines'''

        for bc in mines:    # flag all the coords the process determined belong to mines
            self.flag_tile(bc[0], bc[1])

        self.tracker.append(str("gauss " + str(len(mines))))
        return len(mines)


    # Runs monkey/gauss until they are no longer changing the board.
    # Returns the time it took to run (including printing progress)
    def driver(self, print_progress=False, print_pretty=True, print_delay=1, print_clear=True):
        start_time = time.time()
        changes = 0
        prev_changes = -1
        while (changes != prev_changes):
            prev_changes = changes
            changes += self.monkey(print_progress,
                                   print_pretty, print_delay, print_clear)
            # print("to_gauss")
            # time.sleep(.25)
            changes += self.gauss()

        exploration = 100 * \
            (1-(len(self.all_covered()) / (self.rows * self.cols)))
        endappend = list()
        if exploration == 100:
            endappend.append("Won")
        else:
            endappend.append("Lost")

        endappend.append(exploration)
        endappend.append(str(len(self.flagged)) + "/" + str(len(self.mined)))
        endappend.append(exploration)
        endappend.append(time.time()-start_time)
        self.tracker.append(endappend)
        return self.tracker

        # TODO: brute force border combinations?
        # TODO: generate all possible boards for brute force?
        # TODO: guessing?
