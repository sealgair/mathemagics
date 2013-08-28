import unittest

from EventManager import *
from controller import *
from model import *
from view import * #...but how to test?

import threading
import time

class EventDrivenTestCase(unittest.TestCase):
    """Generic test case that keeps track of an instance of Event Manager, and blanks it out
    at the start up and finish of each test, to eliminate noise"""
    def __init__(self, *args, **kwds):
        unittest.TestCase.__init__(self, *args, **kwds)
        self.evManager = EventManager()
    def setUp(self):
        del self.evManager.initialized
        self.evManager = EventManager()
    def tearDown(self):
        del self.evManager.initialized
        self.evManager = EventManager()

# Some test listeners with varying degrees of validity and functionality
class ValidListener:
    """Properly defines method 'Notify(self, event)'"""
    def Notify(self, event):
        pass

class BadNotifyListener:
    """Improperly defines method 'Notify(self, event)'
    Notify doesn't have required 2nd 'event' param"""
    def Notify(self):
        pass

class NoNotifyListener:
    """doesn't define method 'Notify(self, event)'"""
    pass

class TestListener:
    """Keeps track of all events it hass been notified of"""
    def __init__(self, recordTicks=False):
        self.events = []
        EventManager().RegisterListener(self)
        self.recordTicks = recordTicks
    def Notify(self, event):
        if not isinstance(event, TickEvent) or self.recordTicks == True:
            self.events.append(event)
    def getEventClasses(self):
        return [e.__class__ for e in self.events]

class RegisterListenerTest(EventDrivenTestCase):    
    def testRegisterValidListener(self):
        """Verify that registering a valid listener:
            * doesn't throw an error
            * adds that listener to the list of registered listeners
        """
        vl = ValidListener()
        try: 
            self.evManager.RegisterListener(vl)
        except(TypeError):
            self.fail("RegisterListener raised TypeError when registering valid listener")
        self.assertEqual(len(self.evManager.listeners), 1, 
                         "listeners %s should contain one listener" % self.evManager.listeners.keys())
        self.assertEqual(self.evManager.listeners.keys()[0], vl,
                         "listeners %s should contain %s" % (self.evManager.listeners.keys(), vl))
    
    def testRegisterNoNotifyListener(self):
        """Verify that registering a listener with no notify method:
            * raises a TypeError
            * doesn't add anything to the list of registered listeners
        """
        self.assertRaises(TypeError, self.evManager.RegisterListener, NoNotifyListener(),
                          "Registering a listener with no notify method should raise a TypeError")
        self.assertEqual(len(self.evManager.listeners), 0,
                         "listeners %s should be empty" % self.evManager.listeners.keys())
    
    def testRegisterBadNotifyListener(self):
        """Verify that registering a listener with a bad notify method:
            * raises a TypeError
            * doesn't add anything to the list of registered listeners
        """
        self.assertRaises(TypeError, self.evManager.RegisterListener, BadNotifyListener(),
                          "Registering a listener with a bad notify method should raise a TypeError")
        self.assertEqual(len(self.evManager.listeners), 0,
                         "listeners %s should be empty" % self.evManager.listeners.keys())
    
    def testUnregisterExistingListener(self):
        """Verify that unregistering a valid listener (that is already in the list):
            * doesn't throw an error
            * removes that listener from the list of registered listeners
        """
        vl = ValidListener()
        self.evManager.RegisterListener(vl)
        try:
            self.evManager.UnregisterListener(vl)
        except(BaseException):
            self.fail("Unregistering an existing listener threw an Error")
        self.assertEqual(len(self.evManager.listeners), 0,
                         "listeners %s should be empty" % self.evManager.listeners.keys())
    
    def testUnregisterNonExistantListener(self):
        """Verify that unregistering a listener that is not in the (non-empty) list:
            * doesn't throw an error (fails silently)
            * doesn't change the list of registered listeners
        """
        vl1 = ValidListener()
        vl2 = ValidListener()
        self.evManager.RegisterListener(vl1)
        before = self.evManager.listeners.keys()*1 #create a shallow copy
        try:
            self.evManager.UnregisterListener(vl2)
        except(BaseException):
            self.fail("Unregistering an existing listener threw an Error (should fail silently)")
        after = self.evManager.listeners.keys()
        self.assertEqual(len(before), len(after), 
                         "list of listners is not the same length"+\
                         " before & after unregister: was %s before and %s after" \
                         % (len(before), len(after)))
        for i in range(0,len(before)):
            self.assertEqual(before[i], after[i], 
                             "Listener %s in list was not the same before and after: "+\
                             "found %s before and %s after" % (len(before), len(after)))
                     

class TestEvent(Event):
    """Generic event using specified name for test purposes"""
    def __init__(self, name):
        self.name = name

class NotifyEventTest(EventDrivenTestCase):
    def testNotify(self):
        """Verify that a notification to the event manager will send a 
            notification to a registered listener"""
        tl = TestListener()
        ev = TestEvent("Generic Event")
        self.evManager.Notify(ev)
        
        self.assertEquals(tl.events, [ev],
                          "Test Event list should just contain %s, found to contain %s" % (ev, tl.events))
    
    def testNotifyWhenUnregistered(self):
        """Verify that a newly unregistered listener does not recieve event notifications"""
        tl = TestListener()
        positiveEvents = [TestEvent("Postitive Event 1"), TestEvent("Postitive Event 2")]
        negativeEvents = [TestEvent("Negative Event 1")]        
        self.evManager.Notify(positiveEvents[0]) #should recieve
        self.evManager.UnregisterListener(tl)
        self.evManager.Notify(negativeEvents[0]) #should not recieve
        self.evManager.RegisterListener(tl)
        self.evManager.Notify(positiveEvents[1]) #shoudl recieve
        
        self.assertEquals(tl.events, positiveEvents,
                          "Test Event list should just contain %s, found to contain %s" % (positiveEvents, tl.events))

class MockKeyEvent:
    """Mockup of a pygame keypress event"""
    def __init__(self, type, key=None, unicode=''):
        self.type = type
        self.key = key
        self.unicode = unicode
    def __str__(self):
        return "Test Key Event: type=%s key=%s unicode='%s'" % (self.type, self.key, self.unicode)

class KeyboardControllerTest(EventDrivenTestCase):
    def setUp(self):
        EventDrivenTestCase.setUp(self)
        self.game = Game()
        while self.game.state == Game.STATE_PREPARING:
            self.evManager.Notify(TickEvent(10))
        self.keybd = KeyboardController()
    
    def tearDown(self):
        self.evManager.Notify(QuitEvent())
        EventDrivenTestCase.tearDown(self)
    
    def testQuit(self):
        """Tests the quit keypress to verify the appropriate event is triggered"""
        quitkey = MockKeyEvent(pygame.locals.KEYDOWN, pygame.locals.K_ESCAPE)
        
        tl = TestListener()
        pygame.event.get = lambda: [quitkey]
        self.keybd.Notify(TickEvent(10))
        
        self.assertEquals(len(tl.events), 1, 
                          "Test Event list should contain only one event, found %s" \
                          % len(tl.events))
        self.assertEquals(tl.getEventClasses(), [QuitEvent],
                          "Test Event list should just contain: \n%s \nfound to contain: \n%s" \
                          % (QuitEvent, tl.events))
    
    def testAttackFlow(self):
        """Tests a standard attack flow keypress series to verify that the 
            appropriate events are triggered"""
        attackFlow = []
        expectedEvents = []
        tl = TestListener()
                
        #press space
        attackFlow.append(MockKeyEvent(pygame.locals.KEYDOWN, pygame.locals.K_SPACE))
        expectedEvents.append(RequestAttackEvent)
        expectedEvents.append(RequestSolutionEvent)
        
        #ask for solution to be determined & drawn
        pygame.event.get = lambda: attackFlow
        self.evManager.Notify(TickEvent(10))
        #reset attackFlow
        attackFlow = []
        
        #press 1
        attackFlow.append(MockKeyEvent(pygame.locals.KEYDOWN, unicode=u'1'))
        expectedEvents.append(SolutionUpdateEvent)
        
        #press Enter
        attackFlow.append(MockKeyEvent(pygame.locals.KEYDOWN, pygame.locals.K_RETURN, u'\\r'))
        expectedEvents.append(SolveEvent)
        expectedEvents.append(HurtEvent)
        
        #enter solution
        pygame.event.get = lambda: attackFlow
        self.evManager.Notify(TickEvent(10))
        
        #sorted because order doesn't matter -- some events may get registered in a 
        #    slightly different order sometimes
        expected = expectedEvents.sort()
        found = tl.getEventClasses().sort()
        self.assertEquals(found, expected, 
                          "Test Event list should just contain: \n%s \nfound to contain: \n%s" \
                          % (expected, found))

class CPUSpinnerTest(EventDrivenTestCase):
    def setUp(self):
        EventDrivenTestCase.setUp(self)
        self.spinner = CPUSpinnerController()
        self.spinnerThread = threading.Thread(target=self.spinner.Run)
    
    def tearDown(self):
        self.spinner.keepGoing = False #force spinner to stop, if it hasn't already
        EventDrivenTestCase.tearDown(self)
    
    def testRun(self):
        """Verify that the CPU Spinner sends out tick events at a rate of 'maxfps' per second"""
        maxfps = 20
        runSeconds = 1
        self.spinner = CPUSpinnerController(maxfps)
        self.spinnerThread = threading.Thread(target=self.spinner.Run)
        tl = TestListener(recordTicks=True)
                
        self.spinnerThread.start()
        time.sleep(runSeconds) # let it run for a second
        self.spinner.keepGoing = False # stop it
        
        ticks = [e for e in tl.events if isinstance(e, TickEvent)]
        self.assert_(len(ticks) > 0, "CPU Spinner did not send any Tick Events")
        fpsbuffer = maxfps*runSeconds
        fpsbuffer *= 1.1 # allow +10% margin of error
        self.assert_(len(ticks) < fpsbuffer,
                     "CPU Spinner did not throttle clock ticks to %s per second:" % maxfps +
                     " it ran for %s ticks in %s seconds" % (len(ticks), runSeconds))
    
    def testQuitEvent(self):
        """Verify that the CPU Spinner stops sending out tick events when the quit event is sent"""
        self.spinnerThread.start()
        self.evManager.Notify(QuitEvent())
        time.sleep(.5) # wait a bit for the thread to finish
        self.assert_(not self.spinnerThread.isAlive(), "CPU Spinner did not stop after quit event")
    
    def testNonQuitEvent(self):
        """Verify that the CPU Spinner doesn't stop sending out tick events
            when an event other than the quit event is sent"""
        self.spinnerThread.start()
        self.evManager.Notify(Event()) #something other than the quit event
        time.sleep(.5) # wait a bit for the thread to finish
        self.assert_(self.spinnerThread.isAlive(), "CPU Spinner stopped after quit event")

class GameTest(EventDrivenTestCase):
    def setUp(self):
        self.game = Game()
    
    def testSendSpawnHeroEvent(self):
        """Verifies that a SpawnHeroEvent is sent when the game is started"""
        tl = TestListener()
        self.game.Start()
        self.assert_(tl.getEventClasses().count(SpawnHeroEvent) > 0,
                     "Game did not send a SpawnHeroEvent on game start.  Events sent: %s" \
                     % tl.getEventClasses())
    
    def testSendSpawnEnemyEvent(self):
        """Verifies that a SpawnEnemyEvent is sent when the game is started"""
        tl = TestListener()
        self.game.Start()
        self.assert_(tl.getEventClasses().count(SpawnEnemyEvent) > 0,
                     "Game did not send a SpawnEnemyEvent on game start.  Events sent: %s" \
                     % tl.getEventClasses())
    
    def testSendGameStartedEvent(self):
        """Verifies that a GameStartedEvent is sent when the game is started"""
        tl = TestListener()
        self.game.Start()
        self.assert_(tl.getEventClasses().count(GameStartedEvent) > 0,
                     "Game did not send a GameStartedEvent on game start.  Events sent: %s" \
                     % tl.getEventClasses())
    
    def testStart(self):
        """Verifies that the start method triggers the creation of a hero, enemy, 
            and changes the game's state to Game.STATE_RUNNING"""
        self.game.Start()
        self.assertEquals(self.game.hero.__class__, HeroModel, 
                          "Game did not spawn hero on startup: found %s instead" % self.game.hero)
        self.assertEquals(self.game.enemy.__class__, EnemyModel, 
                          "Game did not spawn enemy on startup: found %s instead" % self.game.enemy)
        self.assertEquals(self.game.state, Game.STATE_RUNNING, 
                          "Game state is not STATE_RUNNING after startup: found %s instead" % self.game.state)
    
    def testGetSpawnHeroEvent(self):
        """Verifies that the game spawns a hero on SpawnHeroEvent"""
        self.evManager.Notify(SpawnHeroEvent("Test"))
        self.assertEquals(self.game.hero.__class__, HeroModel, 
                          "Game did not spawn hero on SpawnHeroEvent: found %s instead" % self.game.hero)
    
    def testGetSpawnEnemyEvent(self):
        """Verifies that the game spawns an enemy on SpawnEnemyEvent"""
        self.evManager.Notify(SpawnEnemyEvent("Test"))
        self.assertEquals(self.game.enemy.__class__, EnemyModel, 
                          "Game did not spawn hero on SpawnEnemyEvent: found %s instead" % self.game.hero)
    
    def testGetDieEvent(self):
        """Verifies that the game state changes to STATE_GAMEOVER on DieEvent"""
        self.game.Start()
        self.evManager.Notify(DieEvent(self.game.hero))
        self.assertEquals(self.game.state, Game.STATE_GAMEOVER,
                          "Game state is not STATE_GAMEOVER after DieEvent: found %s instead" %
                           self.game.state)

class ActorModelTest(EventDrivenTestCase):
    def setUp(self):
        self.tl = TestListener()
        self.actor = ActorModel("Test")
    
    def testWait(self):
        """Verifies that the Actor is put in a waiting state and 
            sends out a WaitEvent when Wait() is called"""
        self.actor.Wait()
        self.assertEquals(self.actor.state, ActorModel.STATE_WAITING, 
                          "Actor.Wait() did not set actor's state to Waiting: "+\
                          "found %s" % self.actor.state)
        self.assertEquals(len(self.tl.events), 1, 
                          "Expected Wait method to send 1 event, instead got %s" % 
                          len(self.tl.events))
        self.assertEquals(str(self.tl.events[0]), str(WaitEvent("Test")), 
                          "Actor.Wait() did not send out a WaitEvent: "+\
                          "found %s" % [str(e) for e in self.tl.events])
    
    def testNextVictim(self):
        """Verifies that the Actor's victim is advanced"""
        self.actor.opponents = {'a':"a", 'b':"b"}
        
        self.actor.nextVictim()
        self.assertEquals(self.actor.victim, "a", 
                          "Actor's victim not set to initial value on first call of nextVictim: "+\
                          "expected %s got %s" % ("a","b"))
        self.actor.nextVictim()
        self.assertEquals(self.actor.victim, "b", 
                          "Actor's victim not advanced along list of opponents on call of nextVictim: "+\
                          "expected %s got %s" % ("a","b"))
        self.actor.nextVictim()
        self.assertEquals(self.actor.victim, "a", 
                          "Actor's victim didn't properly wrap after end of opponent list on call "+
                          "of nextVictim: expected %s got %s" % ("a","b"))        
    
    def testAttack(self):
        """Verifies that state is set to attack and AttackEvent is sent"""
        self.actor.opponents["victim"] = ActorModel("victim")
        self.actor.Attack(0)
        self.assertEquals(self.actor.state, ActorModel.STATE_ATTACKING, 
                          "Actor.Wait() did not set actor's state to Attacking: "+\
                          "found %s" % self.actor.state)
        self.assertEquals([str(e) for e in self.tl.events].count(str(AttackEvent("Test", "victim", 0))), 1,
                          "Actor.Attack() did not send out a AttackEvent: "+\
                          "found %s" % [str(e) for e in self.tl.events])        
    
    def testDefend(self):
        """Verifies that the Actor is put in a defending state and 
            sends out a DefendEvent when Defend() is called"""
        self.actor.Defend()
        self.assertEquals(self.actor.state, ActorModel.STATE_DEFENDING, 
                          "Actor.Defend() did not set actor's state to Defending: "+\
                          "found %s" % self.actor.state)
        self.assertEquals(len(self.tl.events), 1, 
                          "Expected Defend method to send 1 event, instead got %s" % 
                          len(self.tl.events))
        self.assertEquals(str(self.tl.events[0]), str(DefendEvent("Test")), 
                          "Actor.Defend() did not send out a DefendEvent: "+\
                          "found %s" % [str(e) for e in self.tl.events])
    
    def testHurt(self):
        """Verifies that the Actor is put in a hurting state and 
            sends out a HurtEvent when Hurt() is called"""
        self.actor.Hurt(0)
        self.assertEquals(self.actor.state, ActorModel.STATE_HURTING, 
                          "Actor.Hurt() did not set actor's state to HurtING: "+\
                          "found %s" % self.actor.state)
        self.assertEquals(len(self.tl.events), 1, 
                          "Expected Hurt method to send 1 event, instead got %s" % 
                          len(self.tl.events))
        self.assertEquals(str(self.tl.events[0]), str(HurtEvent("Test", 1.0)), 
                          "Actor.Hurt() did not send out a HurtEvent: "+\
                          "found %s" % [str(e) for e in self.tl.events])
    
    def testHurtUpdateHealth(self):
        """Verifies that hurting the actor modifies the actor's health"""
        health = self.actor.health
        dmg = 20
        self.actor.Hurt(dmg)
        self.assertEquals(self.actor.health, health-dmg, 
                          "Hurting the actor did not result in expected health: expected %s, found %s" %
                          (health-dmg, self.actor.health))
    
    def testAttackEvent(self):
        """Verifies that hurt is called if AttackEvent is triggered
            with actor as object of attack"""
        dmg = self.actor.health*0.5
        self.evManager.Notify(AttackEvent("Attacker", "Test", dmg))
        self.assertEquals([str(e) for e in self.tl.events].count(str(HurtEvent("Test", 0.5))), 1,
                          "AttackEvent did not trigger victim to send HurtEvent")
        self.assertEquals(self.actor.health, dmg, 
                          "AttackEvent did not cause victim to lose health")
    
    def testDie(self):
        """Verifies that the Actor is put in a dead state and 
            sends out a DieEvent when Die() is called"""
        self.actor.Die()
        self.assertEquals(self.actor.state, ActorModel.STATE_DEAD, 
                          "Actor.Die() did not set actor's state to Dead: "+\
                          "found %s" % self.actor.state)
        self.assertEquals(len(self.tl.events), 1, 
                          "Expected Die method to send 1 event, instead got %s" % 
                          len(self.tl.events))
        self.assertEquals(str(self.tl.events[0]), str(DieEvent("Test")), 
                          "Actor.Die() did not send out a DieEvent: "+\
                          "found %s" % [str(e) for e in self.tl.events])

class HeroModelTest(EventDrivenTestCase):
    def setUp(self):
        EventDrivenTestCase.setUp(self)
        self.tl = TestListener()
        self.hero = HeroModel("Hero")
        
    def testStartAttack(self):
        """Verifies that the hero is in the right state after a RequestAttackEvent, 
            and generates a RequestSolutionEvent"""
        self.evManager.Notify(TickEvent(10,1)) # to make sure everything is initialized properly
        self.evManager.Notify(RequestAttackEvent())
        
        self.assertEquals(self.hero.problem.__class__, MultiplicationProblem,
                          "Hero did not create a problem on RequestAttackEvent")
        self.assert_(self.hero.solEndTime > 0, 
                     "Hero did not set a solution end time on RequestAttackEvent")
        self.assertEquals(self.tl.getEventClasses().count(RequestSolutionEvent), 1, 
                          "Hero did not send RequestSolutionEvent on RequestAttackEvent")        
    
    def testSolveCorrectly(self):
        """Verifies that solving a problem correctly Generates an attack event"""
        self.hero.opponents["v"] = ActorModel("v")
        self.evManager.Notify(TickEvent(10,1)) # to make sure everything is initialized properly
        self.evManager.Notify(RequestAttackEvent())
        
        self.tl = TestListener() # clear previous events
        self.evManager.Notify(SolveEvent(unicode(self.hero.problem.a*self.hero.problem.b)))
        
        self.assertEquals(self.tl.getEventClasses().count(AttackEvent), 1, 
                          "Correct solution didn't generate AttackEvent: found %s" % self.tl.getEventClasses())
        for e in self.tl.events:
            if isinstance(e, AttackEvent): ae = e
        self.assertEquals(ae.subject, "Hero", 
                          "Generated AttackEvent had wrong subject: Expected 'Hero', got '%s'" % ae.subject)
        self.assertEquals(ae.object, "v", 
                          "Generated AttackEvent had wrong object: Expected 'v', got '%s'" % ae.object)
    
    def testSolveIncorrectly(self):
        """Verifies that solving a problem incorrectly Generates a hurt event"""
        self.hero.opponents["v"] = ActorModel("v")
        self.evManager.Notify(TickEvent(10,1)) # to make sure everything is initialized properly
        self.evManager.Notify(RequestAttackEvent())
        
        self.tl = TestListener() # clear previous events
        self.evManager.Notify(SolveEvent(unicode(self.hero.problem.a*self.hero.problem.b+42)))
        
        self.assertEquals(self.tl.getEventClasses().count(HurtEvent), 1, 
                          "Incorrect solution didn't generate HurtEvent: found %s" % self.tl.getEventClasses())
        for e in self.tl.events:
            if isinstance(e, HurtEvent): he = e
        self.assertEquals(he.subject, "Hero", 
                          "Generated HurtEvent had wrong subject: Expected 'Hero', got '%s'" % he.subject)
    
    def testSolveBadData(self):
        """Verifies that solving a problem with invalid data Generates a hurt event"""
        self.hero.opponents["v"] = ActorModel("v")
        self.evManager.Notify(TickEvent(10,1)) # to make sure everything is initialized properly
        self.evManager.Notify(RequestAttackEvent())        
        self.evManager.Notify(SolveEvent(u"look at me!! I'm invalid!!"))
        
        self.assertEquals(self.tl.getEventClasses().count(HurtEvent), 1, 
                          "Incorrect solution didn't generate HurtEvent: found %s" % self.tl.getEventClasses())
        for e in self.tl.events:
            if isinstance(e, HurtEvent): he = e
        self.assertEquals(he.subject, "Hero", 
                          "Generated HurtEvent had wrong subject: Expected 'Hero', got '%s'" % he.subject)
    
    def testSolveTimeout(self):
        """Verifies that letting the solution timer expire Generates a hurt event"""
        self.hero.opponents["v"] = ActorModel("v")
        self.evManager.Notify(TickEvent(10,1)) # to make sure everything is initialized properly
        self.evManager.Notify(RequestAttackEvent())
        
        dtime = self.hero.solutionWait * 1.1 # expire and then some
        time = self.hero.time + dtime
        self.evManager.Notify(TickEvent(time, dtime))
        
        self.assertEquals(self.tl.getEventClasses().count(HurtEvent), 1, 
                          "Solution timeout didn't generate HurtEvent: found %s" % self.tl.getEventClasses())
        for e in self.tl.events:
            if isinstance(e, HurtEvent): he = e
        self.assertEquals(he.subject, "Hero", 
                          "Generated HurtEvent had wrong subject: Expected 'Hero', got '%s'" % he.subject)

class EnemyModelTest(EventDrivenTestCase):
    def setUp(self):
        EventDrivenTestCase.setUp(self)
        self.tl = TestListener()
        self.enemy = EnemyModel("Enemy", 0)
        self.enemy.opponents["v"] = ActorModel("v")
    
    def testAttackAfterNothing(self):
        """Verify that the enemy attacks some time after creation (with no provocation)"""
        self.evManager.Notify(TickEvent(10,1)) # to make sure everything is initialized properly
        time = self.enemy.nextAttack+50 #milliseconds
        dtime = time - self.enemy.time
        self.evManager.Notify(TickEvent(time, dtime))
        
        self.assertEquals(self.tl.getEventClasses().count(AttackEvent), 1, 
                          "Correct solution didn't generate AttackEvent: found %s" % self.tl.getEventClasses())
        for e in self.tl.events:
            if isinstance(e, AttackEvent): ae = e
        self.assertEquals(ae.subject, "Enemy", 
                          "Generated AttackEvent had wrong subject: Expected 'Enemy', got '%s'" % ae.subject)
        self.assertEquals(ae.object, "v", 
                          "Generated AttackEvent had wrong object: Expected 'v', got '%s'" % ae.object)
    
    def testAttackAfterAttack(self):
        """Verify that the enemy count was reset after a prevoius attack, and that the enemy attacks again"""
        self.evManager.Notify(TickEvent(10,1)) # to make sure everything is initialized properly
        
        time = self.enemy.nextAttack+50 #milliseconds
        dtime = time - self.enemy.time
        self.evManager.Notify(TickEvent(time, dtime))
        self.tl = TestListener() #clear events
        
        #and attack again
        time = self.enemy.nextAttack+50 #milliseconds
        dtime = time - self.enemy.time
        self.evManager.Notify(TickEvent(time, dtime))
                
        self.assertEquals(self.tl.getEventClasses().count(AttackEvent), 1, 
                          "Correct solution didn't generate AttackEvent: found %s" % self.tl.getEventClasses())
        for e in self.tl.events:
            if isinstance(e, AttackEvent): ae = e
        self.assertEquals(ae.subject, "Enemy", 
                          "Generated AttackEvent had wrong subject: Expected 'Enemy', got '%s'" % ae.subject)
        self.assertEquals(ae.object, "v", 
                          "Generated AttackEvent had wrong object: Expected 'v', got '%s'" % ae.object)
    
    def testAttackAfterHurt(self):
        """Verify that the enemy count was reset after being hurt, and that the enemy attacks again"""
        self.evManager.Notify(TickEvent(10,1)) # to make sure everything is initialized properly
        
        self.evManager.Notify(AttackEvent("v", "Enemy", 0))
        self.tl = TestListener() #clear events
        
        #and attack again
        time = self.enemy.nextAttack+50 #milliseconds
        dtime = time - self.enemy.time
        self.evManager.Notify(TickEvent(time, dtime))
                
        self.assertEquals(self.tl.getEventClasses().count(AttackEvent), 1, 
                          "Correct solution didn't generate AttackEvent: found %s" % self.tl.getEventClasses())
        for e in self.tl.events:
            if isinstance(e, AttackEvent): ae = e
        self.assertEquals(ae.subject, "Enemy", 
                          "Generated AttackEvent had wrong subject: Expected 'Enemy', got '%s'" % ae.subject)
        self.assertEquals(ae.object, "v", 
                          "Generated AttackEvent had wrong object: Expected 'v', got '%s'" % ae.object)

#view tests(?)

if __name__ == '__main__':
    unittest.main()
