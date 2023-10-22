# SimCore.py
# Author: Casey Hines October 2021

# For simplicity and to get a working simulation, we are treating vpython as the view
import vpython as view
import time
from abc import ABC, abstractmethod
import simHelper

# Simple representation of time in seconds after epoch
# TODO: think about different implementation
now = 0
epoch = time.time()
nextID = 0

# These classes will go in the model

# base class all physical objects inherit from
class PhysicalObjectBase:
    # trajectory is an array of SpaceTimePositions
    def __init__(self, realTimeEngin, id, trajectory):
        self.realTimeEngin = realTimeEngin
        self.id = id
        self.trajectory = trajectory
        self.visualModel = view.sphere() # TODO this will need to be assigned from a pool.
        self.schedule = []

    def get_position(self):
        # TODO simple stub assuming trajectory is always only 2 points.
        # Do a real calculation during real implementation.
        # TODO validate
        global now
        previousPointOnTrajectory = self.trajectory[0]
        nextPointOnTrajectory = self.trajectory[1]
        interval = nextPointOnTrajectory.t - previousPointOnTrajectory.t
        velocity = nextPointOnTrajectory.sPos - previousPointOnTrajectory.sPos * (1 / interval)
        sPos = previousPointOnTrajectory.sPos + velocity * (now - previousPointOnTrajectory.t)
        return SpaceTimePosition(sPos.x, sPos.y, sPos.z, now)

    def fire_events(self):
        global now
        for event in self.schedule:
            if (now >= event.time):
                event.invoke(self)
                self.schedule.remove(event)

# This is a toy test model object to stress test the simulation
class TestObjectFactory(PhysicalObjectBase):
    def __init__(self, realTimeEngin, id, trajectory):
        super().__init__(realTimeEngin, id, trajectory)
        global now
        rateModifier = 10
        eventTime = now + simHelper.rand()
        nextEventTime = eventTime
        for i in range(1000): # these events will fire produce()
            nextEventTime = nextEventTime + simHelper.rand(1/rateModifier)
            self.schedule.append(
                TestObjectFactoryProduce(nextEventTime))

    def produce(self):
        global now
        global nextID
        point1 = self.get_position()
        maxDistance = 100 # TODO don't use magic numbers in real models
        randUnitVector = simHelper.randomUnitVector() # array form
        point2 = SpaceTimePosition(
            maxDistance * (randUnitVector[0]),
            maxDistance * (randUnitVector[1]),
            maxDistance * (randUnitVector[2]),
            now + 60*simHelper.rand())
        trajectory = [point1, point2]
        nextID = nextID + 1
        newObj = PhysicalObjectBase(self, nextID, trajectory)
        # TODO this will not always be a sphere. We will need an interface
        newObj.visualModel.radius = 5
        spacetimePos = newObj.get_position()
        newObj.visualModel.pos = spacetimePos.sPos
        # TODO make an interface for stuff like this
        self.realTimeEngin.physicalObjectCollection.append(newObj)

class Event(ABC): # Abstract
    def __init__(self, futureTime) -> None:
        super().__init__()
        self.time = futureTime

    @abstractmethod
    def invoke(self, physicalObject):
        pass

class TestObjectFactoryProduce(Event):
    def __init__(self, futureTime) -> None:
        super().__init__(futureTime)

    def invoke(self, physicalObject):
        physicalObject.produce()

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

# Simulation Engin
class RealTimeEngin:
    def __init__(self):
        scene = view.canvas(x = 0, y = 0, autoscale = False)
        # TODO Remember to clean up magic numbers.
        # These can be controls in the UI.
        self.dt = 0.02
        scene.range = 1000
        scene.visible = True
        scene.select()
        self.physicalObjectCollection = self.get_initial_conditions()
        self.start()

    # TODO This will load in some file in the future.
    def get_initial_conditions(self):
        global now
        point1 = SpaceTimePosition(0, 0, 0, now)
        point2 = SpaceTimePosition(0, 0, 0, now + 60) # stay alive for 60 seconds
        trajectory = [point1, point2]
        testObj = TestObjectFactory(self, nextID, trajectory)
        physicalObjectCollection = [testObj]
        return physicalObjectCollection

    # called on each view dt
    def step(self):
        # not sure if real_t_step is needed, vpython has built in rate()
        # that may account for the functionality I was thinking.
        # TODO need to know more.
        real_t = time.time() # this will be needed for logging
        global now
        now = now + self.dt
        view.rate(1/self.dt)
        if len(self.physicalObjectCollection) == 0:
            return False
        for obj in self.physicalObjectCollection:
            if obj.trajectory[-1].t < now: # obj died
                # TODO implement death event for this so model has control.
                self.physicalObjectCollection.remove(obj)
                obj.visualModel.visible = False
                del obj.visualModel # TODO this doesn't work we will need a pool
                break
            obj.fire_events()
            objPos = obj.get_position()
            obj.visualModel.pos = objPos.sPos
        return True

    def start(self):
        running = True
        global epoch
        epoch = time.time()
        global now
        now = 0
        self.get_initial_conditions()
        while (running):
            # The view (vpython) conveniently controls the rate.
            # TODO implement our own rate to decouple (asyncio).
            running = self.step()

if __name__ == "__main__":
    rte = RealTimeEngin()
    rte.start()
