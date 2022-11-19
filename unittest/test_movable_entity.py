from movable_entity import MovableEntity
import unittest

from vmath import Vector

class TestMovableEntity(unittest.TestCase):
    
    def test_Entity(self):
        e = MovableEntity()
        self.assertEqual(e.update_steer_behaviour(1).velocity, Vector.zero())
        w1 = e.shift(Vector(1, 1))
        self.assertEqual(w1.pos, Vector(1, 1))

if __name__ == '__main__':
    unittest.main()
