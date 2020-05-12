digits = '123456789'

def printOneSide(board, colourOnTurn, numMove):
	colour = 'noires' if colourOnTurn == 'b' else 'blanches'
	newBoard = [['O' if c == colourOnTurn else '.' for c in row] for row in board]
	textBoard = '\n'.join([
			'```',
			f'Coup {numMove}.',
			f'Visibles: pierres {colour}.',
			'',
			'  abcdefghi  ',] + 
			[''.join([digits[y], ' ', ''.join(newBoard[y]), ' ', digits[y]]) for y in range(8, -1, -1)] + [
			'  abcdefghi  ',
			'```'
		])
	#textBoard = ''
	return textBoard

def printCapturedStones(capturedStones, colourOnTurn, numMove):
	nbStones = len(capturedStones)
	plural = 's' if len(capturedStones) > 1 else ''
	if colourOnTurn == 'b':
		colourOpponent, colourCapturedStones = 'Noir', 'blanche'
	else:
		colourOpponent, colourCapturedStones = 'Blanc', 'noire'
	board = [['.' for x in range(9)] for y in range(9)]
	for (x,y) in capturedStones:
		board[y][x] = 'X'
	textBoard = '\n'.join([
			'```',
			f'{colourOpponent} a capturé {nbStones} pierre{plural} {colourCapturedStones}{plural}:',
			'',
			'  abcdefghi  ',] + 
			[''.join([digits[y], ' ', ''.join(board[y]), ' ', digits[y]]) for y in range(8, -1, -1)] + [
			'  abcdefghi  ',
			'```'
		])
	return textBoard

def printBoard(board, text=''):
	textBoard = '\n'.join([
			'```',
			text,
			'',
			'  abcdefghi  ',] + 
			[''.join([digits[y], ' ', ''.join(board[y]), ' ', digits[y]]) for y in range(8, -1, -1)] + [
			'  abcdefghi  ',
			'```'
		])
	return textBoard

