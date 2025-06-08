import unittest

from cubing_algs.move import Move


class MoveTestCase(unittest.TestCase):

    def test_base_move(self):
        self.assertEqual(Move('U').base_move, 'U')
        self.assertEqual(Move('x2').base_move, 'x')
        self.assertEqual(Move('Uw').base_move, 'u')

    def test_raw_base_move(self):
        self.assertEqual(Move('U').raw_base_move, 'U')
        self.assertEqual(Move('x2').raw_base_move, 'x')
        self.assertEqual(Move('Uw').raw_base_move, 'Uw')

    def test_modifier(self):
        self.assertEqual(Move('U').modifier, '')
        self.assertEqual(Move('x2').modifier, '2')
        self.assertEqual(Move('Uw').modifier, '')
        self.assertEqual(Move('Uw2').modifier, '2')

    def test_is_valid(self):
        self.assertTrue(Move('U').is_valid)
        self.assertTrue(Move('u').is_valid)
        self.assertTrue(Move('u2').is_valid)
        self.assertTrue(Move('Uw').is_valid)
        self.assertFalse(Move('T').is_valid)
        self.assertFalse(Move('uw').is_valid)
        self.assertFalse(Move('Ux').is_valid)
        self.assertFalse(Move("U2'").is_valid)
        self.assertFalse(Move('3-4R').is_valid)
        self.assertTrue(Move('3-4Rw').is_valid)
        self.assertTrue(Move('2Dw2').is_valid)

    def test_is_valid_move(self):
        self.assertTrue(Move('U').is_valid_move)
        self.assertTrue(Move('u').is_valid_move)
        self.assertTrue(Move('Uw').is_valid_move)
        self.assertFalse(Move('T').is_valid_move)
        self.assertFalse(Move('uw').is_valid_move)

    def test_is_valid_modifier(self):
        self.assertTrue(Move('U').is_valid_modifier)
        self.assertTrue(Move('U2').is_valid_modifier)
        self.assertTrue(Move("U'").is_valid_modifier)
        self.assertTrue(Move('Uw2').is_valid_modifier)
        self.assertTrue(Move("Uw'").is_valid_modifier)
        self.assertFalse(Move("U2'").is_valid_modifier)
        self.assertFalse(Move("Uw2'").is_valid_modifier)

    def test_is_valid_layer(self):
        self.assertTrue(Move('3Rw').is_valid_layer)
        self.assertTrue(Move('3R').is_valid_layer)
        self.assertTrue(Move('3-4Rw').is_valid_layer)
        self.assertTrue(Move('3-4r').is_valid_layer)
        self.assertFalse(Move('3-4R').is_valid_layer)
        self.assertFalse(Move('2-3-4R').is_valid_layer)
        self.assertTrue(Move('2Dw2').is_valid_layer)
        self.assertTrue(Move('3-4Rw').is_valid_layer)

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

    def test_is_layered(self):
        self.assertFalse(Move('x').is_layered)
        self.assertFalse(Move('R').is_layered)
        self.assertTrue(Move('2R').is_layered)
        self.assertTrue(Move('2Rw').is_layered)
        self.assertTrue(Move('2r').is_layered)
        self.assertTrue(Move('4Rw').is_layered)
        self.assertTrue(Move('3-4Rw').is_layered)
        self.assertTrue(Move('r2').is_layered)

    def test_is_japanese_move(self):
        self.assertFalse(Move('x').is_japanese_move)
        self.assertFalse(Move('R').is_japanese_move)
        self.assertTrue(Move('uw').is_japanese_move)
        self.assertTrue(Move('xw').is_japanese_move)
        self.assertTrue(Move('xw2').is_japanese_move)
        self.assertTrue(Move('Rw').is_japanese_move)
        self.assertTrue(Move('Rw2').is_japanese_move)

    def test_inverted(self):
        self.assertEqual(Move('R').inverted, Move("R'"))
        self.assertEqual(Move("R'").inverted, Move('R'))
        self.assertEqual(Move("x'").inverted, Move('x'))
        self.assertEqual(Move('R2').inverted, Move('R2'))

    def test_doubled(self):
        self.assertEqual(Move('R').doubled, Move('R2'))
        self.assertEqual(Move("R'").doubled, Move('R2'))
        self.assertEqual(Move("x'").doubled, Move('x2'))
        self.assertEqual(Move('R2').doubled, Move('R'))

    def test_japanesed(self):
        self.assertEqual(Move('R').japanesed, Move('R'))
        self.assertEqual(Move('x').japanesed, Move('x'))
        self.assertEqual(Move('r').japanesed, Move('Rw'))
        self.assertEqual(Move('r2').japanesed, Move('Rw2'))

    def test_unlayered(self):
        self.assertEqual(Move('R').unlayered, Move('R'))
        self.assertEqual(Move('2R').unlayered, Move('R'))
        self.assertEqual(Move('2-4Rw').unlayered, Move('r'))
        self.assertEqual(Move('Rw').unlayered, Move('r'))
        self.assertEqual(Move('4Rw').unlayered, Move('r'))
        self.assertEqual(Move('u').unlayered, Move('u'))
        self.assertEqual(Move('2u').unlayered, Move('u'))

    def test_layer(self):
        self.assertEqual(Move('R').layer, '')

        self.assertEqual(Move('2R').layer, '2')

        self.assertEqual(Move('2Rw').layer, '2')
        self.assertEqual(Move('2r').layer, '2')

        self.assertEqual(Move('3Rw').layer, '3')
        self.assertEqual(Move('3r').layer, '3')

        self.assertEqual(Move('3-4Rw').layer, '3-4')
        self.assertEqual(Move('3-4r').layer, '3-4')

        self.assertEqual(Move('1-3-4r').layer, '1-3-4')

        self.assertEqual(Move('2Dw2').layer, '2')

    def test_big_moves_japanese(self):
        move = Move('3Rw')

        self.assertEqual(move.layer, '3')
        self.assertEqual(move.japanesed, Move('3Rw'))
        self.assertEqual(move.unjapanesed, Move('3r'))
        self.assertEqual(move.doubled, Move('3r2'))
        self.assertEqual(move.inverted, Move("3r'"))
        self.assertEqual(move.unlayered, Move('r'))
        self.assertEqual(move.raw_base_move, 'Rw')
        self.assertEqual(move.base_move, 'r')
        self.assertEqual(move.modifier, '')
        self.assertTrue(move.is_japanese_move)
        self.assertTrue(move.is_layered)
        self.assertTrue(move.is_wide_move)
        self.assertTrue(move.is_outer_move)
        self.assertFalse(move.is_inner_move)
        self.assertTrue(move.is_face_move)
        self.assertFalse(move.is_rotation_move)
        self.assertTrue(move.is_clockwise)
        self.assertFalse(move.is_counter_clockwise)
        self.assertFalse(move.is_double)

    def test_big_moves_non_japanese(self):
        move = Move('3r')

        self.assertEqual(move.layer, '3')
        self.assertEqual(move.japanesed, Move('3Rw'))
        self.assertEqual(move.unjapanesed, Move('3r'))
        self.assertEqual(move.doubled, Move('3r2'))
        self.assertEqual(move.inverted, Move("3r'"))
        self.assertEqual(move.unlayered, Move('r'))
        self.assertEqual(move.raw_base_move, 'r')
        self.assertEqual(move.base_move, 'r')
        self.assertEqual(move.modifier, '')
        self.assertFalse(move.is_japanese_move)
        self.assertTrue(move.is_layered)
        self.assertTrue(move.is_wide_move)
        self.assertTrue(move.is_outer_move)
        self.assertFalse(move.is_inner_move)
        self.assertTrue(move.is_face_move)
        self.assertFalse(move.is_rotation_move)
        self.assertTrue(move.is_clockwise)
        self.assertFalse(move.is_counter_clockwise)
        self.assertFalse(move.is_double)

    def test_layers(self):
        self.assertEqual(Move('R').layers, [0])
        self.assertEqual(Move('2R').layers, [1])

        self.assertEqual(Move('Rw').layers, [0, 1])
        self.assertEqual(Move('r').layers, [0, 1])

        self.assertEqual(Move('2Rw').layers, [0, 1])
        self.assertEqual(Move('2r').layers, [0, 1])

        self.assertEqual(Move('3Rw').layers, [0, 1, 2])
        self.assertEqual(Move('3r').layers, [0, 1, 2])

        self.assertEqual(Move('3-4Rw').layers, [2, 3])
        self.assertEqual(Move('3-4r').layers, [2, 3])

        self.assertEqual(Move('2-4r').layers, [1, 2, 3])

        self.assertEqual(Move('2Dw2').layers, [0, 1])
