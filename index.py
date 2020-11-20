from enum import Enum
import numpy as np
import random
import math
import time
import pygame
import os
import threading

from pygame.locals import *

clear = lambda: os.system('clear')

pygame.init()
pygame.font.init()

MONO_SPACE = pygame.font.SysFont('monospace', 30)

WIDTH = 700
HEIGHT = 700

LINE_WIDTH = 2
MARGIN = 50

screen = pygame.display.set_mode([WIDTH, HEIGHT])
running = True
playing = True

board = None
PLAYER_TURN = 1
turn = 1
winner = ""

ROW_COUNT = 5
COLUMN_COUNT = 5
WINNING_LENGTH = 4
DEPTH = 7

ai_is_playing = False

mouse_position = None

THE_REST = WIDTH - MARGIN * 2
PER_GRID = min(THE_REST // COLUMN_COUNT, THE_REST // ROW_COUNT)

WIDTH_SCOPE = MARGIN + (COLUMN_COUNT) * PER_GRID
HEIGHT_SCOPE = MARGIN + (ROW_COUNT) * PER_GRID

CIRCLE_RADIUS = (PER_GRID - 5) // 2
game_over = False

class Color(Enum):
	WHITE = (255, 255, 255)
	BLACK = (0, 0, 0)
	RED = (255, 0, 0)
	GREEN = (0, 255, 0)
	BLUE = (0, 0, 255)
	PURPLE = (255, 0, 255)	

class Piece(Enum):
  AI = -1
  Empty = 0
  Player = 1

def create_board():
  board = np.zeros((ROW_COUNT, COLUMN_COUNT))
  board.fill(Piece.Empty.value)
  return board

def drop_piece(board, row, col, piece):
  board[row][col] = piece

def next_row(board, col):
	for row in range(ROW_COUNT - 1, -1, -1):
		if board[row][col] == 0:
			return row
	return -1

def get_available_columns(board):
  available_columns = []
  for column in range(COLUMN_COUNT):
    for row in range(ROW_COUNT):
      if board[row][column] == int(Piece.Empty.value):
        available_columns.append(column)
        break
  return available_columns

def winning_move(board, piece):
	# Check horizontal locations for win
	for c in range(COLUMN_COUNT-3):
		for r in range(ROW_COUNT):
			if board[r][c] == piece and board[r][c+1] == piece and board[r][c+2] == piece and board[r][c+3] == piece:
				return True

	# Check vertical locations for win
	for c in range(COLUMN_COUNT):
		for r in range(ROW_COUNT-3):
			if board[r][c] == piece and board[r+1][c] == piece and board[r+2][c] == piece and board[r+3][c] == piece:
				return True

	# Check positively sloped diaganols
	for c in range(COLUMN_COUNT-3):
		for r in range(ROW_COUNT-3):
			if board[r][c] == piece and board[r+1][c+1] == piece and board[r+2][c+2] == piece and board[r+3][c+3] == piece:
				return True

	# Check negatively sloped diaganols
	for c in range(COLUMN_COUNT-3):
		for r in range(3, ROW_COUNT):
			if board[r][c] == piece and board[r-1][c+1] == piece and board[r-2][c+2] == piece and board[r-3][c+3] == piece:
				return True
	
	return False

def print_board(board):
	global COLUMN_COUNT
	line = 1 + COLUMN_COUNT * 4
	print('-' * line)
	for row in board:
		print('| ', end='')
		for column in row:
			value = '_'
			if column == Piece.Player.value:
				value = 'O'
			elif column == Piece.AI.value:
				value = 'X'
			print(value + ' | ', end='')
		print('')
		print('-' * line)

def is_leaf_node(board):
	return winning_move(board, Piece.Player.value) or winning_move(board, Piece.AI.value) or len(get_available_columns(board)) == 0

def evaluate_window(window, piece):
	score = 0
	opponent_piece = Piece.Player.value
	if piece == Piece.Player.value:
		opponent_piece = Piece.AI.value

	if window.count(piece) == 4:
		score += 100
	elif window.count(piece) == 3 and window.count(Piece.Empty.value) == 1:
		score += 5
	elif window.count(piece) == 2 and window.count(Piece.Empty.value) == 2:
		score += 2

	if window.count(opponent_piece) == 3 and window.count(Piece.Empty.value) == 1:
		score -= 4

	return score

def score_position(board, piece):
	score = 0
	
	# Score Horizontal
	for r in range(ROW_COUNT):
		row_array = [int(i) for i in list(board[r,:])]
		for c in range(COLUMN_COUNT-3):
			window = row_array[c:c+WINNING_LENGTH]
			score += evaluate_window(window, piece)

	# Score Vertical
	for c in range(COLUMN_COUNT):
		col_array = [int(i) for i in list(board[:,c])]
		for r in range(ROW_COUNT-3):
			window = col_array[r:r+WINNING_LENGTH]
			score += evaluate_window(window, piece)

	# Score posiive sloped diagonal
	for r in range(ROW_COUNT-3):
		for c in range(COLUMN_COUNT-3):
			window = [board[r+i][c+i] for i in range(WINNING_LENGTH)]
			score += evaluate_window(window, piece)

	# Score negative sloped diagonal
	for r in range(ROW_COUNT-3):
		for c in range(COLUMN_COUNT-3):
			window = [board[r+3-i][c+i] for i in range(WINNING_LENGTH)]
			score += evaluate_window(window, piece)

	return score

def minimax(board, depth, alpha, beta, maximizingPlayer):
	available_columns = get_available_columns(board)
	is_left_node = is_leaf_node(board)
	if depth == 0 or is_left_node:
		if is_left_node:
			if winning_move(board, Piece.AI.value):
				return (None, 100000000000000)
			elif winning_move(board, Piece.Player.value):
				return (None, -10000000000000)
			else: # Game is over, no more valid moves
				return (None, 0)
		else: # Depth is zero
			return (None, score_position(board, Piece.AI.value))
	
	if maximizingPlayer:
		value = -math.inf
		column = random.choice(available_columns)
		for col in available_columns:
			row = next_row(board, col)
			b_copy = board.copy()
			drop_piece(b_copy, row, col, Piece.AI.value)
			new_score = minimax(b_copy, depth-1, alpha, beta, False)[1]
			if new_score > value:
				value = new_score
				column = col
			alpha = max(alpha, value)
			if alpha >= beta:
				break
		return column, value

	else: # Minimizing player
		value = math.inf
		column = random.choice(available_columns)
		for col in available_columns:
			row = next_row(board, col)
			b_copy = board.copy()
			drop_piece(b_copy, row, col, Piece.Player.value)
			new_score = minimax(b_copy, depth-1, alpha, beta, True)[1]
			if new_score < value:
				value = new_score
				column = col
			beta = min(beta, value)
			if alpha >= beta:
				break
		return column, value

def player_turn(board):
	global winner, playing
	available_columns = get_available_columns(board)
	column = -1
	while column not in available_columns:
		print(available_columns)
		column = int(input("Please choose one of these value:"))
	row = next_row(board, column)
	drop_piece(board, row, column, Piece.Player.value)
	if winning_move(board, Piece.Player.value):
		playing = False
		winner = 'Player Won'

	available_columns = get_available_columns(board)
	if len(winner) == 0 and len(available_columns) == 0:
		playing = False
		winner = "Draw"

def check_winner(board):
	global winner, playing
	if not playing:
		return True
	available_columns = get_available_columns(board)

	if winning_move(board, Piece.Player.value):
		winner = "Play won"
		playing = False
	elif winning_move(board, Piece.AI.value):
		winner = "AI won"
		playing = False
	elif len(winner) == 0 and len(available_columns) == 0:
		playing = False
		winner = "Draw"

def ai_turn(board):
	global ai_is_playing, winner, playing
	if check_winner(board):
		ai_is_playing = False
		return
	available_columns = get_available_columns(board)
	column, value = minimax(board, DEPTH, -math.inf, math.inf, True)
	print(str(column) + ' :: ' + str(value))
	if column in available_columns:
		row = next_row(board, column)
		drop_piece(board, row, column, Piece.AI.value)

	ai_is_playing = False
	check_winner(board)

def main(playerTurn = 1):
  global PLAYER_TURN, board, turn, winner
  PLAYER_TURN = playerTurn
  board = create_board()
  turn = 1
  winner = ""
  while True:
    clear()
    print_board(board)
    
    if turn % 2 == PLAYER_TURN:
      game_over = player_turn(board)
    else:
      game_over = ai_turn(board)
    
    if game_over:
      print_board(board)
      winner = "'Player'" if turn % 2 == PLAYER_TURN else "'AI'"
      print("Winner is " + winner )
      break

    turn += 1

def get_column_from_mouse_position():
	if mouse_position is None:
		return -1
	x, y = mouse_position
	if x >= MARGIN and x <= WIDTH_SCOPE and y >= MARGIN and y <= HEIGHT_SCOPE:
		for c in range(COLUMN_COUNT):
			if x >= MARGIN + c * PER_GRID and x <= MARGIN + (c + 1) * PER_GRID:
				return c
	return -1

def draw_highlight_mouse(board):
	c = get_column_from_mouse_position()
	if c < 0:
		return
	columns = get_available_columns(board)
	color = Color.GREEN.value if c in columns else Color.RED.value
	pygame.draw.rect(screen, color, pygame.Rect(MARGIN + c * PER_GRID, MARGIN, PER_GRID, PER_GRID * ROW_COUNT))

def draw_table():
	for r in range(ROW_COUNT + 1):
		pygame.draw.line(screen, Color.BLACK.value, (MARGIN, MARGIN + r * PER_GRID), (WIDTH_SCOPE, MARGIN + r * PER_GRID), LINE_WIDTH)
	
	for c in range(COLUMN_COUNT + 1):
		pygame.draw.line(screen, Color.BLACK.value, (MARGIN + c * PER_GRID, MARGIN), (MARGIN + c * PER_GRID, HEIGHT_SCOPE), LINE_WIDTH)

def draw_board(board):
	draw_highlight_mouse(board)
	draw_table()
	for row in range(ROW_COUNT):
		for column in range(COLUMN_COUNT):
			piece = board[row][column]
			position = (MARGIN + column * PER_GRID + PER_GRID // 2, MARGIN + row * PER_GRID + PER_GRID // 2)
			if piece == Piece.Player.value:
				pygame.draw.circle(screen, Color.BLUE.value, position, CIRCLE_RADIUS)
			elif piece == Piece.AI.value:
				pygame.draw.circle(screen, Color.PURPLE.value, position, CIRCLE_RADIUS)

board = create_board()

while running:
	# Did the user click the window close button?
	for event in pygame.event.get():
			if event.type == QUIT:
				running = False
			elif not playing or ai_is_playing:
				pass
			elif event.type == MOUSEMOTION:
				mouse_position = pygame.mouse.get_pos()
			elif event.type == MOUSEBUTTONUP:
				mouse_position = pygame.mouse.get_pos()
				c = get_column_from_mouse_position()
				if c >= 0:
					r = next_row(board, c)
					if r != -1:
						drop_piece(board, r, c, Piece.Player.value)
						check_winner(board)
						turn += 1

	if (turn % 2) != PLAYER_TURN:
		# ai_turn(board)
		x = threading.Thread(target=ai_turn, args=(board,))
		x.start()
		ai_is_playing = True
		turn += 1
					
	# Fill the background with white
	screen.fill((255, 255, 255))
	draw_board(board)

	if playing:
		if ai_is_playing:
			textsurface = MONO_SPACE.render('AI is playing', False, (0, 0, 0))
		else:
			textsurface = MONO_SPACE.render('Your Turn', False, (0, 0, 0))
	else:
		textsurface = MONO_SPACE.render(winner, False, (0, 0, 0))
		
	screen.blit(textsurface,(5,5))

	# Draw a solid blue circle in the center
	# pygame.draw.circle(screen, Color.BLUE.value, (250, 250), 75)

	# pygame.draw.line(screen, Color.BLACK.value, (0, 0), (250, 250), 1)

	# Flip the display
	pygame.display.flip()

# Done! Time to quit.
pygame.quit()