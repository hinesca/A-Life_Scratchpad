# A-Life Scratchpad

This is a space for trying out new ideas related to Artificial Life.

## Simulator Core Architecture

The sim core will be prototyped in python. It will provide an API to be used with an abstract visualization project, an event logger, and a custom real time event system to interface with an abstract model project.

It will hold a collection of all of the simulation model objects. On initialization, it will initialize an abstract model object that represents the initial conditions of the simulation. It will schedule abstract events defined by the model objects, and detect collisions that will trigger an abstract interaction between colliding objects.

## Model Architecture

The model will start from of a class who's constructor will initialize the initial conditions of the simulation by instantiating all of the physical object models needed to start the particular simulation.

The physical object models will store their own state information in private backing fields and have methods (or properties) that calculate the future or current state of the object based on the stored intermediate state. For example, the abstract class (or interface) for physical object models will require each object model to implement a GetPosition method that returns it's position (or implement a property to do the same thing). If the object moves, there will be a state variable (backing field) for the trajectory of the object over time. This may be in the form of an equation or a list of positions tracing a path. The position at any given time can then be calculated from this intermediate trajectory. This will avoid having the need to calculate the state of each model object on each time step in the simulation which may be very small.


