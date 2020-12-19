from Board import Board
from random import randint


def get_settings():
    valid_input = False
    while not valid_input:
        difficulty = int(input(
            "\nSelect difficulty: \n 1: 9x9 with 10 mines \n 2: 16x16 with 40 mines \n 3: 16x30 with 99 mines \n 4: Custom size/trials \n "))
        if difficulty == 1:
            return [9, 9, 10, 1, True, True, 0.25, True, False]
        elif difficulty == 2:
            return [16, 16, 40, 1, True, True, 0.25, True, False]
        elif difficulty == 3:
            return [16, 30, 99, 1, True, True, 0.25, True, False]
        elif difficulty == 4:
            rows = int(input("Rows:   "))
            cols = int(input("Cols:   "))
            mines = int(input("Mines:  "))
            trials = int(input("Trials: "))
            print_progress = False
            if trials == 1:
                print_progress = True
            if (rows > 0) and (cols > 0) and (trials > 0):
                return [rows, cols, mines, trials, print_progress, True, 0.25, True, False]
        elif difficulty == 0:
            print("EXTRA OPTIONS")
            print("Board options [enter integers]:")
            rows = int(input("Rows:   "))
            cols = int(input("Cols:   "))
            mines = int(input("Mines:  "))
            trials = int(input("Trials: "))
            print("Print options [enter 1/0]:")
            print_progress = int(input("print_progress: "))
            print_pretty = int(input("print_pretty:   "))
            print_delay = int(input("print_delay:    "))
            print_clear = int(input("print_clear:    "))
            print_tracker = int(input("print_tracker:  "))
            return [rows, cols, mines, trials, print_progress, print_pretty, print_delay, print_clear, print_tracker]
        else:
            print("Invalid input.")


def main():

    rows, cols, mines, trials, print_progress, print_pretty, print_delay, print_clear, print_tracker = get_settings()

    print_pretty = False  # this didnt end up looking right on most PCs

    total_wins = 0
    total_time = 0
    total_exp = 0
    for _ in range(trials):

        b = Board(rows, cols, mines)
        b.start(randint(0, rows-1), randint(0, cols-1))
        tracker = b.driver(print_progress, print_pretty,
                           print_delay, print_clear)

        total_time += tracker[-1][-1]
        total_exp += tracker[-1][1]
        if print_tracker:
            print(tracker)

        if b.board_check():
            total_wins += 1

    print()
    if trials == 1:
        if total_wins == 1:
            print("WIN")
        else:
            print("Loss:\n Explored ", total_exp, '%', sep='')
    else:
        print("AVG TIME:       ", total_time / trials)
        print("TOTAL TIME:     ", total_time)
        print("WIN RATE:        ", 100*total_wins / trials, '%', sep='')
        print("AVG EXPLORATION: ", total_exp / trials, '%', sep='')
    print()


main()
