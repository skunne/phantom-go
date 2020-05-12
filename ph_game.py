import ph_botstate
import ph_printboard
import ph_liberties
import ph_endgame

def alreadyOccupied(x, y, board):
	return (board[y][x] != '.')

def countLiberties(xcoord, ycoord, board, colour):
	newBoard = [[c for c in row] for row in board]
	#print(f'countLiberties: adding stone [{colour}] at ({xcoord},{ycoord})')
	print(newBoard)
	liberties = ph_liberties.countLiberties(xcoord, ycoord, newBoard, colour)
	print(f'Liberties of ({xcoord},{ycoord}): {liberties}.')
	return liberties

def virtualPlayAndCountLiberties(xcoord, ycoord, board, colour):
	newBoard = [[c for c in row] for row in board]
	newBoard[ycoord][xcoord] = colour
	#print(f'countLiberties: adding stone [{colour}] at ({xcoord},{ycoord})')
	print(newBoard)
	liberties = ph_liberties.countLiberties(xcoord, ycoord, newBoard, colour)
	print(f'Liberties of ({xcoord},{ycoord}): {liberties}.')
	return liberties

def playAndCapture(x, y, board, colourOnTurn):
	newBoard = [[c for c in row] for row in board]
	newBoard[y][x] = colourOnTurn
	capturedStones = []
	opponentAtari = False
	opponentColour = 'b' if colourOnTurn == 'w' else 'w'
	for (xadj, yadj) in ph_liberties.getAdjacentIter(x, y):
		if newBoard[yadj][xadj] == opponentColour:
			liberties = countLiberties(xadj, yadj, newBoard, opponentColour)
			if liberties == 0:
				ph_liberties.removeGroup(xadj, yadj, opponentColour, newBoard, capturedStones)
			elif liberties == 1:
				opponentAtari = True
	return capturedStones, newBoard, opponentAtari

def impossibleMoveOutput(xcoord, ycoord):
	outPlayer = 'Coup impossible.'
	return outPlayer, None, None

def normalMoveOutput(nbImpossibleMoves, board, colourOnTurn, numMove):
	colour = 'Noir' if colourOnTurn == 'b' else 'Blanc'
	outGlobal = f'Coup {numMove}: {colour} joue.'
	if nbImpossibleMoves == 1:
		outGlobal = outGlobal[:-1] + f' après {nbImpossibleMoves} coup impossible.'
	elif nbImpossibleMoves > 1:
		outGlobal = outGlobal[:-1] + f' après {nbImpossibleMoves} coups impossibles.'
	outPlayer = '\n\n' + ph_printboard.printOneSide(board, colourOnTurn, numMove)
	#outPlayer = None
	return outPlayer, outGlobal, None

def addOpponentCapturedStones(outPlayer, outGlobal, outOpponent, colourOnTurn, numMove, capturedStones):
	
	nbStones = len(capturedStones)
	if nbStones == 1:
		colour = 'blanche' if colourOnTurn == 'b' else 'noire'
		outGlobal = outGlobal[:-1] + f' et capture {nbStones} pierre {colour}.'
	else:
		colour = 'blanches' if colourOnTurn == 'b' else 'noires'
		outGlobal = outGlobal[:-1] + f' et capture {nbStones} pierres {colour}.'
	outOpponent = '\n\n' + ph_printboard.printCapturedStones(capturedStones, colourOnTurn, numMove)
	return outPlayer, outGlobal, outOpponent

def addOpponentAtari(outPlayer, outGlobal, outOpponent, colourOnTurn):
	colour = 'Blanc' if colourOnTurn == 'b' else 'Noir'
	outGlobal = outGlobal[:-1] + f" et met {colour} en atari."
	return outPlayer, outGlobal, outOpponent

def addSelfAtari(outPlayer, outGlobal, outOpponent):
	outGlobal = outGlobal[:-1] + f" et se met en atari."
	return outPlayer, outGlobal, outOpponent

def nextPlayer(colourOnTurn, white, black):
	if colourOnTurn == 'b':
		playerOnTurn = white
		playerNotOnTurn = black
		colourOnTurn = 'w'
	else:
		playerOnTurn = black
		playerNotOnTurn = white
		colourOnTurn = 'b'
	return playerOnTurn, playerNotOnTurn, colourOnTurn

class Game:
	def __init__(self, botstate, white, black, komi=None, handicap=0):
		self.white = white
		self.black = black
		self.komi = komi if komi else (7 if not handicap else 0)
		self.handicap = handicap
		self.playerOnTurn = black
		self.playerNotOnTurn = white
		self.colourOnTurn = 'b'
		self.numMove = 0
		self.lastPass = None
		#self.board = '.........\n.........\n.........\n.........\n.........\n.........\n.........\n.........\n.........\n'
		self.board = [['.' for x in range(9)] for y in range(9)]
		self.nbImpossibleMoves = 0
		botstate.game = self
		botstate.initBoardWhite = ph_printboard.printOneSide(self.board, 'w', 0)
		botstate.initBoardBlack = ph_printboard.printOneSide(self.board, 'b', 0)

	def playmove(self, botstate, xcoord, ycoord):
		if alreadyOccupied(xcoord, ycoord, self.board):
			outPlayer, outGlobal, outOpponent = impossibleMoveOutput(xcoord, ycoord)
			self.nbImpossibleMoves += 1
		else:
			capturedStones, newBoard, opponentAtari = playAndCapture(xcoord, ycoord, self.board, self.colourOnTurn)
			if len(capturedStones) > 0:
				print('captured some stones!!!!!!!!!!')
				print(f'captured {len(capturedStones)} stones')
				self.board = newBoard
			nbLiberties = virtualPlayAndCountLiberties(xcoord, ycoord, self.board, self.colourOnTurn)
			if nbLiberties == 0:
				outPlayer, outGlobal, outOpponent = impossibleMoveOutput(xcoord, ycoord)
				self.nbImpossibleMoves += 1
			else:
				self.board[ycoord][xcoord] = self.colourOnTurn
				self.numMove += 1
				outPlayer, outGlobal, outOpponent = normalMoveOutput(self.nbImpossibleMoves, self.board, self.colourOnTurn, self.numMove)
				if len(capturedStones) > 0:
					print('we are here and we printed this')
					outPlayer, outGlobal, outOpponent = addOpponentCapturedStones(outPlayer, outGlobal, outOpponent, self.colourOnTurn, self.numMove, capturedStones)
				if opponentAtari:
					outPlayer, outGlobal, outOpponent = addOpponentAtari(outPlayer, outGlobal, outOpponent, self.colourOnTurn)
				if nbLiberties == 1:
					outPlayer, outGlobal, outOpponent = addSelfAtari(outPlayer, outGlobal, outOpponent)
				self.playerOnTurn, self.playerNotOnTurn, self.colourOnTurn = nextPlayer(self.colourOnTurn, self.white, self.black)
				self.nbImpossibleMoves = 0

		return outPlayer, outGlobal, outOpponent

	def passmove(self, botstate):
		print('pass')
		self.numMove += 1
		self.playerOnTurn, self.playerNotOnTurn, self.colourOnTurn = nextPlayer(self.colourOnTurn, self.white, self.black)
		if self.lastPass == self.numMove - 1:
			botstate.endGame = ph_endgame.EndGame(self)
			botstate.game = None
			botstate.triggeredEndGame = True
		self.lastPass = self.numMove
		return (None, f'Coup {self.numMove}: {self.playerNotOnTurn.mention} passe.', None)

	def resign(self, botstate, resignedPlayer):
		print('resign')
		self.playerOnTurn = self.white if self.colourOnTurn == 'b' else self.black
		botstate.endGame = ph_endgame.EndGame(self)
		botstate.game = None
		botstate.triggeredEndGame = True
		return None, f'Abandon de {resignedPlayer.mention}', None