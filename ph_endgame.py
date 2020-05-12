def getAdjacentIter(x, y):
	return filter(
				(lambda coord: coord[0] >= 0 and coord[0] < 9 and coord[1] >= 0 and coord[1] < 9),
				[(x-1, y), (x, y-1), (x+1, y), (x, y+1)]
			)

class EndGame:
	def __init__(self, game):
		self.board = game.board
		self.komi = game.komi
		self.playerOnTurn = game.playerOnTurn
		self.boardWithoutDeadStones = [[c for c in row] for row in self.board]
		self.scoredBoard = [[c for c in row] for row in self.boardWithoutDeadStones]
		self.neutralIntersections = []

	def removeDeadStones(self, ll):
		self.boardWithoutDeadStones = [[c for c in row] for row in self.board]
		for x,y in ll:
			colour = self.boardWithoutDeadStones[y][x]
			self.boardWithoutDeadStones[y][x] = '.'
			toRemove = [(x,y)]
			while toRemove:
				xadj, yadj = toRemove.pop()
				if self.boardWithoutDeadStones[yadj][xadj] == colour:
					self.boardWithoutDeadStones[yadj][xadj] = '.'
					toRemove.extend(getAdjacentIter(xadj, yadj))
		print('Board without dead stones:')
		print(self.boardWithoutDeadStones)

# CONVENTIONS:
#	.	empty intersection
#	b	black stone
#	w	white stone
#	B	black territory
#	W	white territory
	def spreadTerritory(self):
		self.scoredBoard = [[c for c in row] for row in self.boardWithoutDeadStones]
		neutralIntersectionsToSpread = []
		# first stread territory ownership from alive stones and note conflicts in neutralIntersectionsToSpread
		for y in range(9):
			for x in range(9):
				colour = self.scoredBoard[y][x]
				if colour in ['b', 'w']:
					owned = colour.upper()
					unfriendlies = ['b', 'B'] if colour == 'w' else ['w', 'W']
					toSpread = list(getAdjacentIter(x, y))
					while toSpread:
						xadj, yadj = toSpread.pop()
						if self.scoredBoard[yadj][xadj] == '.':
							self.scoredBoard[yadj][xadj] = owned
							toSpread.extend(getAdjacentIter(xadj, yadj))
						elif self.scoredBoard[yadj][xadj] in unfriendlies:
							neutralIntersectionsToSpread.extend([(x,y), (xadj, yadj)])
		# then mark as neutral territories (ie, seki or unplayed dame) all conflicted territories
		for (x, y) in neutralIntersectionsToSpread:
			colourToDestroy = self.scoredBoard[y][x]
			if colourToDestroy in ['B', 'W']:
				toDestroy = [(x,y)]
				while toDestroy:
					xadj, yadj = toDestroy.pop()
					if self.scoredBoard[yadj][xadj] == colourToDestroy:
						self.scoredBoard[yadj][xadj] = '.'
						toDestroy.extend(getAdjacentIter(xadj, yadj))
		print('Board with territory ownership:')
		print(self.scoredBoard)

	def countPoints(self):
		whitePoints = self.komi
		blackPoints = 0
		damePoints = 0
		for y in range(9):
			for x in range(9):
				if self.scoredBoard[y][x] in ['w', 'W']:
					whitePoints += 1
				elif self.scoredBoard[y][x] in ['b', 'B']:
					blackPoints += 1
				elif self.scoredBoard[y][x] == '.':
					damePoints += 1
				else:
					print('This intersection is neither white nor black nor neutrallllllll:')
					print(f'    ({x},{y}) [{self.scoredBoard[y][x]}]')
		print('Décompte des points:')
		print(f'    Blanc   [{whitePoints}]')
		print(f'    Noir    [{blackPoints}]')
		print(f'    Dame    [{damePoints}]')
		print(f'    Total   [{whitePoints + blackPoints + damePoints}] (should be {9*9+self.komi})')
		return (whitePoints, blackPoints, damePoints)



