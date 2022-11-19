import unittest
# import sys

# sys.path.append('.')

from infra.vmath import Vector

class TestVmath(unittest.TestCase):
    def test_length(self):
        self.assertEqual(Vector(3, 4).length(), 5)
    
    def test_normalized(self):
        self.assertAlmostEqual(1, Vector(3, 4).normalize().length())
    
if __name__ == '__main__':
    unittest.main()
