from EventManager import *
from problem import *

import random
import locale

class ActorModel(object):
    """Generic class for anything 'alive' -- namely anything that can be involved in combat
    Tracks the following data:
        * Current state of Actor (Waiting, Attacking, Defending, Hurting or Dead)
        * The amount of time that should be spent in the various states
        * The current and maximum amount of health the Actor has
    """
    STATE_WAITING = 0
    STATE_ATTACKING = 1
    STATE_DEFENDING = 2
    STATE_HURTING = 3
    STATE_DEAD = 4

    def __init__(self, evID, opponents):
        self.evManager = EventManager()
        self.evManager.RegisterListener( self )
        self.evID = evID
        self.opponents = opponents
        self.victim = None
        
        self.state = ActorModel.STATE_WAITING
        
        self.AttackWait = 300 #milliseconds
        self.HurtWait = 200 #milliseconds
        self.time = 0
        self.AttackEndTime = self.time
        self.HurtEndTime = self.time
        
        self.maxHealth = 100
        self.health = self.maxHealth
        
        self.attackPower = 0 # to be defined in subclasses
    
    def Wait(self):
        """Sets Actor's current state to waiting (neutral)"""
        self.state = ActorModel.STATE_WAITING
        event = WaitEvent(self.evID)
        self.evManager.Notify(event)
    
    def nextVictim(self):
        """Determines next victim from list of known opponents"""
        victims = self.opponents.keys()
        Debug("available victims: %s" % victims, 5)
        if len(victims) == 0 or self.victim not in victims:
            self.victim = None
        for a in (1,2): #search list twice to wrap, since current victim might be last opponent in list
            for v in victims:
                if self.victim == None:
                    self.victim = v
                    return
                if v == self.victim:
                    self.victim = None #will set victim and return on next go-round
    
    def Attack(self, damage):
        """Sets Actor's current state to attacking -- and hurts victim based on given damage value"""
        if self.state == ActorModel.STATE_WAITING:
            self.state = ActorModel.STATE_ATTACKING
            self.AttackEndTime = self.time+self.AttackWait
            
            self.nextVictim() #currently there is no targeting system -- so just pick the next opponent in line
            Debug("victim %s has been chosen" % self.victim, 5)
            event = AttackEvent(self.evID, self.victim, damage)
            self.evManager.Notify(event)
    
    def Defend(self):
        """Sets Actor's current state do defending (not yet used)"""
        if self.state == ActorModel.STATE_WAITING:
            self.state = ActorModel.STATE_DEFENDING
            event = DefendEvent(self.evID)
            self.evManager.Notify(event)
    
    def Hurt(self, damage):
        """Sets Actors current state to hurting and deducts damage from health"""
        self.state = ActorModel.STATE_HURTING
        self.HurtEndTime = self.time+self.HurtWait
        
        if self.health >= 0:
            self.health -= damage
        if self.health < 0:
            self.health = 0
        
        event = HurtEvent(self.evID, 1.0*self.health/self.maxHealth)
        self.evManager.Notify(event)
        
        if self.health == 0:
            self.Die()
    
    def Die(self):
        """Sets Actor's current state to dead"""
        self.state = ActorModel.STATE_DEAD
        
        event = DieEvent(self.evID)
        self.evManager.Notify(event)
        self.evManager.UnregisterListener(self)
    
    def Notify(self, event):
        """Handles the following events:
        TickEvent:
            verify whether actor is currently still attacking or hurting based on 
                duration values for these states
        HurtEvent:
            if this actor is being attacked, call hurt
        """
        if isinstance(event, TickEvent):
            self.time = event.time
            #ready to stop attacking
            if self.state == ActorModel.STATE_ATTACKING and self.AttackEndTime <= self.time:
                self.Wait()
            if self.state == ActorModel.STATE_HURTING and self.HurtEndTime <= self.time:
                self.Wait()
        elif isinstance(event, AttackEvent) and event.object == self.evID:
            self.Hurt(event.damage)

class HeroModel(ActorModel):
    """Hero class is responsible for hero logic:
        * sending attack & solution events
        * managing countdown timer
        * creating a new problem for each attack
        * verifying that a problem is solved
        etc.
    Tracks the following data:
        * current problem being solved
        * amount of time left to solve current problem
    """ 
    def __init__(self, evID, opponents):
        ActorModel.__init__(self, evID, opponents)
        self.solutionWait = 5000 #miliseconds
        self.solEndTime = 0
        self.problem = None
    
    def Notify(self, event):
        """Handled events:
        TickEvent:
            Make sure countdown timer hasn't reached zero (if applicable)
        RequestAttackEvent:
            Initiate a new attack
        SolveEvent:
            Solultion entered: Calculate damage and apply it appropriately
        """
        ActorModel.Notify(self, event)
        
        if isinstance(event, TickEvent):
            #deal with solution timeout
            if self.solEndTime != 0 and self.time > self.solEndTime:
                self.solEndTime = self.time #so that dmgOffset doesn't go negative
                self.evManager.Notify(SolveEvent('-1')) #always wrong answer
        elif isinstance(event, RequestAttackEvent):
            self.problem = MultiplicationProblem()
            prob = unicode(self.problem)
            self.solEndTime = self.time+self.solutionWait
            self.evManager.Notify(RequestSolutionEvent(prob, self.solEndTime))
        elif isinstance(event, SolveEvent):
            dmgOffset = 1.0*(self.solEndTime-self.time)/self.solutionWait
            Debug("Damage Offset: %s" % dmgOffset, 2)
            if event.solution.isdigit() and self.problem.solve(locale.atoi(event.solution)):
                self.Attack(60*dmgOffset)
            else:
                self.Hurt(10+20*dmgOffset)
            self.solEndTime = 0

class EnemyModel(ActorModel):
    """Enemy class is responsible for enemy logic:
        * At this point, this is limited to attacking at random intervals
    Tracks the following data:
        * amount of time until next attack
    """
    def __init__(self, evID, opponents, gameTime):
        ActorModel.__init__(self, evID, opponents)
        self.time = gameTime
        self.attackWait = 10000 #milliseconds
        self.nextAttack = self.time + random.randint(self.attackWait/2, self.attackWait)

    def Notify(self, event):
        ActorModel.Notify(self, event)
        if isinstance(event, TickEvent):
            if self.time > self.nextAttack  and self.state == self.STATE_WAITING:
                self.Attack(10)
    
    def Attack(self, damage):
        ActorModel.Attack(self, damage)
        self.nextAttack += random.randint(self.attackWait/2, self.attackWait)        
    
    def Hurt(self, damage):
        ActorModel.Hurt(self, damage)
        self.nextAttack += random.randint(0, self.attackWait/2)
