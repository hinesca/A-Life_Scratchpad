"""
simHelper.py
This module provides physical simulation routines.
"""
from numpy import *
import time
import random

"""
The projectile class is the general object class for preforming classical 
simulations. It provides some basic functions for modifying the state of a
projectile.
"""
class projectile(object):
    def __init__(self,position,velocity = array([0,0,0]),potential = array([0,0,0]),mass = 1,timestep = 1):
            self.positionPast = position - velocity * timestep - potential * timestep**2
            self.positionFuture = position + velocity * timestep + potential * timestep**2
            self.position = position
            self.velocity = velocity
            self.speed = sqrt(sum(i**2 for i in self.velocity))
            self.potential = potential
            self.timestep = timestep
            self.mass = mass

    """
    The unconstrainedMotion function modifies the position of a projectile based 
    on Newton's laws of motion. The function uses the Verlet integration algorithm.
    """
    def unconstrainedMotion(self,potential = array([0,0,0])):
        self.potential = potential
        self.positionPast = self.position
        self.position = self.positionFuture
        self.positionFuture = 2*self.position - self.positionPast + self.potential*self.timestep**2
        self.velocity = (self.positionFuture - self.positionPast)/(2*self.timestep)
        self.speed = sqrt(sum(i**2 for i in self.velocity))

    """
    The constrainedMotion function directly modifies the position of a projectile. 
    """
    def constrainedMotion(self, positionFuture):
        self.positionPast = self.position
        self.position = self.positionFuture
        self.positionFuture = positionFuture
        self.velocity = (self.positionFuture - self.positionPast)/(2*self.timestep)
        self.speed = sqrt(sum(i**2 for i in self.velocity))
        self.potential = (self.positionFuture + self.positionPast - 2*self.position) / self.timestep**2

    """
    The randomWalk function simulates elastic collisions with unseen particles
    in which the resulting velocity vector is in a random direction. The probability
    of a collision is based on the mean free path.
    """
    def randomWalk(self,meanFreePath,potential = array([0,0,0])):
        tau = meanFreePath/self.speed
        # tau is the average time between collisions
        probabilityCollision = exp(-self.timestep/tau)
        # the probability of a collision follows a Poisson distribution
        if rand() < probabilityCollision:
            self.unconstrainedMotion(potential = potential)
            self.collision = False
        else:
            self.positionPast = self.position
            self.position = self.positionFuture
            self.positionFuture = self.position + (self.speed*self.timestep*randomUnitVector())
            self.collision = True

"""
Accepts 0 or 1 argument. 1 argument sets the seed to be used with the random 
number generator. 0 arguments generated a seed based on the time.
Two instances of the random number generator rand with the same seed will 
produce the same random sequence.
"""
def setSeed(*args):
    if len(args) == 0 :
        seed = abs(time.time() - round(time.time()))
    else:
        seed = args[0]
    random.seed = seed

"""
Zero arguments: returns a random float from 0-1.
One argument: returns a random float from 0-arg
More: returns a random float from arg[0]-arg[1]
"""
def rand(*args):
    randomFloat = random.random()
    if len(args) == 0 :
        return randomFloat
    if len(args) == 1 :
        return randomFloat * args[0]
    else:
        return randomFloat * (args[1] - args[0]) + args[0]

"""
Returns a unit vector in a random direction.
"""
def randomUnitVector():
    randomVector = array([rand(-1,1),rand(-1,1),rand(-1,1)])
    return randomVector/sqrt(sum(i**2 for i in randomVector))
