import unittest
from steer.movable_entity import MovableEntity, Waypoint
from steer.steer_behaviour import seek, flee, wander, pursuit
from infra.vmath import Vector

class TestSteerBehaviour(unittest.TestCase):
    
    def test_seek(self):
        w = Waypoint(Vector(3, 4))
        e = MovableEntity(Vector(1, 1))
        slow_radius_factor = 1.1
        f = seek((w.pos - e.pos).length() * slow_radius_factor)
        # print(f(e,w).length()
        self.assertAlmostEqual(f(e, w).length(), e.max_force / slow_radius_factor)
        w.pos = Vector(30, 9)  # change only the waypoint, expecting to get the full max speed
        self.assertAlmostEqual(f(e, w).length(), e.max_force)
        f = seek((w.pos - e.pos).length() * slow_radius_factor)  # getting the force function again with new slow radius
        self.assertAlmostEqual(f(e, w).length(), e.max_force / slow_radius_factor)

    def test_adding_forces(self):
        w = Waypoint(Vector(30, 9))
        e = MovableEntity(Vector(1, 1))
        f1 = seek(20)
        f2 = seek(30)
        f3 = f1 + f2
        self.assertAlmostEqual(f3(e, w).length(), e.max_force * 2)
    
    def test_multiply_force_with_scalar(self):
        w = Waypoint(Vector(30, 9))
        e = MovableEntity(Vector(1, 1))
        f1 = seek(20)
        f4 = f1 * 3
        self.assertAlmostEqual(f4(e, w).length(), e.max_force * 3)
    
    def test_flee(self):
        w = Waypoint(Vector(3, 4))
        e = MovableEntity(Vector(1, 1))
        f5 = flee()
        self.assertAlmostEqual(f5(e, w).length(), e.max_force)

    def test_pursuit(self):
        w = Waypoint(Vector(3, 4))
        e = MovableEntity(Vector(1, 1))
        f6 = pursuit()
        w.velocity = Vector(-15, 0)
        print(f6(e, w))
    
    def test_wander(self):
        # w = Waypoint(Vector(3, 4))
        e = MovableEntity(Vector(1, 1))
        f7 = wander()
        print(f7(e, None))
        print(f7(e, None))
        print(f7(e, None))
    
    def test_update_steer_behaviour(self):
        w = Waypoint(Vector(3, 4))
        e = MovableEntity(Vector(1, 1))
        e.steer_force = seek(1)
        e.target = w
        e.update_steer_behaviour(0.1)
        self.assertAlmostEqual(e.velocity.length(),
                               ((w.pos - e.pos).normalize()
                                * e.max_force * 0.1).length())

if __name__ == '__main__':
    unittest.main()
