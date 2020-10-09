import os
import time
import random

clear = lambda: os.system('clear')

ROW = 10
COLUMN = 7

LINE = 1 + COLUMN * 4

def initial():
    state = []
    for r in range(ROW):
        x = []
        for c in range(COLUMN):
            x.append(0)
        state.append(x)
    return state

current = initial()

def line():
    print('-' * LINE)

def is_full(state, column):
    for row in state:
        if row[column] == 0:
            return False
    return True

def add(state, column, value):
    for row in reversed(state):
        if row[column] == 0:
            row[column] = value
            return True
    return False

def show_table(state):
    line()
    for row in state:
        print('| ', end='')
        for column in row:
            value = '_'
            if column == 1:
                value = 'O'
            elif column == -1:
                value = 'X'
            print(value + ' | ', end='')
        print('')
        line()

def is_done_with_winner(state):
    # Horizontal check
    for r in range(ROW):
        for c in range(COLUMN - 3):
            # print('ROW: ' + str(r) + ', COLUMN: ' + str(c))
            if state[r][c] != 0 and state[r][c] == state[r][c+1] and state[r][c+1] == state[r][c+2] and state[r][c+2] == state[r][c+3]:
                return True, state[r][c]
            
    line()
    # Vertical check
    for c in range(COLUMN):
        for r in range(ROW - 3):
            # print('ROW: ' + str(r) + ', COLUMN: ' + str(c))
            if state[r][c] != 0 and state[r][c] == state[r+1][c] and state[r+1][c] == state[r+2][c] and state[r+2][c] == state[r+3][c]:
                return True, state[r][c]

    line()
    # \ check
    for r in range(ROW - 3):
        for c in range(COLUMN - 3):
            # print('ROW: ' + str(r) + ', COLUMN: ' + str(c))
            if state[r][c] != 0 and state[r][c] == state[r+1][c+1] and state[r+1][c+1] == state[r+2][c+2] and state[r+2][c+2] == state[r+3][c+3]:
                return True, state[r][c]
            
    line()
    # / check
    for r in range(ROW-1, 2, -1):
        for c in range(COLUMN - 3):
            # print('ROW: ' + str(r) + ', COLUMN: ' + str(c))
            if state[r][c] != 0 and state[r][c] == state[r-1][c+1] and state[r-1][c+1] == state[r-2][c+2] and state[r-2][c+2] == state[r-3][c+3]:
                return True, state[r][c]
            
    line()
    return False, None
        

def play_turn(state, value):
    available_columns = []
    for column in range(COLUMN):
        if not is_full(state, column):
            available_columns.append(column)

    if len(available_columns) == 0 or is_done_with_winner(state)[0] == True:
        return state
    
    choice = random.choice(available_columns)
    add(state, choice, value)
    next_value = 1
    if value == 1:
        next_value = -1
    return play_turn(state, next_value)

show_table(play_turn(current, 1))