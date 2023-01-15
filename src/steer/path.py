import math
import random
from typing import Callable
from typing import List
from typing import NewType

from infra.vmath import Rect
from infra.vmath import Vector

Path = NewType('Path', List[Vector])

points_in_circle: int = 12


def reverse_path(path: Path) -> Path:
    return Path(path[::-1])


def shift_path(path: Path, by: Vector) -> Path:
    return Path([point + by for point in path])


def shift_path_with_callable(
    path: Path, with_cal: Callable[[Vector, int], Vector]
) -> Path:
    return Path([with_cal(point, idx) for idx, point in enumerate(path)])


def rotate_path(path: Path, angle: float) -> Path:
    return Path([point.rotate(angle) for point in path])


def circle_path(
    radius: float, starting_angle: float, num_of_points: int, direction: float
) -> Path:
    angle_delta: float = math.pi * 2 / num_of_points
    # start and finish on the same point
    return Path(
        [
            Vector(
                math.sin(starting_angle + (direction * angle_delta * i)) * radius,
                math.cos(starting_angle + (direction * angle_delta * i)) * radius,
            )
            for i in range(num_of_points + 1)
        ]
    )


def patrol_path(
    num_points: int,
    swizzle: bool,
    width: float,
    height: float,
    close_path: bool,
    left_to_right: bool,
) -> Path:
    h: float = 0
    patrol_path = Path([])

    points = max(2, num_points)

    x: float = 0.0 if left_to_right else width
    count_points: int = 1
    step: float = (width / float(points - 1)) * (1.0 if left_to_right is True else -1.0)
    hdt: float = 0
    sign: float = 1
    mul: int = 2 if close_path is True else 1

    while True:
        patrol_path.append(Vector(x, h + hdt))
        if count_points == num_points:
            step = -step
        else:
            x += step
        if swizzle is True or count_points == num_points:
            hdt += sign * height
            sign = sign * -1

        count_points += 1
        if count_points >= (mul * num_points + 1):
            break

    return patrol_path


def in_and_out_path(playable_area: Rect, left_side: bool, randomize: bool) -> Path:
    random_width = random.uniform(0.8, 1.2) if randomize else 1
    random_height_adjust = random.uniform(-120.0, 40) if randomize else 40
    random_radius = random.uniform(3.5, 5) if randomize else 5
    random_circle_offset = random.uniform(0.15, 0.35) if randomize else 0.15

    return_path = patrol_path(
        num_points=2,
        swizzle=False,
        width=float(playable_area.width) * random_width,
        height=40,
        close_path=False,
        left_to_right=left_side,
    )
    return_path = shift_path(
        path=return_path,
        by=Vector(
            x=float(playable_area.width * 0.25),
            y=float(playable_area.height) + random_height_adjust,
        ),
    )
    radius = float(playable_area.width) / random_radius
    return_path += shift_path(
        path=circle_path(
            radius=radius,
            starting_angle=float(math.pi),
            num_of_points=points_in_circle,
            direction=1 if left_side else -1,
        ),
        by=Vector(
            radius
            + float(playable_area.width)
            * (random_circle_offset if left_side else (1 - random_circle_offset)),
            float(playable_area.height / 2) - random.uniform(90, 30),
        ),
    )

    return return_path


def flower_leaf_path(size: float) -> Path:
    return_path = Path([])
    return_path.append(Vector.zero())  # starting point
    return_path.append(Vector(x=-size * 0.75, y=-size * 0.25))
    return_path.append(Vector(x=-size, y=0))
    return_path.append(Vector(x=-size * 0.75, y=size * 0.25))

    return return_path


def flower_path_size(
    size: float, num_leafs_in_quad: int, starting_angle: float
) -> Path:
    return_path = Path([])
    rotate_angle = float(math.pi) / float(num_leafs_in_quad)

    for i in range(num_leafs_in_quad):
        leaf = rotate_path(
            path=flower_leaf_path(size=size),
            angle=starting_angle + (float(i) * rotate_angle),
        )
        leaf_opp = rotate_path(path=reverse_path(path=leaf), angle=float(math.pi))
        return_path += leaf
        return_path += leaf_opp

    return return_path


def flower_path_area(
    playable_area: Rect, num_leafs_in_quad: int, starting_angle: float
) -> Path:
    path = flower_path_size(
        size=float(min(playable_area.width, playable_area.height)) * 0.42,
        num_leafs_in_quad=num_leafs_in_quad,
        starting_angle=starting_angle,
    )

    path = shift_path(
        path=path,
        by=Vector(
            x=playable_area.x + float(playable_area.width) / 2,
            y=playable_area.y + float(playable_area.height) / 2,
        ),
    )

    return path


def spiral_path(playable_area: Rect, num_of_spirals: int) -> Path:
    path = Path([])

    circle = circle_path(
        radius=float(playable_area.width / 5),
        starting_angle=float(math.pi / 2),
        num_of_points=points_in_circle,
        direction=1,
    )

    def callable_shift_path(point, index):
        h = starting_height - float(i - 1) * moving_down
        h -= float(index) * (moving_down / float(points_in_circle))
        new_point = point + Vector(x=float(playable_area.width / 2), y=h)
        return new_point

    for i in range(num_of_spirals):
        starting_height = float(playable_area.height - 50)
        moving_down = float(playable_area.height / 2) / float(num_of_spirals)
        new_circle = shift_path_with_callable(path=circle, with_cal=callable_shift_path)
        path += new_circle

    return path


def v_path(playable_area: Rect, x_mid_point_percentage: float) -> Path:
    path = Path([])
    starting_point_percentage = random.uniform(0.3, 0.5)
    if x_mid_point_percentage > 0.5:
        starting_point_percentage = x_mid_point_percentage - starting_point_percentage
    else:
        starting_point_percentage = x_mid_point_percentage + starting_point_percentage

    mid_height_point_x = float(playable_area.width) * x_mid_point_percentage
    start_point_x = float(playable_area.width) * starting_point_percentage

    path.append(Vector(x=start_point_x, y=float(playable_area.height + 30)))
    path.append(Vector(x=mid_height_point_x, y=float(playable_area.height / 2)))
    path.append(Vector(x=start_point_x, y=-40))

    return path


'''
def createPathFromMovement(startingPoint: Vector, startingVelocity: Vector, endPoint:Vector, maxVelocity: float, continuePathAfterPoint: TimeDelta) -> Path {

    entity = MovableEntityImpl(pos: startingPoint, vel: startingVelocity)
    entity.maxVelocity = maxVelocity
    entity.maxSteeringForce = maxVelocity / 2
    entity.target = Waypoint(pos: endPoint)
    entity.mass = 3

    path = Path()

    // Calculate max time to reach target so that it is not unlimited:
    distance = (endPoint - startingPoint).Length()
    maxTime:TimeDelta = TimeDelta(distance / maxVelocity * 3)

    timeDelta:TimeDelta = 0.1
    time:TimeDelta = 0

    seekForce = seek(0)
    entity.steerForce = seekForce

    while time < maxTime {
        path.append(entity.pos)

        entity.updateSteerBehaviour(timeDelta)

        if (entity.pos - endPoint).Length() < (maxVelocity * float(timeDelta) * 1.1) {
            break
        }

        time += timeDelta
    }

    if continuePathAfterPoint >= 0 {
        path.append(entity.pos + entity.velocity*float(continuePathAfterPoint))
    }

    return path
}
'''
