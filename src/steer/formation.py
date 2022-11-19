import math
from infra.vmath import Vector

class Formation:
    def __init__(self):
        self.scale: float = 1.0
        self.count: int = 0

    def _unscaled_entity_position(self, num):
        return Vector.zero()

    def entity_position(self, num):
        if (num>=self.count):
            raise IndexError
        return self._unscaled_entity_position(num) * self.scale

    @staticmethod
    def rotate(v: Vector, rotation: float) -> Vector:
        """ Rotate a vector around 0,0 by degrees rotation """
        rotation = math.radians(rotation)
        return Vector(v.x * math.cos(rotation) - v.y * math.sin(rotation),
                      v.x * math.sin(rotation) + v.y * math.cos(rotation))

class FormationDiamond(Formation):
    def __init__(self):
        Formation.__init__(self)
        self._positions = [
            Vector(0, 0),
            Vector(-25, -25),
            Vector(25, -25),
            Vector(0, -50),
            Vector(0, -75),
            Vector(50, -50),
            Vector(-50, -50),
            Vector(-25, -75),
            Vector(25, -75),
            Vector(0, -100)]
        self.count = 10
    
    def _unscaled_entity_position(self, num: int):
        if (num >= self.count):
            raise IndexError
        return self._positions[num]

class FormationColumn(Formation):
    def __init__(self):
        Formation.__init__(self)
        self.count: int = 10
        self._positions = [Vector(0, -30 * i) for i in range(self.count)]
    
    def _unscaled_entity_position(self, num):
        if (num>=self.count):
            raise IndexError
        return self._positions[num]
