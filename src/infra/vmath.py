from __future__ import annotations

import math


class Vector:
    def __init__(self, x: float = 0, y: float = 0):
        self.x = x
        self.y = y

    @staticmethod
    def zero() -> Vector:
        return Vector(0, 0)

    def length(self) -> float:
        return math.sqrt(self.x**2 + self.y**2)

    def sqr_length(self) -> float:
        return self.x**2 + self.y**2

    def truncate(self, v: float) -> Vector:
        ln = self.length()
        if ln > v:
            return (self / ln) * v
        return self

    def normalize(self) -> Vector:
        try:
            n = 1 / self.length()
        except ZeroDivisionError:
            return Vector(0, 0)
        return self * n

    def __add__(self, other: Vector) -> Vector:
        return Vector(self.x + other.x, self.y + other.y)

    def __sub__(self, other: Vector) -> Vector:
        return Vector(self.x - other.x, self.y - other.y)

    def __mul__(self, scalar: float) -> Vector:
        return Vector(self.x * scalar, self.y * scalar)

    def __truediv__(self, scalar: float) -> Vector:
        return Vector(self.x / scalar, self.y / scalar)

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, Vector):
            return NotImplemented
        return (self.x == other.x) and (self.y == other.y)

    def __repr__(self) -> str:
        return f"Vector({self.x:.4f},{self.y:.4f})"

    def almost_eq(self, other: object, epsilon: float = 0.001) -> bool:
        if not isinstance(other, Vector):
            return NotImplemented
        return math.isclose(self.x, other.x, abs_tol=epsilon) and math.isclose(
            self.y, other.y, abs_tol=epsilon
        )

    def set_angle(self, angle: float) -> Vector:
        return Vector(math.cos(angle) * self.length(), math.sin(angle) * self.length())


def get_angle_from(new_position: Vector, old_position: Vector) -> float | None:
    ydt = new_position.y - old_position.y
    xdt = new_position.x - old_position.x

    angle = 0.0
    if ydt != 0 and xdt != 0:
        hyp = math.sqrt(math.pow(xdt, 2) + math.pow(ydt, 2))
        if ydt >= 0:
            angle = math.asin(ydt / hyp)
            if xdt < 0:
                angle += 2 * (math.pi / 2 - angle)
        else:
            angle = math.asin((-ydt) / hyp)
            if xdt < 0:
                angle += math.pi
            else:
                angle = 2 * math.pi - angle
    else:
        return None

    return angle
