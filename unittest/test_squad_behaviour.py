import unittest

from steer.formation import FormationDiamond
from steer.movable_entity import MovableEntity
from steer.squad import Squad
from steer.squad_behaviour import wander


class TestSquadBehaviour(unittest.TestCase):
    def test_wander(self):
        s1 = Squad()
        s1.entities = [MovableEntity() for _ in range(3)]
        s1.formation = FormationDiamond()
        s1.squad_behaviour = wander(s1, 30, 800, 800)

        # Leader will seek the middle of the screen, with default force of 30 in 1 sec it should travel
        # from (0,0) to (waypoint(400,400)-pos(0,0)).normalized * 30 / 10(mass) = (2.1213, 2.1213)
        s1.update_squad_behaviour(dt=1)
        self.assertAlmostEqual(s1.entities[0].pos.x, 2.1213, places=4)
        self.assertAlmostEqual(s1.entities[0].pos.y, 2.1213, places=4)
        # since the formation is diamond, than the second entity should be offset by -25, -25 from the leader
        e2_formation_pos = s1.get_position_delta(s1.entities[1], s1.entities[0])
        self.assertEqual(e2_formation_pos.x, -25)
        self.assertEqual(e2_formation_pos.y, -25)
        # The second entity should follow the leader unless it's distance is within 35 pixel and than it evades
        # which will lead his in the exact opposite direction
        self.assertAlmostEqual(s1.entities[1].pos.x, -2.1213, places=4)
        self.assertAlmostEqual(s1.entities[1].pos.y, -2.1213, places=4)


if __name__ == '__main__':
    unittest.main()
