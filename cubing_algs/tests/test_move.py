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

    def test_is_rotation_move(self):
        self.assertFalse(Move('U').is_rotation_move)
        self.assertTrue(Move('x').is_rotation_move)

    def test_is_face_move(self):
        self.assertFalse(Move('x').is_face_move)
        self.assertTrue(Move('F').is_face_move)

    def test_is_inner_move(self):
        self.assertFalse(Move('R').is_inner_move)
        self.assertTrue(Move('M').is_inner_move)

    def test_is_outer_move(self):
        self.assertFalse(Move('x').is_outer_move)
        self.assertFalse(Move('M').is_outer_move)
        self.assertTrue(Move('R').is_outer_move)
        self.assertTrue(Move('r2').is_outer_move)

    def test_is_wide_move(self):
        self.assertFalse(Move('x').is_wide_move)
        self.assertFalse(Move('R').is_wide_move)
        self.assertTrue(Move('r2').is_wide_move)
