"""
simModelInterface.py
Provides the base classes used to interface with the Simulation Core.
This module also provides physical simulation routines.
Originates from A-Life, 2.0, CS Capstone project at Oregon State University
"""
from numpy import *
import time
import random
from abc import ABC, abstractmethod
import vpython as view # TODO decouple and interface through simCore

"""
Base class all physical objects inherit from.
"""
class PhysicalObjectBase:
    # trajectory is an array of SpaceTimePositions
    def __init__(self, simCore, id, trajectory, class_type = ""):
        self.simCore = simCore
        self.id = id
        self.trajectory = trajectory
        if class_type == "":
            self.class_type = type(self)
        else:
            self.class_type = class_type
            self.__class__ = globals()[class_type]
        self.visualModel = view.sphere() # TODO this will need to be assigned from a pool.
        self.schedule = []

    def get_position(self, t):
        # TODO simple stub assuming trajectory is always only 2 points.
        # Do a real calculation during real implementation.
        # TODO validate
        previousPointOnTrajectory = self.trajectory[0]
        nextPointOnTrajectory = self.trajectory[1]
        interval = nextPointOnTrajectory.t - previousPointOnTrajectory.t
        velocity = nextPointOnTrajectory.sPos - previousPointOnTrajectory.sPos * (1 / interval)
        sPos = previousPointOnTrajectory.sPos + velocity * (t - previousPointOnTrajectory.t)
        return SpaceTimePosition(sPos.x, sPos.y, sPos.z, t)

    def fire_events(self, t):
        for event in self.schedule:
            if (t >= event.t):
                event.invoke(self)
                self.schedule.remove(event)

class Event(ABC): # Abstract
    def __init__(self, t, args) -> None:
        super().__init__()
        self.t = t
        self.args = args
    @abstractmethod
    def invoke(self):
        pass

# borrowing vpython's vector TODO we will want owr own.
#class Vector:

class SpaceTimePosition:
    def __init__(self, x, y, z, t):
        self.x = x
        self.y = y
        self.z = z
        self.t = t
        self.sPos = view.vector(self.x, self.y, self.z)

    def __str__(self):
        return f"({self.x}, {self.y}, {self.z}, {self.t})"

"""
Test model class used to stress test the simulation.
"""
class TestObjectFactory(PhysicalObjectBase):
    def __init__(self, simCore, id, trajectory):
        super().__init__(simCore, id, trajectory)
        now = trajectory[0].t
        rateModifier = 10
        eventTime = now + rand()
        nextEventTime = eventTime
        for i in range(1000): # these events will fire produce()
            nextEventTime = nextEventTime + rand(1/rateModifier)
            childID = f"{id}.{i}"
            args = [childID]
            self.schedule.append(
                TestObjectFactoryProduceEvent(nextEventTime, args))

    def produce(self, t, id):
        point1 = self.get_position(t)
        maxDistance = 100 # TODO don't use magic numbers in real models
        randUnitVector = randomUnitVector() # array form
        point2 = SpaceTimePosition(
            maxDistance * (randUnitVector[0]),
            maxDistance * (randUnitVector[1]),
            maxDistance * (randUnitVector[2]),
            t + 60*rand())
        trajectory = [point1, point2]
        newObj = PhysicalObjectBase(self, id, trajectory)
        # TODO this will not always be a sphere. We will need an interface
        newObj.visualModel.radius = 5
        spacetimePos = newObj.get_position(t)
        newObj.visualModel.pos = spacetimePos.sPos
        # TODO make an interface for stuff like this
        self.simCore.physicalObjects[newObj.id] = newObj

"""
Event that goes with the TestObjectFactory
"""
class TestObjectFactoryProduceEvent(Event):
    def __init__(self, t, args) -> None:
        super().__init__(t, args)
    def invoke(self, physicalObject):
        id = self.args[0]
        physicalObject.produce(self.t, id)

# TODO remove after save/load_simulation implemented and tested
def get_initial_conditions(simCore):
    # TODO For Brook to write test initial conditions
    point1 = SpaceTimePosition(0, 0, 0, simCore.now)
    point2 = SpaceTimePosition(0, 0, 0, simCore.now + 60) # stay alive for 60 seconds
    trajectory = [point1, point2]
    testObj = TestObjectFactory(simCore, simCore.nextID, trajectory)
    physicalObjects = {f"{simCore.nextID}": testObj}
    return physicalObjects


"""
The projectile class is the general object class for preforming classical 
simulations. It provides some basic functions for modifying the state of a
projectile.
"""
class Projectile(object):
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
    def unconstrainedMotion(self, potential = array([0,0,0])):
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
    if len(args) == 0:
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
    if len(args) == 0:
        return randomFloat
    if len(args) == 1:
        return randomFloat * args[0]
    else:
        return randomFloat * (args[1] - args[0]) + args[0]

"""
Returns a unit vector in a random direction.
"""
def randomUnitVector():
    randomVector = array([rand(-1,1),rand(-1,1),rand(-1,1)])
    return randomVector/sqrt(sum(i**2 for i in randomVector))
