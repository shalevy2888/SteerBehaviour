from __future__ import annotations

import math
import random
from typing import Callable

from infra.vmath import did_reach_target
from infra.vmath import Vector
from steer.formation import Formation
from steer.globals import ahead_check_radius
from steer.globals import ahead_search_time
from steer.globals import follow_slow_radius
from steer.globals import path_target_radius
from steer.globals import separation_added_force_magnitude
from steer.globals import separation_radius
from steer.globals import wander_divider
from steer.globals import wander_radius
from steer.movable_entity import MovableEntity
from steer.movable_entity import Waypoint
from steer.path import Path
from steer.squad import Squad

SteeringForceFunc = Callable[[MovableEntity, Waypoint], Vector]


class SteeringForce:
    def __init__(self, f: SteeringForceFunc | None = None):
        self.f = f

    def __call__(self, entity: MovableEntity, target: Waypoint) -> Vector:
        if self.f is not None:
            return self.f(entity, target)
        raise ValueError('self.f is None')

    def __add__(self, other: SteeringForce) -> SteeringForce:
        def steering_force(entity: MovableEntity, waypoint: Waypoint) -> Vector:
            return self(entity, waypoint) + other(entity, waypoint)

        return SteeringForce(steering_force)

    def __mul__(self, scalar: float) -> SteeringForce:
        def steering_force(entity: MovableEntity, waypoint: Waypoint) -> Vector:
            return self(entity, waypoint) * scalar

        return SteeringForce(steering_force)

    def __ge__(
        left: SteeringForce, right: SteeringForce  # noqa: N805
    ) -> SteeringForce:
        def steering_force(entity, target) -> Vector:
            right_pos = right(entity, target)
            w = Waypoint()
            w.pos = right_pos
            w.velocity = target.velocity
            return left(entity, w)

        return SteeringForce(steering_force)


def target_in_future(target_position: Vector, velocity: Vector, t: float) -> Vector:
    return target_position + velocity * t


def future_time(length: float, speed: float) -> float:
    return length / speed


def seek(slow_radius: float) -> SteeringForce:
    def steering_force(entity: MovableEntity, waypoint: Waypoint) -> Vector:
        desired_vector = waypoint.pos - entity.pos
        distance = desired_vector.length()
        target_force = entity.max_force
        if distance < slow_radius:
            target_force = target_force * distance / slow_radius
        return desired_vector.normalize() * target_force

    return SteeringForce(steering_force)


def wander() -> SteeringForce:
    wander_angle_change = math.pi / wander_divider
    wander_angle = 0.0

    def steering_force(entity: MovableEntity, waypoint: Waypoint) -> Vector:
        nonlocal wander_angle
        nonlocal wander_angle_change
        circle_center = entity.velocity.normalize() * (wander_radius * 2)
        displacement = Vector(0, -1) * wander_radius
        displacement = displacement.set_angle(wander_angle)
        wander_angle += (
            random.uniform(0, wander_angle_change) - wander_angle_change * 0.5
        )
        return circle_center + displacement

    return SteeringForce(steering_force)


def flee() -> SteeringForce:
    return seek(0) * -1


def pursuit() -> SteeringForce:
    def steering_force(entity: MovableEntity, pursuit_entity: Waypoint) -> Vector:
        return target_in_future(
            pursuit_entity.pos,
            pursuit_entity.velocity,
            future_time((pursuit_entity.pos - entity.pos).length(), entity.max_force),
        )

    return seek(0) >= SteeringForce(steering_force)


def evade() -> SteeringForce:
    def steering_force(entity: MovableEntity, evade_entity: Waypoint):
        return target_in_future(
            evade_entity.pos,
            evade_entity.velocity,
            future_time((evade_entity.pos - entity.pos).length(), entity.max_force),
        )

    return flee() >= SteeringForce(steering_force)


# TODO: Need to write test
def follow(distance) -> SteeringForce:
    def steering_force(entity: MovableEntity, leader: Waypoint):
        ahead = leader.pos + leader.velocity * ahead_search_time
        distance_from_leader = min(
            (entity.pos - ahead).length(), (entity.pos - leader.pos).length()
        )
        if distance_from_leader < ahead_check_radius:
            return evade()(entity, leader)
        elif distance_from_leader < (ahead_check_radius * 1.5):
            entity.speed_mul = 1
        else:
            entity.speed_mul = 1.2
        rot = leader.rotation - math.pi
        shaped_distance = Formation.rotate(distance, rot)
        return seek(follow_slow_radius)(entity, leader.shift(shaped_distance))

    return SteeringForce(steering_force)


def separation(squad: Squad):
    def steering_force(entity, leader):
        added_forces = Vector.zero()
        count_neighbors = 0
        for e1 in (e1 for e1 in squad.active_iter() if e1 != entity):
            delta = (e1.pos - entity.pos).length()
            if delta < separation_radius and delta > 0.01:
                added_forces += e1.pos - entity.pos
                count_neighbors += 1
        if count_neighbors > 0:
            added_forces = added_forces / count_neighbors
            added_forces *= -1
            added_forces = added_forces.normalize() * separation_added_force_magnitude
        return added_forces

    return SteeringForce(steering_force)


class PathBehaviourWhenDone:
    nothing = 'nothing'
    return_to_beginning = 'return to beginning'
    reverse_direction = 'reverse direction'

    def __init__(self, state) -> None:
        self.state = state


def path(path: Path, when_done: PathBehaviourWhenDone, radius: float) -> SteeringForce:
    cur_path_index: int = 0
    path_dir: int = 1

    def steering_force(entity, leader):
        nonlocal cur_path_index, path_dir
        if len(path) != 0 and cur_path_index < len(path):
            target_pos = path[cur_path_index]

            if (
                did_reach_target(
                    entity.pos, entity.prev_pos, target_pos, path_target_radius
                )
                is True
            ):
                cur_path_index += path_dir
                # println("entity.pos = \(entity.pos) entity.prevPost = \(entity.prevPos) targetPost = \(target_pos) cur_path_index = \(cur_path_index)")
                if cur_path_index >= len(path) or cur_path_index < 0:
                    if when_done.state == PathBehaviourWhenDone.nothing:
                        return Vector.zero()
                    elif when_done.state == PathBehaviourWhenDone.return_to_beginning:
                        cur_path_index = 0
                    elif when_done.state == PathBehaviourWhenDone.reverse_direction:
                        path_dir *= -1
                        cur_path_index += 2 * path_dir

                target_pos = path[cur_path_index]

            entity.target = Waypoint(target_pos)
            return seek(radius)(entity, entity.target)
        return Vector.zero()

    return SteeringForce(steering_force)
