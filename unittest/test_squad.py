from steer.squad import Squad
from steer.formation import FormationDiamond
from steer.movable_entity import MovableEntity
import unittest

from infra.vmath import Vector

class TestSquad(unittest.TestCase):
    
    def test_append(self):
        s = Squad()
        s.formation = FormationDiamond()
        e1 = MovableEntity(Vector(1, 1))
        e2 = MovableEntity(Vector(2, 2))
        e3 = MovableEntity(Vector(3, 3))
        e4 = MovableEntity(Vector(4, 4))
        e5 = MovableEntity(Vector(5, 5))
        
        s.entities.append(e1)
        s.entities.append(e2)
        s.entities.append(e3)
        s.entities.append(e4)
        s.entities.append(e5)

        self.assertEqual(s.count(), 5)

    def test_get_by_index(self):
        s = Squad()
        s.formation = FormationDiamond()
        e1 = MovableEntity(Vector(1, 1))
        e2 = MovableEntity(Vector(2, 2))
        e3 = MovableEntity(Vector(3, 3))
        e4 = MovableEntity(Vector(4, 4))
        e5 = MovableEntity(Vector(5, 5))
        
        s.entities.append(e1)
        s.entities.append(e2)
        s.entities.append(e3)
        s.entities.append(e4)
        s.entities.append(e5)

        self.assertEqual(s.get_entity_by_index(0), e1)
        self.assertEqual(s.get_entity_by_index(1), e2)
        self.assertEqual(s.get_entity_by_index(6), None)

    def test_Member_in_front(self):
        s=Squad()
        s.formation = FormationDiamond()
        e1 = MovableEntity(Vector(1, 1))
        e2 = MovableEntity(Vector(2, 2))
        e3 = MovableEntity(Vector(3, 3))
        e4 = MovableEntity(Vector(4, 4))
        e5 = MovableEntity(Vector(5, 5))
        
        s.entities.append(e1)
        s.entities.append(e2)
        s.entities.append(e3)
        s.entities.append(e4)
        s.entities.append(e5)
        self.assertEqual(s.get_member_in_front_of(e2), e1)
        self.assertEqual(s.get_member_in_front_of(e5), e4)
        self.assertEqual(s.get_member_in_front_of(e4), e3)

    def test_leader(self):
        s=Squad()
        s.formation = FormationDiamond()
        e1 = MovableEntity(Vector(1, 1))
        e2 = MovableEntity(Vector(2, 2))
        e3 = MovableEntity(Vector(3, 3))
        e4 = MovableEntity(Vector(4, 4))
        e5 = MovableEntity(Vector(5, 5))
        
        s.entities.append(e1)
        s.entities.append(e2)
        s.entities.append(e3)
        s.entities.append(e4)
        s.entities.append(e5)
        # print(s.getLeader())
        # Not a good assert since it rely on the repr definition.
        self.assertEqual(repr(s.get_leader()), "MovableEntity(Vector(1.0000,1.0000))")
        self.assertEqual(repr(s.get_leader()), "MovableEntity(Vector(1.0000,1.0000))")  # making sure a second call doesn't change the result
        
    def test_position_delta(self):
        s=Squad()
        s.formation = FormationDiamond()
        e1 = MovableEntity(Vector(1, 1))
        e2 = MovableEntity(Vector(2, 2))
        e3 = MovableEntity(Vector(3, 3))
        e4 = MovableEntity(Vector(4, 4))
        e5 = MovableEntity(Vector(5, 5))
        
        s.entities.append(e1)
        s.entities.append(e2)
        s.entities.append(e3)
        s.entities.append(e4)
        s.entities.append(e5)
        self.assertEqual(s.get_position_delta(e1), Vector(0, 0))
        self.assertEqual(s.get_position_delta(e4), Vector(0, -50))
    
    def test_get_index(self):
        s=Squad()
        s.formation = FormationDiamond()
        e1 = MovableEntity(Vector(1, 1))
        e2 = MovableEntity(Vector(2, 2))
        e3 = MovableEntity(Vector(3, 3))
        e4 = MovableEntity(Vector(4, 4))
        e5 = MovableEntity(Vector(5, 5))
        
        s.entities.append(e1)
        s.entities.append(e2)
        s.entities.append(e3)
        s.entities.append(e4)
        s.entities.append(e5)
        self.assertEqual(s.get_index_of_entity(e3), 2)
    
    def test_active(self):
        s=Squad()
        s.formation = FormationDiamond()
        e1 = MovableEntity(Vector(1, 1))
        e2 = MovableEntity(Vector(2, 2))
        e3 = MovableEntity(Vector(3, 3))
        e4 = MovableEntity(Vector(4, 4))
        e5 = MovableEntity(Vector(5, 5))
        
        s.entities.append(e1)
        s.entities.append(e2)
        s.entities.append(e3)
        s.entities.append(e4)
        s.entities.append(e5)
        e1.is_active = False
        e2.is_active = False
        self.assertEqual(s.get_member_in_front_of(e2), None)
        self.assertEqual(s.get_member_in_front_of(e3), None)
        self.assertEqual(s.get_member_in_front_of(e4), e3)
        self.assertEqual(s.get_index_of_entity(e3), 0)
        self.assertEqual(s.get_position_delta(e4), Vector(-25, -25))
        self.assertEqual(s.get_position_delta(e1), Vector(0, 0))
        self.assertEqual(s.get_position_delta(e4, e5), Vector(-50, 0))
        self.assertEqual(repr(s.get_leader()), "MovableEntity(Vector(3.0000,3.0000))")

        self.assertEqual(s.get_entity_by_index(0), e3)

        e3.is_active = False
        e4.is_active = False
        e5.is_active = False
        self.assertEqual(repr(s.get_leader()), "None")

if __name__ == '__main__':
    unittest.main()
