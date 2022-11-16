import math


class Vector:
    def __init__(self, _x=0, _y=0):
        self.x = _x
        self.y = _y

    @staticmethod
    def zero():
        return Vector(0, 0)

    def length(self):
        return math.sqrt(self.x**2 + self.y**2)

    def sqrLength(self):
        return self.x**2 + self.y**2

    def truncate(self, v):
        l = self.length()
        if (l>v):
            return (self / l) * v
        return self

    def normalize(self):
        try:
            n = 1 / self.length()
        except ZeroDivisionError:
            return Vector(0, 0)
        return self * n

    def __add__(self, other):
        return Vector(self.x + other.x, self.y + other.y)

    def __sub__(self, other):
        return Vector(self.x - other.x, self.y - other.y)

    def __mul__(self, scalar):
        return Vector(self.x * scalar, self.y * scalar)
    
    def __truediv__(self, scalar):
        return Vector(self.x / scalar, self.y / scalar)

    def __eq__(self, other):
        if (other is None): return False
        return self.x == other.x and self.y == other.y

    def __repr__(self):
        return f"Vector({self.x},{self.y})"

    def eqEpsilon(self, other, epsilon=0.001):
        return math.isclose(
            self.x, other.x, abs_tol=epsilon) and math.isclose(
                self.y, other.y, abs_tol=epsilon)

    def setAngle(self, angle):
        return Vector(math.cos(angle)*self.length(), math.sin(angle)*self.length())


def getAngleFrom(newPosition, oldPosition):
    ydt = newPosition.y - oldPosition.y
    xdt = newPosition.x - oldPosition.x

    angle = 0
    if (ydt != 0 and xdt != 0):
        hyp = math.sqrt(math.pow(xdt, 2)+math.pow(ydt, 2))
        if (ydt >= 0):
            angle = math.asin(ydt/hyp)
            if (xdt <0):
                angle += 2*(math.pi/2 - angle)
        else:
            angle = math.asin((-ydt)/hyp)
            if (xdt <0):
                angle += math.pi
            else:
                angle = 2*math.pi-angle
    else:
        return None

    return angle

