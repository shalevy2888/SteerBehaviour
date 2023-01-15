from __future__ import annotations

import math
import random
from typing import Callable

from infra.vmath import Rect
from infra.vmath import Vector
from steer.globals import path_leader_seek_radius
from steer.movable_entity import MovableEntity
from steer.movable_entity import Targetable
from steer.movable_entity import Waypoint
from steer.path import circle_path
from steer.path import flower_path_area
from steer.path import in_and_out_path
from steer.path import Path
from steer.path import patrol_path
from steer.path import shift_path
from steer.path import spiral_path
from steer.path import v_path
from steer.squad import Squad
from steer.squad import SquadForceFunc
from steer.squad_behaviour_condition import CondRes
from steer.squad_behaviour_condition import infinite_behaviour_condition
from steer.squad_behaviour_condition import SquadBehaviourCondition
from steer.squad_behaviour_condition import time_elapsed
from steer.steer_behaviour import follow
from steer.steer_behaviour import path as steer_path
from steer.steer_behaviour import PathBehaviourWhenDone
from steer.steer_behaviour import seek
from steer.steer_behaviour import separation
from steer.steer_behaviour import SteeringForce
from steer.steer_behaviour import wander as steer_wander

# from typing import Optional
# from typing import Tuple


class SquadBehaviour:
    def __init__(
        self, _f: SquadForceFunc | None = None, _debug_path: Path | None = None
    ):
        self.f = _f
        self._debug_path = _debug_path

    def __call__(self, restart: bool, dt: float):
        if self.f is not None:
            return self.f(restart, dt)

    # The combined operation returns:
    # CondRes(CondRes.abort) when both l & other operands are not CondRes(CondRes.not_met) and at least one is CondRes(CondRes.abort) -> returns CondRes(CondRes.abort)
    # CondRes(CondRes.met) when either l & other operands -> return CondRes(CondRes.met) (both are finished)
    # CondRes(CondRe_met) in any other
    # l is being executed serially before other
    def __or__(self, other: SquadBehaviour) -> SquadBehaviour:
        self_cond_met: CondRes = CondRes(CondRes.not_met)
        other_cond_met: CondRes = CondRes(CondRes.not_met)

        def squad_force(restart: bool, dt: float) -> CondRes:
            nonlocal self_cond_met
            nonlocal other_cond_met
            if restart is True:
                self_cond_met = CondRes(CondRes.not_met)
                other_cond_met = CondRes(CondRes.not_met)
                self(True, 0)
                other(True, 0)
                return CondRes(CondRes.not_met)

            if self_cond_met == CondRes(CondRes.not_met):
                self_cond_met = self(restart, dt)

            if other_cond_met == CondRes(CondRes.not_met):
                other_cond_met = other(restart, dt)

            if self_cond_met != CondRes(CondRes.not_met) or other_cond_met != CondRes(
                CondRes.not_met
            ):
                if self_cond_met == CondRes(CondRes.abort) or other_cond_met == CondRes(
                    CondRes.abort
                ):
                    return CondRes(CondRes.abort)
                return CondRes(CondRes.met)

            return CondRes(CondRes.not_met)

        return SquadBehaviour(squad_force)

    def __rshift__(self, other: SquadBehaviour) -> SquadBehaviour:
        self_cond_met: CondRes = CondRes(CondRes.not_met)

        def squad_force(restart: bool, dt: float) -> CondRes:
            nonlocal self_cond_met

            if restart is True:
                self_cond_met = CondRes(CondRes.not_met)
                self(True, 0)
                other(True, 0)
                return CondRes(CondRes.not_met)

            if self_cond_met != CondRes(CondRes.not_met):
                if self_cond_met == CondRes(CondRes.abort):
                    return CondRes(CondRes.abort)
                return other(restart, dt)

            self_cond_met = self(restart, dt)
            return CondRes(CondRes.not_met)

        return SquadBehaviour(squad_force)

    def __add__(self, other: SquadBehaviour) -> SquadBehaviour:
        return self >> other

    # In General, 'and' operator means that we need to finish both behaviour
    # to finish the combined operation.
    # 'or' operator means that is enough for one to finish to finish the combined operation.

    # The combined operation returns:
    # met when both l & r operands -> return met (both are finished)
    # abort when both l & r operands are not 'not_met' and at least one
    # is abort -> returns abort
    # 'not_met' in any other case
    # l is being executed serially before r
    def __and__(self, other: SquadBehaviour) -> SquadBehaviour:
        self_cond_met: CondRes = CondRes(CondRes.not_met)
        other_cond_met: CondRes = CondRes(CondRes.not_met)

        def squad_force(restart: bool, dt: float) -> CondRes:
            nonlocal self_cond_met
            nonlocal other_cond_met
            if restart is True:
                self_cond_met = CondRes(CondRes.not_met)
                other_cond_met = CondRes(CondRes.not_met)
                self(True, 0)
                other(True, 0)
                return CondRes(CondRes.not_met)

            if self_cond_met == CondRes(CondRes.not_met):
                self_cond_met = self(restart, dt)

            if other_cond_met == CondRes(CondRes.not_met):
                other_cond_met = other(restart, dt)

            if self_cond_met != CondRes(CondRes.not_met) and other_cond_met != CondRes(
                CondRes.not_met
            ):
                if self_cond_met == CondRes(CondRes.abort) or other_cond_met == CondRes(
                    CondRes.abort
                ):
                    return CondRes(CondRes.abort)
                return CondRes(CondRes.met)

            return CondRes(CondRes.not_met)

        return SquadBehaviour(squad_force)


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
) -> tuple[MovableEntity, CondRes]:
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

            entity.steer_force = follow(formation_vector) + (separation(squad) * 0.5)


restart_definition = Callable[[], None]


def check_condition(
    restart_needed: bool,
    dt: float,
    cond: SquadBehaviourCondition,
    res_def: restart_definition,
) -> CondRes:
    if restart_needed is True:
        res_def()
        cond.check(True, 0)
        return CondRes(CondRes.met)  # The return isn't checked in case of restart
    return cond.check(restart_needed, dt)


def zero_behaviour(cond: SquadBehaviourCondition) -> SquadBehaviour:
    def squad_force(restart: bool, dt: float) -> CondRes:
        def res_def():
            pass

        return check_condition(restart, dt=dt, cond=cond, res_def=res_def)

    return SquadBehaviour(squad_force)


def loop_ex(
    cond: SquadBehaviourCondition, loop_behaviour: SquadBehaviour
) -> SquadBehaviour:
    def squad_force(restart: bool, dt: float) -> CondRes:
        def res_def():
            pass

        res = check_condition(restart, dt=dt, cond=cond, res_def=res_def)
        if res != CondRes(CondRes.not_met):
            return res

        res = loop_behaviour(restart, dt)
        if res == CondRes(CondRes.abort):
            return CondRes(CondRes.abort)
        if res == CondRes(CondRes.met):
            loop_behaviour(True, 0)
        return CondRes(CondRes.not_met)

    return SquadBehaviour(squad_force)


def loop(loop_behaviour: SquadBehaviour) -> SquadBehaviour:
    return loop_ex(infinite_behaviour_condition, loop_behaviour)


def repeat_ex(
    cond: SquadBehaviourCondition, repeat_behaviour: SquadBehaviour, times: int
) -> SquadBehaviour:
    count: int = 0

    def squad_force(restart: bool, dt: float) -> CondRes:
        nonlocal count

        def res_def():
            pass

        res = check_condition(restart, dt=dt, cond=cond, res_def=res_def)
        if res != CondRes(CondRes.not_met):
            return res

        res = repeat_behaviour(restart, dt)
        if res == CondRes(CondRes.abort):
            return CondRes(CondRes.abort)
        if res == CondRes(CondRes.met):
            count += 1
            if count == times:
                return CondRes(CondRes.met)
            repeat_behaviour(True, 0)
        return CondRes(CondRes.not_met)

    return SquadBehaviour(squad_force)


def repeat(repeat_behaviour: SquadBehaviour, times: int) -> SquadBehaviour:
    return repeat_ex(infinite_behaviour_condition, repeat_behaviour, times)


def do_while(
    left: SquadBehaviour, delay: float, right: SquadBehaviour
) -> SquadBehaviour:
    return left or loop(zero_behaviour(time_elapsed(delay)) >> right)


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

        def res_def():
            nonlocal leader
            leader = None

        res = check_condition(restart, dt=dt, cond=cond, res_def=res_def)
        if res != CondRes(CondRes.not_met):
            return res

        (leader, cond_res) = set_leader_steer(
            leader,
            weak_squad,
            steer_path(
                path,
                PathBehaviourWhenDone(PathBehaviourWhenDone.return_to_beginning),
                path_leader_seek_radius,
            ),
            Waypoint.NAWaypoint(),
            follow_front,
        )
        return cond_res

    return SquadBehaviour(squad_force, path)


def patrol(cond: SquadBehaviourCondition, squad: Squad, rect: Rect) -> SquadBehaviour:
    return patrol_ext(cond, squad=squad, num_points=3, swizzle=True, rect=rect)


def patrol_ext(
    cond: SquadBehaviourCondition,
    squad: Squad,
    num_points: int,
    swizzle: bool,
    rect: Rect,
) -> SquadBehaviour:

    h: float = random.uniform(float(rect.height - 50), float(rect.height - 200))
    ppath = shift_path(
        patrol_path(
            num_points=num_points,
            swizzle=swizzle,
            width=float(rect.width - 40),
            height=40,
            close_path=True,
            left_to_right=True,
        ),
        by=Vector(x=rect.x, y=rect.y + h),
    )

    return path(cond, path=ppath, squad=squad, follow_front=False)


def circles(cond: SquadBehaviourCondition, squad: Squad, rect: Rect) -> SquadBehaviour:
    radius: float = random.uniform(85, 120)
    num_of_points: int = 36
    goto_point: Vector = Vector(
        x=random.uniform(2 * radius, float(rect.width) - 2 * radius),
        y=random.uniform(3 * radius, float(rect.height) - 3 * radius),
    )

    ccpath = shift_path(
        path=circle_path(
            radius=radius, starting_angle=0, num_of_points=num_of_points, direction=1
        ),
        by=goto_point,
    )
    ccpath += shift_path(
        path=circle_path(
            radius=radius,
            starting_angle=float(math.pi),
            num_of_points=num_of_points,
            direction=-1,
        ),
        by=(goto_point + Vector(x=0, y=radius * 2)),
    )

    return path(cond, path=ccpath, squad=squad, follow_front=False)


def random_path(
    cond: SquadBehaviourCondition, squad: Squad, rect: Rect
) -> SquadBehaviour:
    rpath: list[Vector] = []
    for i in range(5):
        rpath.append(
            Vector(
                x=random.uniform(float(rect.minX), float(rect.width)),
                y=random.uniform(float(rect.minY), float(rect.height)),
            )
        )
    return path(cond, path=rpath, squad=squad, follow_front=False)


def in_and_out(
    cond: SquadBehaviourCondition, left: bool, squad: Squad, rect: Rect, randomize: bool
) -> SquadBehaviour:
    ppath = in_and_out_path(rect, left_side=left, randomize=randomize)

    return path(cond, path=ppath, squad=squad, follow_front=True)


def flower(
    cond: SquadBehaviourCondition,
    num_leafs_in_quad: int,
    num_of_iterations: int,
    startingAngle: float,
    squad: Squad,
    rect: Rect,
) -> SquadBehaviour:
    ppath = flower_path_area(
        playable_area=rect,
        num_leafs_in_quad=num_leafs_in_quad,
        num_of_iterations=num_of_iterations,
        startingAngle=startingAngle,
    )

    return path(cond, path=ppath, squad=squad, follow_front=True)


def flower_in_out(
    cond: SquadBehaviourCondition,
    num_leafs_in_quad: int,
    num_of_iterations: int,
    startingAngle: float,
    squad: Squad,
    rect: Rect,
) -> SquadBehaviour:
    ppath = patrol_path(
        num_points=2,
        swizzle=False,
        width=float(rect.width) * 1.5,
        height=40,
        close_path=False,
        left_to_right=True,
    )
    ppath = shift_path(
        path=ppath, by=Vector(x=-float(rect.width * 0.25), y=float(rect.height + 300))
    )

    ppath += flower_path_area(
        playable_area=rect,
        num_leafs_in_quad=num_leafs_in_quad,
        num_of_iterations=num_of_iterations,
        starting_angle=startingAngle,
    )

    return path(cond, path=ppath, squad=squad, follow_front=True)


def spiral(
    cond: SquadBehaviourCondition, num_of_spirals: int, squad: Squad, rect: Rect
) -> SquadBehaviour:
    ppath = shift_path(
        path=spiral_path(playable_area=rect, num_of_spirals=num_of_spirals),
        by=Vector(x=0, y=-20),
    )
    return path(cond, path=ppath, squad=squad, follow_front=True)


def spiral_in_out(
    cond: SquadBehaviourCondition, num_of_spirals: int, squad: Squad, rect: Rect
) -> SquadBehaviour:
    ppath = patrol_path(
        num_points=2,
        swizzle=False,
        width=float(rect.width) * 1.5,
        height=40,
        close_path=False,
        left_to_right=True,
    )

    ppath = shift_path(
        path=ppath, by=Vector(x=-float(rect.width * 0.25), y=float(rect.height + 300))
    )

    ppath += shift_path(
        path=spiral_path(playable_area=rect, num_of_spirals=num_of_spirals),
        by=Vector(x=0, y=-20),
    )
    return path(cond, path=ppath, squad=squad, follow_front=True)


def v_shape(
    cond: SquadBehaviourCondition,
    x_mid_point_percentage: float,
    squad: Squad,
    rect: Rect,
) -> SquadBehaviour:
    vpath = v_path(playableArea=rect, x_mid_point_percentage=x_mid_point_percentage)
    return path(cond, path=vpath, squad=squad, follow_front=True)


def dive_to(
    cond: SquadBehaviourCondition, squad: Squad, x: float, y: float
) -> SquadBehaviour:
    leader: MovableEntity | None = None
    weak_squad = squad

    def squad_force(restart: bool, dt: float) -> CondRes:
        nonlocal leader, weak_squad

        def res_def():
            nonlocal leader
            leader = None

        res = check_condition(restart, dt=dt, cond=cond, res_def=res_def)
        if res != CondRes(CondRes.not_met):
            return res

        (leader, cond_res) = set_leader_steer(
            leader, weak_squad, seek(5), Waypoint(Vector(x, y)), True
        )

        if cond_res != CondRes(
            CondRes.not_met
        ):  # if res2 != CondRes(CondRes.not_met) {
            return cond_res

        leader._force_mul = 1.6
        leader._speed_mul = 1.6

        return CondRes(CondRes.not_met)

    return SquadBehaviour(squad_force)
