import os
import random
from dotenv import load_dotenv
from discord.ext import commands

import ph_botstate
import ph_game
import ph_printboard

load_dotenv()
TOKEN = os.getenv('DISCORD_TOKEN')

bot = commands.Bot(command_prefix='!')
botstate = ph_botstate.BotState()

@bot.event
async def on_ready():
    print(f'{bot.user.name} has connected to Discord!')

# @bot.event
# async def on_message(msg):
# 	if msg.author == bot.user:
# 		return
# 	if 'call me' in msg.content:
# 		await msg.channel.send(msg.author.mention)

def chooseWhiteAndBlackUsers(ctx):
	ll = ctx.message.mentions
	print(ll)
	if (len(ll) > 0):
		opponent = ll[0]
		challenger = ctx.author
		if 'white' in ctx.message.content:
			userWhite = challenger
			userBlack = opponent
		elif 'black' in ctx.message.content:
			userWhite = opponent
			userBlack = challenger
		else:
			ll = [opponent, challenger]
			random.shuffle(ll)
			userWhite, userBlack = ll
	else:
		userWhite = None
		userBlack = None
	return userWhite, userBlack

@bot.command(name='newgame', help='pseudo_blanc pseudo_noir [komi [handicap]]')
async def new_game(ctx, mentionOpponent):
	alreadyPlaying = (botstate.game is not None)
	userWhite, userBlack = chooseWhiteAndBlackUsers(ctx)
	#whiteOK = nameWhite in [user.name for user in ctx.guild.members]
	#blackOK = nameBlack in [user.name for user in ctx.guild.members]
	playerInPlayerList = ctx.author in [userWhite, userBlack]
	if alreadyPlaying:
		await ctx.send('Erreur: Il y a déjà une partie en cours.')
	elif userWhite and userBlack:
		ph_game.Game(botstate, userWhite, userBlack, komi=None, handicap=0)
		botstate.channel = ctx
		await userWhite.create_dm()
		await userBlack.create_dm()
		greetings = f'Nouvelle partie de go fantôme démarrée. \nBlanc: {userWhite.mention}. Noir: {userBlack.mention}.\n'
		await ctx.send(greetings)
		await userBlack.dm_channel.send(greetings)
		await userBlack.dm_channel.send(botstate.initBoardBlack)
		await userWhite.dm_channel.send(greetings)
		await userWhite.dm_channel.send(botstate.initBoardWhite)
	else:
		await ctx.send(f'Erreur: pas de joueur nommé {mentionOpponent}!')

async def checkPlayerOnMoveAndSendErrorMsg(ctx):
	playerIsPlaying = (ctx.author in [botstate.game.white, botstate.game.black])
	playerIsOnTurn = (ctx.author == botstate.game.playerOnTurn)
	if not playerIsPlaying:
		await ctx.send('Erreur: vous n\'êtes pas en train de jouer une partie!')
		return False
	elif not playerIsOnTurn:
		await ctx.send('Erreur: ce n\'est pas à vous de jouer!')
		return False
	else:
		return True

async def checkPlayerOnResignAndSendErrorMsg(ctx):
	playerIsPlaying = (ctx.author in [botstate.game.white, botstate.game.black])
	if not playerIsPlaying:
		await ctx.send('Erreur: vous n\'êtes pas en train de jouer une partie!')
		return False
	else:
		return True

def intersectionTextToNumbers(s):
	xcoord, ycoord = None, None
	if len(s) == 2:
		xcoord = ord(s[0].lower()) - ord('a')
		ycoord = ord(s[1]) - ord('1')
		if not (xcoord in range(9) and ycoord in range(9)):
			xcoord, ycoord = None, None
	return xcoord, ycoord

async def sendMessages(ctx, playerOutput, globalOutput, opponentOutput):
	opponent = botstate.game.playerOnTurn if botstate.game else botstate.endGame.playerOnTurn
	if globalOutput:
		await ctx.send(globalOutput)
		await botstate.channel.send(globalOutput)
		await opponent.dm_channel.send(globalOutput)
	if playerOutput:
		await ctx.send(playerOutput)
	if opponentOutput:
		await opponent.dm_channel.send(opponentOutput)

@bot.command(name='play', help='a1..i9')
async def play_move(ctx, intersection):
	playerIsOK = await checkPlayerOnMoveAndSendErrorMsg(ctx)
	if playerIsOK:
		xcoord, ycoord = intersectionTextToNumbers(intersection)
		if xcoord is None or ycoord is None:
			await ctx.send(f'Erreur: {intersection} n\'est pas une intersection valide. Intersections valides: de a1 jusqu\'à i9.')
		else:
			playerOutput, globalOutput, opponentOutput = botstate.game.playmove(botstate, xcoord, ycoord)
			await sendMessages(ctx, playerOutput, globalOutput, opponentOutput)

async def sendEndGameMessage(ctx, board, bothPlayersPassed = True):
	textBoard = ph_printboard.printBoard(board)
	await sendMessages(ctx, None, 'La partie est terminée.', None)
	await sendMessages(ctx, None, textBoard, None)
	if bothPlayersPassed:
		await sendMessages(ctx, None, 'Utiliser la commande !score pour retirer les pierres mortes et voir le résultat.', None)

@bot.command(name='pass', help='')
async def pass_move(ctx):
	playerIsOK = await checkPlayerOnMoveAndSendErrorMsg(ctx)
	if playerIsOK:
		playerOutput, globalOutput, opponentOutput = botstate.game.passmove(botstate)
		await sendMessages(ctx, playerOutput, globalOutput, opponentOutput)
		if botstate.triggeredEndGame:
			botstate.triggeredEndGame = False
			await sendEndGameMessage(ctx, botstate.endGame.board)

@bot.command(name='resign', help='')
async def resign(ctx):
	playerIsOK = await checkPlayerOnResignAndSendErrorMsg(ctx)
	if playerIsOK:
		playerOutput, globalOutput, opponentOutput = botstate.game.resign(botstate, ctx.author)
		await sendMessages(ctx, playerOutput, globalOutput, opponentOutput)
		if botstate.triggeredEndGame:
			botstate.triggeredEndGame = False
			await sendEndGameMessage(ctx, botstate.endGame.board, bothPlayersPassed = False)

@bot.command(name='score', help='list of dead groups')
async def kill_dead_groups_and_score(ctx, *deadStones):
	if botstate.endGame:
		botstate.endGame.removeDeadStones([intersectionTextToNumbers(s) for s in deadStones])
		await ctx.send(ph_printboard.printBoard(botstate.endGame.boardWithoutDeadStones, text='Plateau sans les pierres mortes:'))
		botstate.endGame.spreadTerritory()
		(whitePoints, blackPoints, damePoints) = botstate.endGame.countPoints()
		await ctx.send(f'Blanc: {whitePoints}; Noir: {blackPoints}; Dame: {damePoints}.')

bot.run(TOKEN)
