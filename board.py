from random import randrange, shuffle
import datetime
import time

board = [
	'go', 'mediterranean ave',  'community chest1', 'baltic ave', 'income tax', 'reading railroad', 'oriental ave', 'chance1', 'vermont ave', 'connecticut ave',
	'jail/just visiting', 'st charles place', 'electric company', 'states ave', 'virginia ave', 'pennsylvania railroad', 'st james place', 'community chest2', 'tennessee ave', 'new york ave',
	'free parking', 'kentucky ave', 'chance2', 'indiana ave', 'illinois ave', 'b&o railroad', 'atlantic ave', 'ventnor ave', 'water works', 'marvin gardens',
	'go to jail', 'pacific ave', 'north carolina ave', 'community chest3', 'pennsylvania ave', 'short line', 'chance3', 'park place', 'luxury tax', 'boardwalk'
]
communityChest = [
	'go to jail', 'inherit $100', 'street repairs', 'second place in beauty contest', 'life insurance matures', 'xmas fund matures',
	'receive for services', 'pay school tax', 'from sale of stock', 'pay hospital', 'income tax refund', 'collect $50 from every player',
	'doctor\'s fee', 'bank error in your favor', 'advance to go', 'get out of jail free'
]
chance = [
	'advance to illinois ave', 'general repairs', 'elected chairman', 'get out of jail free', 'go back 3 spaces', 'go to jail', 'pay poor tax',
	'go to reading railroad', 'advance to nearest utility', 'building and loan matures', 'advance to go', 'advance to nearest railroad',
	'advance to boardwalk', 'bank dividend', 'advance to nearest railroad', 'advance to st charles place'
]

currentChance = []
currentCommunityChest = []

def drawCard(originalBag, currentBag):
	if len(currentBag) == 0:
		# Reshuffle, copy array first
		currentBag = originalBag[:]
		for i in range(3): shuffle(currentBag)
		
	return currentBag.append(currentBag.pop(0))
	#return currentBag.pop(0)

def drawCommunityChest():
	global currentCommunityChest
	return drawCard(communityChest, currentCommunityChest)

def drawChance():
	global currentChance
	return drawCard(chance, currentChance)

def roll():
	sides = 6
	num = 1
	return sum(randrange(sides) + 1 for die in range(num))

def timestamp():
	return datetime.datetime.fromtimestamp(time.time()).strftime('%Y-%m-%d %H:%M:%S')

boardSize = len(board)
boardIndexSize = boardSize - 1
jailPos = board.index('jail/just visiting')
totalRolls = 6000000
updateInterval = totalRolls // 10

class Player:
	def __init__(self):
		self._pos = 0
		self._positionsHit = {}
		for i in range(boardSize):
			self._positionsHit[i] = 0
		self._doublesTurns = 0
		self._jailed = False
		self._jailedTurns = 0
		self._turns = 0

	def processRoll(self):
		self._turns += 1
		rollAgain = False
		die1 = roll()
		die2 = roll()

		if die1 == die2:
			if self._jailed:
				self._jailed = False
				self._pos += die1 + die2
				self._jailedTurns = 0
			elif self._doublesTurns == 2:
				self._pos = jailPos
				self._jailed = True
				self._doublesTurns = 0
			else:
				self._pos += die1 + die2
				self._doublesTurns += 1
				rollAgain = True
		elif self._jailed:
			if self._jailedTurns == 2:
				# Has to pay to get out
				self._jailed = False
				self._pos += die1 + die2
				self._jailedTurns = 0
			else: self._jailedTurns += 1
		else: self._pos += die1 + die2
		if self._pos > boardIndexSize: self._pos -= boardSize

		if board[self._pos] == 'go to jail':
			self._pos = jailPos
			self._jailed = True
		elif board[self._pos] in ['chance1', 'chance2', 'chance3']:
			card = drawChance()
			if card == 'advance to go': self._pos = 0
			elif card == 'go to jail':
				self._pos = jailPos
				self._jailed = True
			elif card == 'go back 3 spaces':
				self._pos -= 3
				if self._pos < 0: self._pos += boardSize
			elif card == 'advance to st charles place': self._pos = board.index('st charles place')
			elif card == 'advance to boardwalk': self._pos = board.index('boardwalk')
			elif card == 'advance to illinois ave': self._pos = board.index('illinois ave')
			elif card == 'go to reading railroad': self._pos = board.index('reading railroad')
			elif card == 'advance to nearest railroad':
				newPos = self._pos
				# Can't advance to a spot you're on
				if board[newPos] in ['short line', 'b&o railroad', 'pennsylvania railroad', 'reading railroad']: newPos += 1
				while board[newPos] not in ['short line', 'b&o railroad', 'pennsylvania railroad', 'reading railroad']:
					newPos += 1
					if newPos > boardIndexSize: newPos -= boardSize
				self._pos = newPos
			elif card == 'advance to nearest utility':
				newPos = self._pos
				# Can't advance to a spot you're on
				if board[newPos] in ['electric company', 'water works']: newPos += 1
				while board[newPos] not in ['electric company', 'water works']:
					newPos += 1
					if newPos > boardIndexSize: newPos -= boardSize
				self._pos = newPos
		elif board[self._pos] in ['community chest1', 'community chest2', 'community chest3']:
			card = drawCommunityChest()
			if card == 'advance to go': self._pos = 0
			elif card == 'go to jail':
				self._pos = jailPos
				self._jailed = True

		self._positionsHit[self._pos] += 1
		return rollAgain

	def positionsHit(self):
		return self._positionsHit
		
	def turns(self):
		return self._turns

	def __str__(self):
		return '{\n' + '\n'.join(['   {}: {}'.format(board[key], round(self._positionsHit[key] / self._turns * 100, 2)) for key in sorted(self._positionsHit, key = self._positionsHit.get)]) + '\n}'

players = [Player(), Player()]

for i in range(totalRolls):
	if (i % updateInterval) == 0: print('[{}] {}/{}'.format(timestamp(), i, totalRolls))

	player = players.pop(0)

	if not player.processRoll():
		players.append(player)
	else:
		players.insert(0, player)

# Summarize player totals
finalTally = {}
finalTurns = 0
for i in range(len(players)):
	player = players[i]
	positionsHit = player.positionsHit()
	for key in sorted(positionsHit, key = positionsHit.get):
		if key not in finalTally: finalTally[key] = 0
		finalTally[key] += positionsHit[key]
	
	finalTurns += player.turns()
	print('Player {}: {}'.format(i, player))

print('Player Summary: {{\n{}\n}}'.format('\n'.join(['   {}: {}'.format(board[key], round(finalTally[key] / finalTurns * 100, 2)) for key in sorted(finalTally, key = finalTally.get)])))
