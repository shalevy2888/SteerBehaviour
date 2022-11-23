from __future__ import annotations

import abc
import math
from itertools import count

from infra.vmath import get_angle_from
from infra.vmath import Vector


class Targetable(abc.ABC):
    id = count(0)

    def __init__(self, v: Vector = Vector()):
        self.name = f'e{next(Targetable.id)}'
        self.pos: Vector = v
        self.velocity: Vector = Vector()


class Waypoint(Targetable):
    @staticmethod
    def NAWaypoint():  # noqa: N802
        return Vector(0, 0)


class MovableEntity(Targetable):
    def __init__(self, v: Vector = Vector()):
        Targetable.__init__(self, v)
        # print(self.name)
        self.is_active = True
        self.max_force: float = 30.0
        self.max_speed: float = 80.0
        self.speed_mul: float = 1.0  # to be used when following
        self.rotation: float = 0.0
        self.mass: float = 10.0
        self.steer_force = None
        self.target = None

    def __repr__(self) -> str:
        return f"MovableEntity({self.pos})"

    def shift(self, shift_by: float) -> Waypoint:
        return Waypoint(self.pos + shift_by)

    def update_steer_behaviour(self, dt: float) -> MovableEntity:
        if self.steer_force is None or self.target is None:  # type: ignore[unreachable]
            return self

        force = self.steer_force.f(self, self.target).truncate(self.max_force) / self.mass  # type: ignore[unreachable]
        self.velocity = (self.velocity + force).truncate(
            self.max_speed * self.speed_mul
        )
        self.speed_mul = 1.0  # speed_mul needs to be reapplied by the force function
        self.pos = self.pos + (self.velocity * dt)
        angle = get_angle_from(self.velocity, Vector.zero())
        if angle is not None:
            self.rotation = angle + math.pi / 2
        return self
