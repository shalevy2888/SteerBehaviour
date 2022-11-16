import abc
import vmath
import math
from vmath import Vector


class Targetable(abc.ABC):
    def __init__(self, v=Vector()):
        self.pos = v
        self.velocity = Vector()


class Waypoint(Targetable):
    @staticmethod
    def NAWaypoint():
        return Vector(0, 0)


class MovableEntity(Targetable):
    def __init__(self, v=Vector()):
        Targetable.__init__(self, v)
        self.isActive = True
        self.maxForce = 30
        self.maxSpeed = 80
        self.rotation = 0
        self.mass = 10
        self.steerForce = None
        self.target = None

    def __repr__(self):
        return f"MovableEntity({self.pos})"
    
    def shift(self, shiftBy):
        return Waypoint(self.pos + shiftBy)

    def updateSteerBehaviour(self, dt):
        if self.steerForce is None or self.target is None:
            return self
        
        force = self.steerForce.f(self, self.target).truncate(self.maxForce) / self.mass
        self.velocity = (self.velocity + force).truncate(self.maxSpeed)
        self.pos = self.pos + (self.velocity * dt)
        angle = vmath.getAngleFrom(self.velocity, Vector.zero())
        if angle is not None:
            self.rotation = angle + math.pi / 2
        return self
        
