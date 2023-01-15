import math
import unittest

from infra.vmath import Vector
from steer.path import circle_path
from steer.path import Path
from steer.path import patrol_path
from steer.path import reverse_path
from steer.path import rotate_path
from steer.path import shift_path
from steer.path import shift_path_with_callable


class TestPath(unittest.TestCase):
    def test_reverse(self):
        self.assertEqual(
            reverse_path([Vector(2.0, 1.0), Vector(3.0, 1.0), Vector(5.0, 1.0)]),
            [Vector(5.0, 1.0), Vector(3.0, 1.0), Vector(2.0, 1.0)],
        )
        self.assertEqual(reverse_path([Vector(5.0, 1.0)]), [Vector(5.0, 1.0)])
        self.assertEqual(reverse_path([]), [])

    def test_shift(self):
        path: Path = [Vector(2.0, 1.0), Vector(3.0, 1.0), Vector(5.0, 1.0)]
        self.assertEqual(
            shift_path(path, Vector(1.0, 1.0)),
            [Vector(3.0, 2.0), Vector(4.0, 2.0), Vector(6.0, 2.0)],
        )
        self.assertEqual(
            shift_path([Vector(-2.0, 1.0)], Vector(1.0, 1.0)), [Vector(-1.0, 2.0)]
        )
        self.assertEqual(shift_path([], Vector(1.0, 1.0)), [])

        def shift_func(point: Vector, index: int) -> Vector:
            return Vector(point.x + (index * 2), point.y)

        self.assertEqual(
            shift_path_with_callable(path, shift_func),
            [Vector(2.0, 1.0), Vector(5.0, 1.0), Vector(9.0, 1.0)],
        )

    def test_rotate(self):
        path: Path = [Vector(2.0, 1.0), Vector(3.0, 1.0), Vector(5.0, 1.0)]
        rotated_path = rotate_path(path, math.pi / 2)
        compare_against = [Vector(p.y * -1, p.x) for p in path]
        for idx in range(len(rotated_path)):
            self.assertAlmostEqual(rotated_path[idx], compare_against[idx], places=4)

        rotated_path = rotate_path(path, math.pi)
        compare_against = [Vector(p.x * -1, p.y * -1) for p in path]
        for idx in range(len(rotated_path)):
            self.assertAlmostEqual(rotated_path[idx], compare_against[idx], places=4)

    def test_circle_path(self):
        radius: float = 10
        path: Path = circle_path(radius, 0, 8, 1)
        cos_45: float = math.cos(math.pi / 4) * radius
        compare_path: Path = [
            Vector(0.0, 10.0),
            Vector(cos_45, cos_45),
            Vector(10, 0),
            Vector(cos_45, -cos_45),
            Vector(0, -10.0),
            Vector(-cos_45, -cos_45),
            Vector(-10, 0),
            Vector(-cos_45, cos_45),
            Vector(0.0, 10.0),
        ]
        for idx, point in enumerate(path):
            self.assertAlmostEqual(point, compare_path[idx], places=4)

    def test_patrol_path(self):
        width = 450
        height = 300
        shift_x = 100
        shift_y = 100
        left_to_right = True
        for num_of_points in range(2, 12, 2):
            path = shift_path(
                patrol_path(num_of_points, False, width, height, True, left_to_right),
                Vector(shift_x, shift_y),
            )
            self.assertAlmostEqual(path[0], Vector(shift_x, shift_y), places=4)
            self.assertAlmostEqual(
                path[1],
                Vector(shift_x + width / (num_of_points - 1), shift_y),
                places=4,
            )
            self.assertAlmostEqual(
                path[num_of_points - 1], Vector(shift_x + width, shift_y), places=4
            )
        for num_of_points in range(2, 12, 2):
            path = shift_path(
                patrol_path(num_of_points, False, width, height, True, left_to_right),
                Vector(shift_x, shift_y),
            )
            self.assertAlmostEqual(
                path[num_of_points * 2 - 1], Vector(shift_x, shift_y + height), places=4
            )
            self.assertAlmostEqual(
                path[num_of_points * 2 - 2],
                Vector(shift_x + width / (num_of_points - 1), shift_y + height),
                places=4,
            )
            self.assertAlmostEqual(
                path[num_of_points], Vector(shift_x + width, shift_y + height), places=4
            )
        num_of_points = 8
        for shift_x in range(20, 100, 20):
            path = shift_path(
                patrol_path(num_of_points, False, width, height, True, left_to_right),
                Vector(shift_x, shift_y),
            )
            self.assertAlmostEqual(path[0], Vector(shift_x, shift_y), places=4)
            self.assertAlmostEqual(
                path[1],
                Vector(shift_x + width / (num_of_points - 1), shift_y),
                places=4,
            )
            self.assertAlmostEqual(
                path[num_of_points - 1], Vector(shift_x + width, shift_y), places=4
            )


if __name__ == '__main__':
    unittest.main()
