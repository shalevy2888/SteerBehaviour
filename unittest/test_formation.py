import math
import unittest

from infra.vmath import Vector
from steer.formation import Formation
from steer.formation import FormationColumn
from steer.formation import FormationDiamond


class TestFormation(unittest.TestCase):
    def test_diamond(self):
        f = FormationDiamond()
        self.assertEqual(f.entity_position(5), Vector(50, -50))

    def test_index_error(self):
        f = FormationDiamond()
        with self.assertRaises(IndexError):
            f.entity_position(10)

    def test_scale(self):
        f = FormationDiamond()
        f.scale = 2
        self.assertEqual(f.entity_position(5), Vector(100, -100))

    def test_rotate(self):
        self.assertEqual(Formation.rotate(Vector(0, 0), math.radians(90)), Vector(0, 0))
        self.assertAlmostEqual(Formation.rotate(Vector(1, 0), math.radians(90)).x, 0)
        self.assertAlmostEqual(Formation.rotate(Vector(1, 0), math.radians(90)).y, 1)

    def test_column(self):
        f1 = FormationColumn()
        self.assertEqual(f1.entity_position(5), Vector(0, -150))


if __name__ == '__main__':
    unittest.main()
