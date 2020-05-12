class BotState:
	def __init__(self):
		self.game = None
		self.channel = None
		self.initBoardBlack = None
		self.initBoardWhite = None
		self.endgame = None
		self.triggeredEndGame = False