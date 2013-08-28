from EventManager import *
from problem import *
from actor import *

import random
import locale

class Game(object):
    """Responsible for setting the stage:
    Namely, making sure that the appropriate Actors exist and know the appropriate things
    """
    __metaclass__ = SingletonType

    STATE_PREPARING = 0
    STATE_RUNNING = 1
    STATE_PAUSED = 2
    STATE_GAMEOVER = 3

    def __init__(self):
        self.evManager = EventManager()
        self.evManager.RegisterListener( self )

        self.state = Game.STATE_PREPARING
        self.heroes = {}
        self.enemies = {}
        self.enemyCount = 0
        self.problem = (0,0)
        self.time = 0
        self.solutionWait = 5000 #milliseconds
        self.solEndTime = 0

    def Start(self):
        """starts the game action -- spawning any Actors needed, setting required variables
            and generating the GameStartedEvent"""
        self.SpawnHero()
        self.SpawnEnemy()
            
        self.state = Game.STATE_RUNNING
        self.evManager.Notify(GameStartedEvent(self))

    def SpawnHero(self):
        self.heroes["hero"] = HeroModel("hero", self.enemies)
        self.evManager.Notify(SpawnHeroEvent(self.heroes["hero"].evID))
    
    def SpawnEnemy(self):
        self.enemyCount += 1
        enemyID = "enemy%s" % self.enemyCount
        self.enemies[enemyID] = EnemyModel(enemyID, self.heroes, self.time)
        self.evManager.Notify(SpawnEnemyEvent(enemyID))
    
    def myOpponents(self, actor):
        if isinstance(actor, Hero):
            return self.enemies
        elif isinstance(actor, Enemy):
            return self.heroes
    
    def Notify(self, event):
        """Handled events:
        TickEvent:
            progress the game action by one game tick (currently just starts game
                if it's not already set up)
        DieEvent:
            Actor has died.  If hero, game is over, if (last) enemy, victory is achieved
        NextBattleEvent:
            Player has requested next battle, so spawn an enemy
        """
        if self.state == Game.STATE_GAMEOVER:
            return #don't do anything if the game is over
        elif self.state == Game.STATE_PREPARING:
            if isinstance( event, TickEvent ):
                self.Start()
        
        if isinstance( event, TickEvent ):
            self.time = event.time
            
        if self.state == Game.STATE_RUNNING:
            if isinstance(event, DieEvent):
                if event.subject in self.heroes.keys():
                    self.state = Game.STATE_GAMEOVER
                    self.evManager.Notify(GameOverEvent())
                    #del self.heroes[event.subject]
                elif event.subject in self.enemies.keys():
                    self.evManager.Notify(VictoryEvent())
                    del self.enemies[event.subject]
            elif isinstance(event, NextBattleEvent):
                self.SpawnEnemy()