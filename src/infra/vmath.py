from __future__ import annotations

import math

from steer.globals import FAST_CHECK_INTERSECTION


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

    def __abs__(self):
        return (self.x * self.x + self.y * self.y) ** 0.5

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

    def rotate(self, angle: float) -> Vector:
        return Vector(
            (self.x * math.cos(angle)) - (self.y * math.sin(angle)),
            (self.x * math.sin(angle)) + (self.y * math.cos(angle)),
        )


class Rect:
    def __init__(self, x: float, y: float, width: float, height: float):
        self.x = x
        self.y = y
        self.width = width
        self.height = height


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


def point_on_segment(seg_start: Vector, seg_end: Vector, point: Vector) -> bool:
    min_x = min(seg_start.x, seg_end.x)
    max_x = max(seg_start.x, seg_end.x)
    if point.x < min_x or point.x > max_x:
        return False
    min_y = min(seg_start.y, seg_end.y)
    max_y = max(seg_start.y, seg_end.y)
    if point.y < min_y or point.y > max_y:
        return False

    return True


def sign(x: float) -> float:
    if x < 0:
        return -1
    return 1


def line_segment_intersect_circle(
    pos1: Vector, pos2: Vector, center: Vector, radius: float
) -> bool:
    pos1t = pos1 - center
    pos2t = pos2 - center
    dx = pos2t.x - pos1t.x
    dy = pos2t.y - pos2t.y
    dr2 = dx * dx + dy * dy
    d = pos1t.x * pos2t.y - pos2t.x * pos1t.y
    delta = (radius * radius * dr2) - (d * d)
    if delta < 0 or dr2 == 0:
        return False

    # find the points
    intersect1: Vector = Vector.zero()
    intersect2: Vector = Vector.zero()

    part_x = sign(dy) * dx * math.sqrt(delta)
    part_x2 = d * dy
    intersect1.x = (part_x2 + part_x) / dr2
    intersect2.x = (part_x2 - part_x) / dr2

    part_y = abs(dy) * math.sqrt(delta)
    part_y2 = -d * dx
    intersect1.y = (part_y2 + part_y) / dr2
    intersect2.y = (part_y2 - part_y) / dr2

    if point_on_segment(pos1, pos2, intersect1) is True:
        return True

    if point_on_segment(pos1, pos2, intersect2) is True:
        return True

    return False


def did_reach_target(
    current_pos: Vector, prev_pos: Vector, target: Vector, radius: float
) -> bool:
    if FAST_CHECK_INTERSECTION is True:
        if (current_pos - target).length() < radius:
            return True
    else:
        if (current_pos - target).length() < radius:
            return True
        if (
            line_segment_intersect_circle(
                current_pos, pos2=prev_pos, center=target, radius=radius
            )
            is True
        ):
            return True
    return False
