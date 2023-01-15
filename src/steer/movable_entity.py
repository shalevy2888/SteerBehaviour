from __future__ import annotations

import abc
import math
from itertools import count
from typing import Any

from infra.vmath import get_angle_from
from infra.vmath import Vector
from steer.globals import speed_mul_target_steps
from steer.globals import velocity_decay_max

# from infra.vmath import sign


class Targetable(abc.ABC):
    id = count(0)

    def __init__(self, v: Vector = Vector()):
        self.name = f'e{next(Targetable.id)}'
        self.pos: Vector = v
        self.velocity: Vector = Vector()
        self.prev_pos: Vector = v


class Waypoint(Targetable):
    @staticmethod
    def NAWaypoint():  # noqa: N802
        return Waypoint(Vector(0, 0))


class MovableEntity(Targetable):
    def __init__(self, v: Vector = Vector()):
        Targetable.__init__(self, v)
        # print(self.name)
        self.is_active = True
        self._max_force: float = 30.0
        self.max_speed: float = 80.0
        self.speed_mul_target: float = 1.0  # to be used when following / seek
        self.force_mul_target: float = 1.0  # to be used when following / seek
        self.rotation: float = 0.0
        self._mass: float = 10.0
        self.steer_force: Any = None
        self.target: None | Targetable = None

        self._speed_mul: float = 1.0
        self._speed_mul_steps: float = speed_mul_target_steps
        self._force_mul: float = 1.0
        self._calculate_velocity_decay()

    def __repr__(self) -> str:
        return f"MovableEntity({self.pos})"

    def _calculate_velocity_decay(self):
        max_velocity_per_update: float = self.max_force / self.mass
        self._velocity_decay = min(
            velocity_decay_max, (max_velocity_per_update / 2) / self.max_speed
        )

    @property
    def max_force(self) -> float:
        return self._max_force

    @max_force.setter
    def max_force(self, mf: float) -> None:
        self._max_force = min(mf, self.max_speed * self.mass)
        self._calculate_velocity_decay()

    @property
    def mass(self) -> float:
        return self._mass

    @mass.setter
    def mass(self, m: float) -> None:
        self._mass = max(m, self.max_force / self.max_speed)
        self._calculate_velocity_decay()

    def shift(self, shift_by: Vector) -> Waypoint:
        return Waypoint(self.pos + shift_by)

    def update_steer_behaviour(self, dt: float) -> MovableEntity:
        if self.steer_force is None or self.target is None:
            return self

        self._force_mul += (
            self.force_mul_target - self._force_mul
        ) * self._speed_mul_steps
        self.force_mul_target = (
            1.0  # force_mul_target needs to be reapplied by the force function
        )

        force = (
            self.steer_force.f(self, self.target).truncate(
                self.max_force * self._force_mul
            )
            / self.mass
        )

        self._speed_mul += (
            self.speed_mul_target - self._speed_mul
        ) * self._speed_mul_steps

        # print(self.name, self.speed_mul_target, self._speed_mul)

        self.velocity = (self.velocity * (1 - self._velocity_decay) + force).truncate(
            self.max_speed * self._speed_mul
        )
        self.speed_mul_target = (
            1.0  # speed_mul_target needs to be reapplied by the force function
        )

        self.prev_pos = self.pos
        self.pos = self.pos + (self.velocity * dt)
        angle = get_angle_from(self.velocity, Vector.zero())
        if angle is not None:
            self.rotation = angle + math.pi / 2
        return self
