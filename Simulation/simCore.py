"""
simCore.py
For A-Life 2.0
Originates from A-Life, 2.0. A CS Capstone project at Oregon State University
"""

# For simplicity and to get a working simulation, we are treating vpython as the view
import vpython as view
import time
import json
from simModelInterface import *

# Simulation Engine
class SimCore:
    def __init__(self):
        scene = view.canvas(x = 0, y = 0, autoscale = False)
        # TODO Remember to clean up magic numbers.
        # These can be controls in the UI.
        self.now = 0
        self.dt = 0.02
        self.epoch = time.time()
        self.nextID = 0
        scene.range = 500
        scene.visible = True
        # TODO placeholders for visual object pool. Need one for each type used in visualization.
        self.visualSpheres = []
        self.visualBoxes = []
        self.visualMeshes = []
        # ...
        scene.select()
        self.start()

    # called on each view dt
    def step(self):
        real_t = time.time() # this will be needed for logging
        self.now = self.now + self.dt
        view.rate(1 / self.dt)
        # copy keys to avoid modifying dct while iterating
        keys = list(self.physicalObjects.keys())
        if len(keys) == 0:
            return False
        for key in keys:
            if self.physicalObjects[key].trajectory[-1].t < self.now: # obj died
                # TODO implement death event for this so model has control.
                self.physicalObjects[key].visualModel.visible = False
                self.physicalObjects[key].visualModel = None # TODO store in pool
                # TODO make a method to store in pool
                del self.physicalObjects[key]
                break
            # TODO handel collisions in method, introduce concept of uncertainty
            self.physicalObjects[key].fire_events(self.now)
            objPos = self.physicalObjects[key].get_position(self.now)
            self.physicalObjects[key].visualModel.pos = objPos.sPos
        return True

    def start(self):
        running = True
        self.physicalObjects = get_initial_conditions(self)
        # Uncomment the below for testing load_simulation
        self.save_simulation("test")
        self.physicalObjects = self.load_simulation("test_A-Life.json")
        while (running):
            # The view (vpython) conveniently controls the rate.
            # TODO implement our own rate to decouple (asyncio).
            running = self.step()

    # loads a simulation into the simCore from a JSON file
    def load_simulation(simCore, filename):
        with open(filename, "r") as json_file:
            serialized = json_file.read()
        physicalObjectsDct = json.loads(serialized)
        physicalObjects = {}
        
        for key in physicalObjectsDct.keys():
            trajectory = []
            for spPos in physicalObjectsDct[key]["trajectory"]:
                thisStPos = SpaceTimePosition(
                spPos["x"],
                spPos["y"],
                spPos["z"],
                spPos["t"])
                trajectory.append(thisStPos)
            po = PhysicalObjectBase(
                simCore,
                physicalObjectsDct[key]["id"],
                trajectory,
                physicalObjectsDct[key]["class_type"])
            schedule = []
            for eventDct in physicalObjectsDct[key]["schedule"]:
                event = globals()[eventDct["event_type"]](eventDct["t"], eventDct["args"])
                schedule.append(event)
            po.schedule = schedule
            physicalObjects[key] = po
        return physicalObjects

    # saves the simulation into a JSON file
    def save_simulation(simCore, name):
        rootDct = {}
        for key in simCore.physicalObjects:
            objDct = {}
            po = simCore.physicalObjects[key]
            objDct["id"] = key
            objDct["trajectory"] = []
            for stPos in po.trajectory:
                posDct = {}
                posDct["x"] = stPos.x
                posDct["y"] = stPos.y
                posDct["z"] = stPos.z
                posDct["t"] = stPos.t
                objDct["trajectory"].append(posDct)
            objDct["class_type"] = type(po).__name__
            schedule = []
            for event in po.schedule:
                eventDct = {}
                eventDct["event_type"] = type(event).__name__
                eventDct["t"] = event.t
                eventDct["args"] = event.args
                schedule.append(eventDct)
            objDct["schedule"] = schedule
            rootDct[key] = objDct
        serialized = json.dumps(rootDct, indent=4)
        
        with open(f"{name}_A-Life.json", "w") as json_file:
            json_file.write(serialized)


if __name__ == "__main__":
    rte = SimCore()
    rte.start()
