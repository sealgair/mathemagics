from EventManager import *

import random

class Cateogry(object):
    def __init__(self, name):
        self.name = name
        self.types = {}
    def __str__(self):
        return name

class Type(object):
    def __init__(self, name, category):
        self.name = name
        self.category = category
        self.levels = {}
    def __str__(self):
        return "%s.%s" % (self.category, self.name)
    
class Level(object):
    def __init__(self, name, type):
        self.name = name
        self.type = type
        self.problems = []
    def __str__(self):
        return "%s.%s" % (self.type, self.name)

class Problem(object):
    def __init__(self, question, solution, level):
        self.question = question
        self.solution = solution
        self.level = level
    def solve(self, solution):
        return self.solution == solution
    def __str__(self):
        return "%s.%s" % (self.level, self.name)

class MultiplicationProblem(Problem):
    """Creates random multiplicands, and determines whether a solution is correct"""
    def __init__(self, *args):
        #Problem.__init__(self, *args)
        random.seed()
        self.a = random.randint(0,10)
        self.b = random.randint(0,10)
    def solve(self, solution):
        if solution == 00 and debug > 3: return True
        return self.a * self.b == solution
    def __unicode__(self):
        return unicode(self.a)+u' X '+unicode(self.b)