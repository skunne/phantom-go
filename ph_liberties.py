# CONVENTIONS:
#	.	empty intersection
#	b	black stone
#	w	white stone
#	%	already visited intersection


def getAdjacentIter(x, y):
	return filter(
				(lambda coord: coord[0] >= 0 and coord[0] < 9 and coord[1] >= 0 and coord[1] < 9),
				[(x-1, y), (x, y-1), (x+1, y), (x, y+1)]
			)


def countLiberties(x, y, newboard, colour):
	#print(newboard)
	if newboard[y][x] == '.':			# if empty intersection
		newboard[y][x] = '%'			#     erase liberty because we counted it once
		liberties = 1							#     add 1 liberty
		#print(f'  + 1   ({x},{y})')
	elif newboard[y][x] == colour:	# if still in the group of stones
		newboard[y][x] = '%'			#     erase stone to avoid cycles
		adjacent_iter = getAdjacentIter(x, y)
		#print(f'  + ?   ({x},{y})')
		liberties = 0
		for (xadj,yadj) in adjacent_iter:
			liberties += countLiberties(xadj, yadj, newboard, colour)
	else:										# if opponent stone or already counted
		liberties = 0
		#print(f'  + 0   ({x},{y})')
	return liberties

def removeGroup(x, y, colour, board, capturedStones):
	if board[y][x] == colour:
		board[y][x] = '.'
		capturedStones.append((x,y))
		for (xadj, yadj) in getAdjacentIter(x, y):
			removeGroup(xadj, yadj, colour, board, capturedStones)

