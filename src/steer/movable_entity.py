from __future__ import annotations
import abc
from infra.vmath import Vector, get_angle_from


class Targetable(abc.ABC):
    def __init__(self, v: Vector = Vector()):
        self.pos: Vector = v
        self.velocity: Vector = Vector()


class Waypoint(Targetable):
    @staticmethod
    def NAWaypoint():  # noqa: N802
        return Vector(0, 0)


class MovableEntity(Targetable):
    def __init__(self, v: Vector = Vector()):
        Targetable.__init__(self, v)
        self.is_active = True
        self.max_force: float = 30.0
        self.max_speed: float = 80.0
        self.rotation: float = 0.0
        self.mass: float = 10.0
        self.steer_force = None
        self.target = None

    def __repr__(self) -> str:
        return f"MovableEntity({self.pos})"
    
    def shift(self, shift_by: float) -> Waypoint:
        return Waypoint(self.pos + shift_by)

    def update_steer_behaviour(self, dt: float) -> MovableEntity:
        if self.steer_force is None or self.target is None:  # type: ignore
            return self
        
        force = self.steer_force.f(self, self.target).truncate(self.max_force) / self.mass  # type: ignore
        self.velocity = (self.velocity + force).truncate(self.max_speed)
        self.pos = self.pos + (self.velocity * dt)
        angle = get_angle_from(self.velocity, Vector.zero())
        if angle is not None:
            self.rotation = angle  # + math.pi / 2
        return self
        
