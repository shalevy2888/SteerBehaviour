from squad import Squad, SquadForceFunc
from steer_behaviour import follow, separation, seek
from steer_behaviour import wander as steer_wander
from movable_entity import MovableEntity, Waypoint
from vmath import Vector
from typing import Optional

class SquadBehaviour:
    def __init__(self, _f: Optional[SquadForceFunc] = None):
        self.f = _f

    def __call__(self):
        if self.f is not None:
            return self.f()

def set_entities_follow_target(squad: Squad, leader: MovableEntity, follow_front_entity: bool):
    for entity in squad.activeIter():
        if entity is not leader:
            formation_vector = Vector.zero()
            if follow_front_entity is True:
                entity_in_front = squad.getMemberInFrontOf(entity)
                if entity_in_front is not None:
                    formation_vector = squad.getPositionDelta(entity, entity_in_front)
                    entity.target = entity_in_front
            else:
                formation_vector = squad.getPositionDelta(entity, leader)
                entity.target = leader

            entity.steerForce = follow(formation_vector) + separation(squad)


def wander(squad, xymin, width, height):
    leader = None
    seek_waypoint = False

    def squad_force():
        nonlocal leader
        nonlocal seek_waypoint
        new_leader = squad.get_leader()
        if new_leader is not leader:
            if leader is None:
                new_leader.steer_force = steer_wander()
            else:
                new_leader.steer_force = leader.steer_force  # type: ignore
            new_leader.target = MovableEntity.Waypoint.NAWaypoint()
            set_entities_follow_target(squad, new_leader, False)
            leader = new_leader

        if leader is None:
            return

        if leader.pos.x < xymin or leader.pos.x > (width - xymin) or \
                leader.pos.y < xymin or leader.pos.y > (height - xymin):
            leader.target = MovableEntity.Waypoint(Vector(width / 2, height / 2))
            leader.steerForce = seek(0)
            seek_waypoint = True
        elif seek_waypoint is True:
            leader.steerForce = steer_wander()
            leader.target = Waypoint.NAWaypoint()
            seek_waypoint = False
    
    return SquadBehaviour(squad_force)