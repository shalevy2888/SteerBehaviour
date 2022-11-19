from steer.formation import FormationDiamond, FormationColumn, Formation
import unittest

from infra.vmath import Vector

class TestFormation(unittest.TestCase):
    
    def test_Diamond(self):
        f = FormationDiamond()
        self.assertEqual(f.entity_position(5), Vector(50, -50))

    def test_IndexError(self):
        f = FormationDiamond()
        with self.assertRaises(IndexError):
            f.entity_position(10)

    def test_scale(self):
        f = FormationDiamond()
        f.scale = 2
        self.assertEqual(f.entity_position(5), Vector(100, -100))

    def test_rotate(self):
        self.assertEqual(Formation.rotate(Vector(0, 0), 90), Vector(0, 0))
        self.assertAlmostEqual(Formation.rotate(Vector(1, 0), 90).x, 0)
        self.assertAlmostEqual(Formation.rotate(Vector(1, 0), 90).y, 1)

    def test_Column(self):
        f1 = FormationColumn()
        self.assertEqual(f1.entity_position(5), Vector(0, -150))

if __name__ == '__main__':
    unittest.main()
