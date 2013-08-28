from EventManager import *

import pygame
from pygame.locals import *

class KeyboardController(object):
	"""Takes input from the keboard and translates that into game Events to trigger action
		in the rest of the system"""
	STATE_ACTION = 0
	STATE_SOLVE = 1
	STATE_VICTORY = 2
	
	def __init__(self):
		self.evManager = EventManager()
		self.evManager.RegisterListener( self )
		self.state = KeyboardController.STATE_ACTION
		self.solution = ""
		self.solveTime = 0

	def Notify(self, event):
		"""Takes mostly keyboard inputs and generates events based on state.
		STATE_ACTION: Generic state -- basically just waiting for player to attack
			RequestSolutionEvent:
				Change state to STATE_SOLVE
			TickEvent:
				Check to see if game is quit or attack is requested based on key presses
		STATE_VICTORY: Player has defeated all enemies (waiting for next battle)
		STATE_SOLVE: Player has attacked, and is in the process of entering the solution
			SolveEvent:
				Attack has completed, change state back to STATE_ACTION and reset solution
			TickEvent:
				Listen for any key presses (quit, numbers, delete, submit) and update appropriately
		"""
		events = [] #events to be raised at the end if necessary
		
		#always quit (regardless of state)
		if isinstance(event, TickEvent):
			pgEventList = pygame.event.get()
			for pgEvent in pgEventList:
				if pgEvent.type == QUIT:
					events.append(QuitEvent())
				elif pgEvent.type == KEYDOWN:
					if pgEvent.key == K_ESCAPE:
						events.append(QuitEvent())
		#always switch to victory state (regardless of current state)
		elif isinstance(event, VictoryEvent):
			print "controller victory"
			self.state = KeyboardController.STATE_VICTORY
		
		if self.state == KeyboardController.STATE_ACTION:
			if isinstance(event, RequestSolutionEvent):
				self.state = KeyboardController.STATE_SOLVE
			elif isinstance(event, TickEvent):
				#Handle Input Events
				for pgEvent in pgEventList:
					if pgEvent.type == KEYDOWN:
						if pgEvent.key == K_SPACE:
							events.append(RequestAttackEvent())
		
		elif self.state == KeyboardController.STATE_SOLVE:
			if isinstance(event, SolveEvent):
				self.state = KeyboardController.STATE_ACTION
				self.solution = ""
			elif isinstance(event, TickEvent):
				for pgEvent in pgEventList:
					if pgEvent.type == KEYDOWN:
						if pgEvent.unicode in u'0123456789': #typed a digit
							self.solution += pgEvent.unicode
							events.append(SolutionUpdateEvent(self.solution))
						elif pgEvent.key == K_BACKSPACE:
							self.solution = self.solution[:-1]
							events.append(SolutionUpdateEvent(self.solution))
						elif pgEvent.key in (K_RETURN, K_KP_ENTER):
							events.append(SolveEvent(self.solution))
		
		elif self.state == KeyboardController.STATE_VICTORY:
			if isinstance(event, TickEvent):
				for pgEvent in pgEventList:
					if pgEvent.type == KEYDOWN:
						if pgEvent.key == K_SPACE:
							events.append(NextBattleEvent())
							self.state = KeyboardController.STATE_ACTION
		for ev in events:
			self.evManager.Notify( ev )

class CPUSpinnerController(object):
	"""Controls the game clock -- generating an Event for each game tick, and throttling
		the game to limit CPU usage"""
	def __init__(self, maxfps=40):
		self.evManager = EventManager()
		self.evManager.RegisterListener( self )

		self.keepGoing = 1
		self.clock = pygame.time.Clock()
		self.maxfps = maxfps

	def Run(self):
		"""Start the game by telling the game clock to go!"""
		while self.keepGoing:
			event = TickEvent(pygame.time.get_ticks(), self.clock.tick(self.maxfps))
			self.evManager.Notify( event )

	def Notify(self, event):
		"""handled events:
		Quit Event:
			Stop the clock from ticking (the app will then close)
		"""
		if isinstance(event, QuitEvent):
			#this will stop the while loop from running
			self.keepGoing = 0