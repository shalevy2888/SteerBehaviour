from __future__ import annotations

from typing import Callable

from infra.vmath import did_reach_target
from infra.vmath import Vector
from steer.globals import path_target_radius

# from steer.squad import Squad


class CondRes:
    not_met = 'Not Met'
    met = 'Met'
    abort = 'Abort'

    def __init__(self, state: str) -> None:
        self.state = state

    def __or__(self, r: CondRes) -> CondRes:
        if self.state == CondRes.not_met or r.state == CondRes.not_met:
            return CondRes(CondRes.not_met)
        if self.state == CondRes.met or r.state == CondRes.met:
            return CondRes(CondRes.met)
        return CondRes(CondRes.abort)

    def __and__(self, r: CondRes) -> CondRes:
        if self.state == CondRes.not_met or r.state == CondRes.not_met:
            return CondRes(CondRes.not_met)
        if self.state == CondRes.met and r.state == CondRes.met:
            return CondRes(CondRes.met)
        return CondRes(CondRes.abort)

    def __eq__(self, other: object) -> bool:
        if isinstance(other, CondRes):
            return self.state == other.state
        return False


check_func = Callable[[bool, float], CondRes]


class SquadBehaviourCondition:
    def __init__(self, check: check_func) -> None:
        self.check: check_func = check

    # @classmethod
    # def zero() -> SquadBehaviourCondition:
    #     return zeroBehaviourCondition()
    @staticmethod
    def zero_func() -> SquadBehaviourCondition:
        return SquadBehaviourCondition(check=lambda _, __: CondRes(CondRes.met))

    def __add__(self, r: SquadBehaviourCondition) -> SquadBehaviourCondition:
        return SquadBehaviourCondition.zero_func()

    def __or__(self, r: SquadBehaviourCondition) -> SquadBehaviourCondition:
        def squad_cond(restart: bool, dt: float):
            if restart is True:
                self.check(True, 0)
                r.check(True, 0)
                return CondRes(CondRes.abort)
            return self.check(restart, dt) or r.check(restart, dt)

        return SquadBehaviourCondition(check=squad_cond)

    def __and__(self, r: SquadBehaviourCondition) -> SquadBehaviourCondition:
        left_res: CondRes = CondRes(CondRes.abort)
        right_res: CondRes = CondRes(CondRes.abort)

        def squad_cond(restart: bool, dt: float):
            nonlocal left_res, right_res
            if restart is True:
                self.check(True, 0)
                r.check(True, 0)
                return CondRes(CondRes.abort)
            if left_res == CondRes(CondRes.abort):
                left_res = self.check(restart, dt)
            if right_res == CondRes(CondRes.abort):
                right_res = r.check(restart, dt)

            return left_res and right_res

        return SquadBehaviourCondition(check=squad_cond)


def time_elapsed(time: float) -> SquadBehaviourCondition:
    elapsed: float = 0.0

    def squad_cond(restart: bool, dt: float) -> CondRes:
        nonlocal elapsed
        if restart is True:
            elapsed = 0
            return CondRes(CondRes.not_met)
        elapsed += dt
        if elapsed >= time:
            return CondRes(CondRes.met)
        return CondRes(CondRes.not_met)

    return SquadBehaviourCondition(check=squad_cond)


def infinite_behaviour_condition() -> SquadBehaviourCondition:
    def squad_cond(_: bool, __: float) -> CondRes:
        return CondRes(CondRes.not_met)

    return SquadBehaviourCondition(check=squad_cond)


def zero_behaviour_condition() -> SquadBehaviourCondition:
    return SquadBehaviourCondition.zero_func()


def reached_waypoint(squad, waypoint: Vector) -> SquadBehaviourCondition:
    weak_ptr_squad = squad

    def squad_cond(restart: bool, dt: float) -> CondRes:
        if restart is True:
            return CondRes(CondRes.not_met)
        leader = weak_ptr_squad.getLeader()
        if leader is not None:
            if (
                did_reach_target(
                    leader.pos,
                    prev_pos=leader.prevPos,
                    target=waypoint,
                    radius=path_target_radius,
                )
                is True
            ):
                return CondRes(CondRes.met)
        else:
            return CondRes(CondRes.met)  # no leader, stop behaviour
        return CondRes(CondRes.not_met)

    return SquadBehaviourCondition(check=squad_cond)


'''
func reachedBelowYCoordinate(squad: Squad, rect: CGRect, yPerc: Float) -> SquadBehaviourCondition {
    weak var weakSquad = squad
    return SquadBehaviourCondition { restart, _ in
        if restart == true {
            return CondRes(CondRes.abort)
        }
        var passed = true
        let y: Float = Float(rect.height) * yPerc
        for entity in weakSquad! {
            if entity.isActive == true {
                if (entity.pos.y) > y  {
                    passed = false
                    break
                }
            }
        }

        if passed == true {
            return CondRes(CondRes.met)
        }
        return CondRes(CondRes.abort)
    }
}

func reachedAboveYCoordinate(squad: Squad, rect: CGRect, yPerc: Float) -> SquadBehaviourCondition {
    weak var weakSquad = squad
    return SquadBehaviourCondition { restart, _ in
        if restart == true {
            return CondRes(CondRes.abort)
        }
        var passed = true
        let y: Float = Float(rect.height) * yPerc
        for entity in weakSquad! {
            if entity.isActive == true {
                if (entity.pos.y) < y  {
                    passed = false
                    break
                }
            }
        }

        if passed == true {
            return CondRes(CondRes.met)
        }
        return CondRes(CondRes.abort)
    }
}


func velocityBelowThreshold(squad: Squad, percenteVelocity: Float) -> SquadBehaviourCondition {
    weak var weakSquad = squad
    return SquadBehaviourCondition { restart, _ in
        if restart == true {
            return CondRes(CondRes.abort)
        }
        for entity in weakSquad! {
            if entity.isActive == true {
                if (entity.minVelocity / entity.maxVelocity) > percenteVelocity {
                    if (entity.velocity.Length() - entity.minVelocity) > 0.1 {
                        return CondRes(CondRes.abort)
                    }
                }

                if entity.velocity.Length() / entity.maxVelocity > percenteVelocity {
                    return CondRes(CondRes.abort)
                }
            }
        }

        return CondRes(CondRes.met)
    }
}

func squadCountBelowThreshold(squad: Squad, belowCount: Int) -> SquadBehaviourCondition {
    weak var weakSquad = squad
    return SquadBehaviourCondition { restart, _ in
        if restart == true {
            return CondRes(CondRes.abort)
        }

        let count = weakSquad!.getSquadCount()
        if count < belowCount {
            return CondRes(CondRes.met)
        }
        return CondRes(CondRes.abort)
    }
}
'''
