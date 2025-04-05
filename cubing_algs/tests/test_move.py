import unittest

from cubing_algs.move import Move


class MoveTestCase(unittest.TestCase):

    def test_is_valid(self):
        self.assertTrue(Move('U').is_valid)
        self.assertFalse(Move('T').is_valid)

    def test_is_double(self):
        self.assertFalse(Move('U').is_double)
        self.assertFalse(Move("U'").is_double)
        self.assertTrue(Move('U2').is_double)

    def test_is_clockwise(self):
        self.assertTrue(Move('U').is_clockwise)
        self.assertFalse(Move("U'").is_clockwise)

    def test_is_counter_clockwise(self):
        self.assertTrue(Move("U'").is_counter_clockwise)
        self.assertFalse(Move('U').is_counter_clockwise)
