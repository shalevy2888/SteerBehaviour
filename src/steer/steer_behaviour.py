from __future__ import annotations
import math
import random
from movable_entity import Waypoint, MovableEntity
from vmath import Vector
from formation import Formation
from squad import Squad
from typing import Callable, Optional

SteeringForceFunc = Callable[[MovableEntity, Waypoint], Vector]

class SteeringForce:
    def __init__(self, f: Optional[SteeringForceFunc] = None):
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
        
    def __ge__(left: SteeringForce, right: SteeringForce) -> SteeringForce:  # noqa: N805
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
        target_speed = entity.max_force
        if (distance < slow_radius):
            target_speed = target_speed * distance / slow_radius
        desired_velocity = desired_vector.normalize() * target_speed
        force = (desired_velocity - entity.velocity)
        return force

    return SteeringForce(steering_force)

wander_radius: float = 20.0
wander_divider: float = 6.0

def wander() -> SteeringForce:
    wander_angle_change = math.pi / wander_divider
    wander_angle = 0.0
    
    def steering_force(entity: MovableEntity, waypoint: Waypoint) -> Vector:
        nonlocal wander_angle
        nonlocal wander_angle_change
        circle_center = entity.velocity.normalize() * (wander_radius * 2)
        displacement = Vector(0, -1) * wander_radius
        displacement = displacement.set_angle(wander_angle)
        wander_angle += random.uniform(0, wander_angle_change) - wander_angle_change * 0.5
        return (circle_center + displacement)
    
    return SteeringForce(steering_force)

def flee() -> SteeringForce:
    return (seek(0) * -1)
    
def pursuit() -> SteeringForce:
    def steering_force(entity: MovableEntity, pursuit_entity: Waypoint) -> Vector:
        return target_in_future(pursuit_entity.pos, pursuit_entity.velocity,
                                future_time((pursuit_entity.pos - entity.pos).length(), entity.max_force))
    return seek(0) >= SteeringForce(steering_force)

def evade() -> SteeringForce:
    def steering_force(entity: MovableEntity, evade_entity: Waypoint):
        return target_in_future(evade_entity.pos, evade_entity.velocity,
                                future_time((evade_entity.pos - entity.pos).length(), entity.max_force))
    return flee() >= SteeringForce(steering_force)


ahead_search_time = 0.5
separation_added_force_magnitude = 80.0
ahead_check_radius = 15.0
follow_slow_radius = 20.0
separation_radius = 15.0

# TODO: Need to write test
def follow(distance) -> SteeringForce:
    def steering_force(entity: MovableEntity, leader: Waypoint):
        ahead = leader.pos + leader.velocity * ahead_search_time
        if (entity.pos - ahead).length() < ahead_check_radius or (entity.pos - leader.pos).length() < ahead_check_radius:
            return evade()(entity, leader)
        else:
            rot = leader.rotation - math.pi
            shaped_distance = Formation.Formation.rotate(distance, rot)
            return seek(follow_slow_radius)(entity, leader.shift(shaped_distance))
    return SteeringForce(steering_force)

def separation(squad: Squad):
    def steering_force(entity, leader):
        added_forces = Vector.zero()
        count_neighbors = 0
        for e1 in (e1 for e1 in squad.active_iter() if e1 != entity):
            delta = (e1.pos - entity.pos).length()
            if (delta < separation_radius and delta>0.01):
                added_forces += e1.pos - entity.pos
                count_neighbors += 1
        if (count_neighbors>0):
            added_forces = added_forces / count_neighbors
            added_forces *= -1
            added_forces = added_forces.normalize() * separation_added_force_magnitude
        return added_forces
    return SteeringForce(steering_force)
