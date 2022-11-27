from typing import Callable
from typing import Optional
from typing import Tuple

from infra.vmath import Vector
from steer.movable_entity import MovableEntity
from steer.movable_entity import Targetable
from steer.movable_entity import Waypoint
from steer.path import Path
from steer.squad import Squad
from steer.squad import SquadForceFunc
from steer.squad_behaviour_condition import CondRes
from steer.squad_behaviour_condition import SquadBehaviourCondition
from steer.steer_behaviour import follow
from steer.steer_behaviour import path as steer_path
from steer.steer_behaviour import PathBehaviourWhenDone
from steer.steer_behaviour import seek
from steer.steer_behaviour import separation
from steer.steer_behaviour import SteeringForce
from steer.steer_behaviour import wander as steer_wander


class SquadBehaviour:
    def __init__(self, _f: Optional[SquadForceFunc] = None):
        self.f = _f

    def __call__(self, restart: bool, dt: float):
        if self.f is not None:
            return self.f(restart, dt)


def is_new_leader(
    cur_leader: MovableEntity | None, squad: Squad
) -> MovableEntity | None:
    if cur_leader is None or cur_leader is not squad.get_leader():
        return squad.get_leader()

    return None


def set_leader_steer(
    leader: MovableEntity | None,
    squad: Squad,
    steer: SteeringForce,
    target: Targetable,
    follow_front_entity: bool,
) -> Tuple[MovableEntity, CondRes]:
    new_leader = is_new_leader(leader, squad)
    if new_leader is not None:
        if leader is None:
            new_leader.steer_force = steer
        else:
            new_leader.steer_force = leader.steer_force

        new_leader.target = target
        if follow_front_entity is False:
            set_entities_follow_target(
                squad=squad, leader=new_leader, follow_front_entity=False
            )

        leader = new_leader

    if leader is None:
        assert (
            squad.getSquadCount() == 0
        ), "Squad cannot have no leader when count is >0"
        return (None, CondRes(CondRes.abort))

    if follow_front_entity is True:
        # This is needed incase one fo the entities in the squad (not only the leader) becomes inActive
        set_entities_follow_target(squad=squad, leader=leader, follow_front_entity=True)
    return (leader, CondRes(CondRes.not_met))


def set_entities_follow_target(
    squad: Squad, leader: MovableEntity, follow_front_entity: bool
):
    for entity in squad.active_iter():
        if entity is not leader:
            formation_vector = Vector.zero()
            if follow_front_entity is True:
                entity_in_front = squad.get_member_in_front_of(entity)
                if entity_in_front is not None:
                    formation_vector = squad.get_position_delta(entity, entity_in_front)
                    entity.target = entity_in_front
            else:
                formation_vector = squad.get_position_delta(entity, leader)
                entity.target = leader

            entity.steer_force = follow(formation_vector) + separation(squad)


restart_function = Callable[[], None]


def check_condition(
    restart_needed: bool,
    dt: float,
    cond: SquadBehaviourCondition,
    res_func: restart_function,
) -> CondRes:
    if restart_needed is True:
        res_func()
        cond.check(True, 0)
        return CondRes(CondRes.met)  # The return isn't checked in case of restart
    return cond.check(restart_needed, dt)


def wander(squad, xymin, width, height):
    leader: MovableEntity = None
    seek_waypoint: Waypoint = False

    def squad_force(restart: bool, dt: float):
        nonlocal leader
        nonlocal seek_waypoint
        new_leader = squad.get_leader()
        if new_leader is not leader:
            if leader is None:
                new_leader.steer_force = steer_wander()
            else:
                new_leader.steer_force = leader.steer_force
            new_leader.target = Waypoint.NAWaypoint()
            set_entities_follow_target(squad, new_leader, False)
            leader = new_leader

        if leader is None:
            return
        if (
            leader.pos.x < xymin
            or leader.pos.x > (width - xymin)
            or leader.pos.y < xymin
            or leader.pos.y > (height - xymin)
        ):
            if seek_waypoint is False:
                leader.target = Waypoint(Vector(width / 2, height / 2))
                leader.steer_force = seek(0)
                seek_waypoint = True
            # print('seek', leader.target.pos, leader.pos)
        elif seek_waypoint is True:
            leader.steer_force = steer_wander()
            leader.target = Waypoint.NAWaypoint()
            seek_waypoint = False
            # print('wander', leader.pos)

    return SquadBehaviour(squad_force)


def path(
    cond: SquadBehaviourCondition, path: Path, squad: Squad, follow_front: bool
) -> SquadBehaviour:
    leader: MovableEntity | None = None
    weak_squad = squad

    def squad_force(restart: bool, dt: float) -> CondRes:
        nonlocal leader, weak_squad

        def res_func():
            nonlocal leader
            leader = None

        res = check_condition(restart, dt=dt, cond=cond, res_func=res_func)
        if res != CondRes(CondRes.not_met):
            return res

        (leader, cond_res) = set_leader_steer(
            leader,
            weak_squad,
            steer_path(
                path,
                PathBehaviourWhenDone(PathBehaviourWhenDone.return_to_beginning),
                0,
            ),
            Waypoint.NAWaypoint(),
            follow_front,
        )
        return cond_res

    return SquadBehaviour(squad_force)
