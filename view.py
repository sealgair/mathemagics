from EventManager import *

import pygame
from pygame.locals import *

class PygameView:
	"""Creates the game window, and handles drawing everything inside it"""
	def __init__(self):
		self.evManager = EventManager()
		self.evManager.RegisterListener(self)

		#set up pygame requriements
		pygame.init()
		self.window = pygame.display.set_mode( (640,480) )
		pygame.display.set_caption('Mathemagics')
		self.background = pygame.Surface(self.window.get_size())
		self.background.fill( (0,0,0) )

		self.backSprites = pygame.sprite.RenderUpdates()
		self.menuSprites = pygame.sprite.RenderUpdates()
		self.actorSprites = pygame.sprite.RenderUpdates()
		
		self.mapspr = MapSprite(self.window.get_rect(), self.backSprites)
		self.hud = HUD(self.window.get_rect(), self.menuSprites)

	def SpawnHero(self, evID):
		x = self.window.get_width()/4
		y = self.window.get_height()/3
		hero = HeroSprite(x, y, evID, self.actorSprites)
	
	def SpawnEnemy(self, evID):
		x = self.window.get_width()*3/4
		y = self.window.get_height()/3
		enemy = EnemySprite(x, y, evID, self.actorSprites)
	
	def GetActor(self, evID):
		for sprite in self.actorSprites.sprites():
			if sprite.evID == evID: return sprite
	
	def Notify(self, event):
		"""Handled events:
		TickEvent:
			redraw back & front sprites using double buffering
		DieEvent:
		SpawnEvent:
			Create the spawned actor
		"""
		if isinstance( event, TickEvent ):
			#Draw Everything
			self.backSprites.clear(self.window, self.background)
			self.menuSprites.clear(self.window, self.background)
			self.actorSprites.clear(self.window, self.background)

			self.backSprites.update()
			self.menuSprites.update()
			self.actorSprites.update()
			
			dirtyRects1 = self.backSprites.draw(self.window)
			dirtyRects2 = self.menuSprites.draw(self.window)
			dirtyRects3 = self.actorSprites.draw(self.window)

			pygame.display.update(dirtyRects1 + dirtyRects2 + dirtyRects3)
		
		#..should go to HUD?
		elif isinstance(event, DieEvent):
			subject = self.GetActor(event.subject)
			if subject.evID == 'hero': self.hud.Defeat() #placeholder
			else: self.hud.Victory()
		
		elif isinstance(event, SpawnEvent):
			if isinstance(event, SpawnHeroEvent): self.SpawnHero(event.evID)
			if isinstance(event, SpawnEnemyEvent): self.SpawnEnemy(event.evID)

class HUD(pygame.sprite.Sprite):
	"""Handles drawing any displayed info, namely:
		* text for the problem, solution, and any other messages
		* timer bar for problem
		* the lines separating the screens
	"""
	def __init__(self, rect, group=None):
		pygame.sprite.Sprite.__init__(self, group)
		self.evManager = EventManager()
		self.evManager.RegisterListener(self)
		
		self.time = 0
		
		#self.image = pygame.Surface(rect.size, SRCALPHA)
		self.image = pygame.Surface(rect.size)
		self.image.set_colorkey((0,0,0))
		self.image.fill((0,0,0,0))
		self.color = (255,255,255)
		self.rect = self.image.get_rect()
		
		self.hero = None
		
		#set hud areas
		w = rect.width
		h = rect.height
		self.heroBox = self.image.subsurface((0,0, w/2,h*2/3)) #top left box
		#pygame.draw.rect(self.heroBox, self.color, self.heroBox.get_rect(), 4)
		self.DrawBorder(self.heroBox)
		
		self.enemyBox = self.image.subsurface((w/2,0, w/2,h*2/3)) #top right box
		#pygame.draw.rect(self.enemyBox, self.color, self.enemyBox.get_rect(), 4)
		self.DrawBorder(self.enemyBox)
		
		self.dataBox = self.image.subsurface((0,h*2/3, w,h/3))
		#pygame.draw.rect(self.dataBox, self.color, self.dataBox.get_rect(), 4)
		self.DrawBorder(self.dataBox)
		
		self.solutionBox = self.dataBox.subsurface((50,50, 100,50))
		self.timerBox = self.dataBox.subsurface((30,100, 300,20))
		self.timer = (0,0) #beginning and end of timer
		
		self.instrBox = self.dataBox.subsurface((200, 20, w/2, 100))
		
		#set hud font
		self.font = pygame.font.SysFont("Arial", 18)
		self.font_height = 20
		
		#initialize instruction text:
		self.instr_wait = "Press SPACE to attack"
		self.instr_prob = "%s \nType solution and press ENTER to solve"
		self.instr_win = "Victory! \nPress SPACE for next battle"
		self.instr_loose = "Game Over! \nPress ESC to quit"
		self.instr = self.instr_wait
		self.sol = ""
	
	def DrawBorder(self, surf):
		surf.fill(self.color)
		rect = surf.get_rect().inflate(-4,-4)
		surf.fill((200,200,200,127), rect)
		rect = rect.inflate(-4,-4)
		surf.fill((0,0,0), rect)
		return rect
	
	def Victory(self):
		self.instr = self.instr_win
	
	def Defeat(self):
		self.instr = self.instr_loose
	
	def DrawInstructions(self, color = False):
		if not color: color = self.color
		vpos = 0
		self.instrBox.fill((0,0,0))
		for text in self.instr.split('\n'):
			pImg = self.font.render(text, False, color)
			self.instrBox.blit(pImg, (0,vpos))
			vpos += self.font_height
	
	def DrawSolution(self, color = False):
		if not color: color = self.color
		sImg = self.font.render(self.sol, False, color)
		self.solutionBox.fill((0,0,0))
		self.solutionBox.blit(sImg, (0,0))
	
	def UpdateTimer(self):
		#rect = self.DrawBorder(self.timerBox)
		rect = self.timerBox.get_rect()
		w = rect.width
		p = 1.*(self.timer[1]-self.time)/(self.timer[1]-self.timer[0])
		w = w*p
		rect = (0,0, w,rect.height)
		self.timerBox.fill((0,0,0))
		self.timerBox.fill(self.color, rect)
	
	def Notify(self, event):
		"""events handled:
		TickEvent:
			shrink the timer (if we're counting)
		RequestSolutionEvent:
			display the problem & timer
		SolutionUpdateEvent:
			update the solution to the current state
		SolveEvent:
			Hide problem & timer
		"""
		if isinstance(event, TickEvent):
			self.time = event.time
			self.DrawInstructions()
			self.DrawSolution()
			if self.time < self.timer[1]: #timer on
				self.UpdateTimer()
		elif isinstance(event, SpawnHeroEvent):
			self.hero = event.evID
		elif isinstance(event, RequestSolutionEvent):
			self.instr = self.instr_prob % event.problem
			self.timer = (self.time, event.endTime)
		elif isinstance(event, SolutionUpdateEvent):
			self.sol = event.solution
		elif isinstance(event, SolveEvent):
			self.sol = ""
			self.instr = self.instr_wait
			self.timer = (0,0)
			self.timerBox.fill((0,0,0))
		elif isinstance(event, VictoryEvent):
			self.instr = self.instr_win
		elif isinstance(event, NextBattleEvent):
			self.instr = self.instr_wait

class ActorSprite(pygame.sprite.Sprite):
	""" Virtual sprite for a generic game actor
		subclasses must define the following:
			self.waitImage
			self.attackImage
			self.defendImage
			self.hurtImage
	"""
	def __init__(self, x, y, evID, group=None):
		self.evManager = EventManager()
		self.evManager.RegisterListener( self )
		
		pygame.sprite.Sprite.__init__(self, group)
		
		self.evID = evID
		
		self.pos = (x,y)
		self.InitImages()
		
		self.image = self.waitImage #start out waiting
		
		self.rect  = self.image.get_rect()
		self.rect.center = self.pos
		
		self.healthBox = pygame.Surface((self.rect.width,15))
		self.healthBox.fill((0,255,0))
		#self.healthBox.set_colorkey((0,0,0))
	
	def InitImages(self):
		# predefine images
		self.deadImage = pygame.Surface((0,0))
		self.waitImage = pygame.Surface((64,64)) #Idle image
		self.attackImage = pygame.Surface((64,64)) #Attack image
		self.defendImage = pygame.Surface((64,64)) #Defend image
		self.hurtImage = pygame.Surface((64,64)) #Hurt image
	
	def update(self):
		pygame.sprite.Sprite.update(self)
		self.image.blit(self.healthBox, (0,0))
	
	def UpdateHealth(self, newHealth):
		y = self.healthBox.get_rect().height
		x = self.healthBox.get_rect().width
		dx = x*newHealth
		grey = 255*newHealth
		r = min((255-grey)*2, 255)
		g = min(grey*2, 255)
		b = 0
		
		self.healthBox.fill((0,0,0))
		self.healthBox.fill((r,g,b), (0,0, dx,y))
	
	def Wait(self):
		#if self.image == self.attackImage:
		self.image = self.waitImage
		self.rect  = self.image.get_rect()
		self.rect.center = self.pos
	
	def Attack(self):
		if self.image == self.waitImage:
			self.image = self.attackImage
			self.rect  = self.image.get_rect()
			self.rect.center = self.pos
	
	def Defend(self):
		if self.image == self.waitImage:
			self.image = self.defendImage
			self.rect  = self.image.get_rect()
			self.rect.center = self.pos
	
	def Hurt(self, newHealth):
		self.UpdateHealth(newHealth)
		self.image = self.hurtImage
		self.rect  = self.image.get_rect()
		self.rect.center = self.pos
	
	def Die(self):
		self.image = self.deadImage
	
	#todo: actor objects should only get notifications for themselves (and maybe clock tick events)
	def Notify(self, event):
		"""handled events:
		WaitEvent:
			Display Wait
		AttackEvent:
			Display Attack
		Defend:
			Display Defend
		HurtEvent:
			Dislpay Hurt
		DieEvent:
			Display Die
		"""
		if isinstance(event, ActorStateChangeEvent) and self.evID == event.subject:
			if isinstance(event, WaitEvent): self.Wait()
			elif isinstance(event, AttackEvent): self.Attack()
			elif isinstance(event, DefendEvent): self.Defend()
			elif isinstance(event, HurtEvent): self.Hurt(event.newHealth)
			elif isinstance(event, DieEvent): 
				self.Die()
	
class HeroSprite(ActorSprite):
	"""Knows how to draw a hero (images or circles)
	can eventually be just images -- and then wrapped into ActorSprite class with 
	special code to map images to a directory based on constructor params
	"""
	def __init__(self, x, y, evID, group=None):
		ActorSprite.__init__(self, x, y, evID, group)
	
	def InitImages(self):
		# define images
		ActorSprite.InitImages(self)
		
		extended = pygame.image.get_extended()
		if extended:
			self.waitImage = pygame.image.load("images/wait.png")
			self.attackImage = pygame.image.load("images/attack.png")
			self.defendImage = pygame.image.load("images/defend.png")
			self.hurtImage = pygame.image.load("images/hurt.png")
		else:
			self.waitImage.set_colorkey((0,0,0)) #Idle image
			pygame.draw.circle(self.waitImage, (255,0,0), (32,32), 32)
			self.attackImage.set_colorkey((0,0,0)) #Attack image
			pygame.draw.circle(self.attackImage, (0,0,255), (32,32), 32)
			self.defendImage.set_colorkey((0,0,0)) #Defend image
			pygame.draw.circle(self.defendImage, (100,100,100), (32,32), 32)
			self.hurtImage.set_colorkey((0,0,0)) #Hurt image
			pygame.draw.circle(self.hurtImage, (100,100,100), (32,32), 32)

class EnemySprite(ActorSprite):
	"""Knows how to draw an enemy (squares)
	can eventually be just images -- and then wrapped into ActorSprite class with 
	special code to map images to a directory based on constructor params
	"""
	def __init__(self, x, y, evID, group=None):
		ActorSprite.__init__(self, x, y, evID, group)
	
	def InitImages(self):
		# define images
		ActorSprite.InitImages(self)
		
		self.waitImage.fill((127,127,127)) #Idle image
		self.attackImage.fill((255,0,0)) #Attack image
		self.defendImage.fill((0,0,255)) #Defend image
		self.hurtImage.fill((255,0,255))

class MapSprite(pygame.sprite.Sprite):
	"""Displays the background map"""
	def __init__(self, rect, group=None):
		pygame.sprite.Sprite.__init__(self, group)
		self.image = pygame.image.load("images/bg.png")
		self.rect = self.image.get_rect()