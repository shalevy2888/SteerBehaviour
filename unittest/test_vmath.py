import math
import unittest

from infra.vmath import angle_between
from infra.vmath import Vector


class TestVmath(unittest.TestCase):
    def test_length(self):
        self.assertEqual(Vector(3, 4).length(), 5)

    def test_normalized(self):
        self.assertAlmostEqual(1, Vector(3, 4).normalize().length())

    def test_angle_between(self):
        self.assertAlmostEqual(
            angle_between(Vector(0, 1), Vector(1, 1)), math.pi / 4, places=2
        )
        self.assertAlmostEqual(
            angle_between(Vector(0, 1), Vector(1, 0)), math.pi / 2, places=2
        )
        self.assertAlmostEqual(
            angle_between(Vector(0, 1), Vector(-1, 0)), math.pi / 2, places=2
        )
        self.assertAlmostEqual(angle_between(Vector(0, 1), Vector(0, 1)), 0, places=2)
        self.assertAlmostEqual(
            angle_between(Vector(0, 1), Vector(0, -1)), math.pi, places=2
        )
        self.assertAlmostEqual(
            angle_between(Vector(0, 1), Vector(1, -1)), math.pi / 4 * 3, places=2
        )
        self.assertAlmostEqual(
            angle_between(Vector(0, 1), Vector(-1, -1)), math.pi / 4 * 3, places=2
        )
        self.assertAlmostEqual(
            angle_between(Vector(0, 1), Vector(-4, -4)), math.pi / 4 * 3, places=2
        )
        self.assertAlmostEqual(
            angle_between(Vector(0, 10), Vector(-4, -4)), math.pi / 4 * 3, places=2
        )


if __name__ == '__main__':
    unittest.main()
