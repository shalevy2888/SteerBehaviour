import math
from typing import Callable
from typing import List

from infra.vmath import Vector

Path = List[Vector]

points_in_circle: int = 12


def reverse_path(path: Path) -> Path:
    return path[::-1]


def shift_path(path: Path, by: Vector) -> Path:
    return [point + by for point in path]


def shift_path_with_func(
    path: Path, with_func: Callable[[Vector, int], Vector]
) -> Path:
    return [with_func(point, idx) for idx, point in enumerate(path)]


def rotate_path(path: Path, angle: float) -> Path:
    return [point.rotate(angle) for point in path]


def circle_path(
    radius: float, starting_angle: float, num_of_points: int, direction: float
) -> Path:
    angle_delta: float = math.pi * 2 / num_of_points
    # start and finish on the same point
    return [
        Vector(
            math.sin(starting_angle + (direction * angle_delta * i)) * radius,
            math.cos(starting_angle + (direction * angle_delta * i)) * radius,
        )
        for i in range(num_of_points + 1)
    ]


def patrol_path(
    num_points: int,
    swizzle: bool,
    width: float,
    height: float,
    close_path: bool,
    left_to_right: bool,
) -> Path:
    h: float = 0
    patrol_path: Path = []

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


'''
func inAndOutPath(playableArea:CGRect, leftSide: Bool, randomize: Bool) -> Path {
    let randomWidth = randomize ? RandomFloatRange(0.8, max: 1.2) : 1.5
    let randomHeightAdjust = randomize ? RandomFloatRange(-120, max: 40) : 40
    let randomRadius = randomize ? RandomFloatRange(3.5,max: 5) : 5
    let randomCircleOffset = randomize ? RandomFloatRange(0.15,max: 0.35) : 0.15

    var returnPath = patrolPath(numPoints:2, swizzle:false, width: float(playableArea.width) * randomWidth, height: 40, closePath:false, leftToRight: leftSide)
    returnPath = shiftPath(path: returnPath,
        by: Vector(x: -float(playableArea.width * 0.25), y: float(playableArea.height) + randomHeightAdjust))

    returnPath += (shiftPath(path:
        circlePath(radius: float(playableArea.width)/randomRadius,
            startingAngle:float(M_PI),
            numOfPoints:pointsInCircle,
            direction: leftSide == true ? 1 : -1),
        by: Vector(x: float(playableArea.width)*(leftSide==true ? randomCircleOffset : (1-randomCircleOffset)), y: float(playableArea.height/2) -  RandomFloatRange(90,max: 30) )))

    return returnPath
}

func flowerLeafPath(size size: float) -> Path {
    var returnPath = Path()
    returnPath.append(Vector.Zero()) // starting point
    // 2:
    returnPath.append(Vector(x: -size*0.75, y: -size*0.25))
    // 3:
    returnPath.append(Vector(x: -size, y: 0))
    // 4:
    returnPath.append(Vector(x: -size*0.75, y: size*0.25))

    return returnPath
}

func flowerPath(size size: float, numLeafsInQuad: int, numOfIterations: int, startingAngle: float) -> Path {
    var returnPath = Path()
    let rotateAngle = float(M_PI_2) / float(numLeafsInQuad)

    for i in 0...(numOfIterations) {
        let leaf = rotatePath(path: flowerLeafPath(size: size), byAngle: startingAngle + (float(i) * rotateAngle))
        let leafOpp = rotatePath(path: reversePath(path: leaf), byAngle: float(M_PI))
        returnPath += leaf
        returnPath += leafOpp
    }

    return returnPath
}

func flowerPath(playableArea playableArea:CGRect, numLeafsInQuad: int, numOfIterations: int, startingAngle: float) -> Path {
    var path = flowerPath(size: float(min(playableArea.width, playableArea.height)) * 0.42, numLeafsInQuad:numLeafsInQuad, numOfIterations: numOfIterations,
    startingAngle: startingAngle)

    path = shiftPath(path: path, by: Vector(x: float(playableArea.width)/2, y: float(playableArea.height)/2 + 50))

    return path
}

func spiralPath(playableArea playableArea:CGRect, numOfSpirals: int) -> Path {
    var path = Path()

    let circle = circlePath(radius: float(playableArea.width / 5), startingAngle: float(M_PI_2), numOfPoints: pointsInCircle, direction: 1)

    for i in 1...numOfSpirals {
        let startingHeight = float(playableArea.height - 50)
        let movingDown = float(playableArea.height / 2) / float(numOfSpirals)
        let newCircle = shiftPath(path: circle) { point, index in
            var h = startingHeight - float(i-1)*movingDown
            h -= float(index) * (movingDown / float(pointsInCircle))
            let newPoint = point + Vector(x: float(playableArea.width/2), y: h)
            return newPoint
        }
        path += newCircle
    }

    return path
}

func vPath(playableArea playableArea:CGRect, xMidPointPercentage: float) -> Path {
    var path = Path()

    var startingPointPerc = RandomFloatRange(0.3, max: 0.5)
    if xMidPointPercentage > 0.5 {
        startingPointPerc = xMidPointPercentage - startingPointPerc
    } else {
        startingPointPerc = xMidPointPercentage + startingPointPerc
    }

    let midHeightPointX = float(playableArea.width) * xMidPointPercentage
    let startPointX = float(playableArea.width) * startingPointPerc

    path.append(Vector(x: startPointX, y: float(playableArea.height + 30)))
    path.append(Vector(x: midHeightPointX, y: float(playableArea.height/2)))
    path.append(Vector(x: startPointX, y: -40))

    return path
}

func createPathFromMovement(startingPoint: Vector, startingVelocity: Vector, endPoint:Vector, maxVelocity: float, continuePathAfterPoint: TimeDelta) -> Path {

    let entity = MovableEntityImpl(pos: startingPoint, vel: startingVelocity)
    entity.maxVelocity = maxVelocity
    entity.maxSteeringForce = maxVelocity / 2
    entity.target = Waypoint(pos: endPoint)
    entity.mass = 3

    var path = Path()

    // Calculate max time to reach target so that it is not unlimited:
    let distance = (endPoint - startingPoint).Length()
    let maxTime:TimeDelta = TimeDelta(distance / maxVelocity * 3)

    let timeDelta:TimeDelta = 0.1
    var time:TimeDelta = 0

    let seekForce = seek(0)
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
