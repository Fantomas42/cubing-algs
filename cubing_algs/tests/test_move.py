import unittest

from cubing_algs.move import Move


class MoveTestCase(unittest.TestCase):

    def test_base_move(self):
        self.assertEqual(Move('U').base_move, 'U')
        self.assertEqual(Move('x2').base_move, 'x')
        self.assertEqual(Move('Uw').base_move, 'U')
        self.assertEqual(Move('u').base_move, 'U')
        self.assertEqual(Move('.').base_move, '.')
        self.assertEqual(Move("2-4u'@200").base_move, 'U')
        self.assertEqual(Move("2-4Uw'@200").base_move, 'U')

    def test_raw_base_move(self):
        self.assertEqual(Move('U').raw_base_move, 'U')
        self.assertEqual(Move('x2').raw_base_move, 'x')
        self.assertEqual(Move('Uw').raw_base_move, 'Uw')
        self.assertEqual(Move('u').raw_base_move, 'u')
        self.assertEqual(Move("u'").raw_base_move, 'u')
        self.assertEqual(Move("2-4u'@200").raw_base_move, 'u')
        self.assertEqual(Move("2-4Uw'@200").raw_base_move, 'Uw')
        self.assertEqual(Move('.').raw_base_move, '.')

    def test_modifier(self):
        self.assertEqual(Move('U').modifier, '')
        self.assertEqual(Move('x2').modifier, '2')
        self.assertEqual(Move('Uw').modifier, '')
        self.assertEqual(Move('Uw2').modifier, '2')
        self.assertEqual(Move('.').modifier, '')

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
        self.assertTrue(Move('2Dw2@200').is_valid)
        self.assertTrue(Move('.').is_valid)

    def test_is_valid_move(self):
        self.assertTrue(Move('U').is_valid_move)
        self.assertTrue(Move('u').is_valid_move)
        self.assertTrue(Move('Uw').is_valid_move)
        self.assertFalse(Move('T').is_valid_move)
        self.assertFalse(Move('uw').is_valid_move)
        self.assertTrue(Move('.').is_valid_move)

    def test_is_valid_modifier(self):
        self.assertTrue(Move('U').is_valid_modifier)
        self.assertTrue(Move('U2').is_valid_modifier)
        self.assertTrue(Move("U'").is_valid_modifier)
        self.assertTrue(Move('Uw2').is_valid_modifier)
        self.assertTrue(Move("Uw'").is_valid_modifier)
        self.assertFalse(Move("U2'").is_valid_modifier)
        self.assertFalse(Move("Uw2'").is_valid_modifier)
        self.assertTrue(Move('.').is_valid_modifier)

    def test_is_valid_layer(self):
        self.assertTrue(Move('3Rw').is_valid_layer)
        self.assertTrue(Move('3R').is_valid_layer)
        self.assertTrue(Move('3-4Rw').is_valid_layer)
        self.assertTrue(Move('3-4r').is_valid_layer)
        self.assertFalse(Move('3-4R').is_valid_layer)
        self.assertFalse(Move('2-3-4R').is_valid_layer)
        self.assertTrue(Move('2Dw2').is_valid_layer)
        self.assertTrue(Move('3-4Rw').is_valid_layer)
        self.assertTrue(Move('.').is_valid_layer)

    def test_is_double(self):
        self.assertFalse(Move('U').is_double)
        self.assertFalse(Move("U'").is_double)
        self.assertTrue(Move('U2').is_double)
        self.assertFalse(Move('.').is_double)

    def test_is_clockwise(self):
        self.assertTrue(Move('U').is_clockwise)
        self.assertFalse(Move("U'").is_clockwise)
        self.assertFalse(Move('.').is_clockwise)

    def test_is_counter_clockwise(self):
        self.assertTrue(Move("U'").is_counter_clockwise)
        self.assertFalse(Move('U').is_counter_clockwise)
        self.assertFalse(Move('.').is_counter_clockwise)

    def test_is_pause(self):
        self.assertFalse(Move('U').is_pause)
        self.assertFalse(Move('x').is_pause)
        self.assertTrue(Move('.').is_pause)
        self.assertTrue(Move('.@100').is_pause)

    def test_is_rotation_move(self):
        self.assertFalse(Move('U').is_rotation_move)
        self.assertFalse(Move('.').is_rotation_move)
        self.assertTrue(Move('x').is_rotation_move)

    def test_is_face_move(self):
        self.assertFalse(Move('x').is_face_move)
        self.assertFalse(Move('.').is_face_move)
        self.assertTrue(Move('F').is_face_move)

    def test_is_inner_move(self):
        self.assertFalse(Move('R').is_inner_move)
        self.assertTrue(Move('M').is_inner_move)
        self.assertFalse(Move('.').is_inner_move)

    def test_is_outer_move(self):
        self.assertFalse(Move('x').is_outer_move)
        self.assertFalse(Move('M').is_outer_move)
        self.assertTrue(Move('R').is_outer_move)
        self.assertTrue(Move('r2').is_outer_move)
        self.assertFalse(Move('.').is_outer_move)

    def test_is_wide_move(self):
        self.assertFalse(Move('x').is_wide_move)
        self.assertFalse(Move('R').is_wide_move)
        self.assertTrue(Move('r2').is_wide_move)
        self.assertTrue(Move('rw2').is_wide_move)
        self.assertTrue(Move('Rw2').is_wide_move)
        self.assertFalse(Move('.').is_wide_move)

    def test_is_layered(self):
        self.assertFalse(Move('x').is_layered)
        self.assertFalse(Move('R').is_layered)
        self.assertFalse(Move('.').is_layered)
        self.assertTrue(Move('2R').is_layered)
        self.assertTrue(Move('2Rw').is_layered)
        self.assertTrue(Move('2r').is_layered)
        self.assertTrue(Move('4Rw').is_layered)
        self.assertTrue(Move('3-4Rw').is_layered)
        self.assertTrue(Move('r2').is_layered)

    def test_is_timed(self):
        self.assertFalse(Move('x').is_timed)
        self.assertFalse(Move('R').is_timed)
        self.assertFalse(Move('.').is_timed)
        self.assertTrue(Move('x@500').is_timed)
        self.assertTrue(Move('R@500').is_timed)
        self.assertTrue(Move('2R@500').is_timed)
        self.assertTrue(Move('2Rw@500').is_timed)
        self.assertTrue(Move('2r@500').is_timed)
        self.assertTrue(Move('4Rw@500').is_timed)
        self.assertTrue(Move('3-4Rw@500').is_timed)
        self.assertTrue(Move('r2@500').is_timed)
        self.assertTrue(Move('.@500').is_timed)

    def test_is_standard_move(self):
        self.assertTrue(Move('x').is_standard_move)
        self.assertTrue(Move('R').is_standard_move)
        self.assertTrue(Move('.').is_standard_move)
        self.assertTrue(Move('uw').is_standard_move)
        self.assertTrue(Move('xw').is_standard_move)
        self.assertTrue(Move('xw2').is_standard_move)
        self.assertTrue(Move('Rw').is_standard_move)
        self.assertTrue(Move('Rw2').is_standard_move)
        self.assertFalse(Move('u2').is_standard_move)
        self.assertFalse(Move("u'").is_standard_move)
        self.assertFalse(Move("u'@100").is_standard_move)
        self.assertFalse(Move("2-4u'@100").is_standard_move)

    def test_is_sign_move(self):
        self.assertFalse(Move('x').is_sign_move)
        self.assertFalse(Move('R').is_sign_move)
        self.assertFalse(Move('.').is_sign_move)
        self.assertFalse(Move('uw').is_sign_move)
        self.assertFalse(Move('xw').is_sign_move)
        self.assertFalse(Move('xw2').is_sign_move)
        self.assertFalse(Move('Rw').is_sign_move)
        self.assertFalse(Move('Rw2').is_sign_move)
        self.assertTrue(Move('u2').is_sign_move)
        self.assertTrue(Move("u'").is_sign_move)
        self.assertTrue(Move("u'@100").is_sign_move)
        self.assertTrue(Move("2-4u'@100").is_sign_move)

    def test_inverted(self):
        self.assertEqual(Move('R').inverted, Move("R'"))
        self.assertEqual(Move("R'").inverted, Move('R'))
        self.assertEqual(Move("x'").inverted, Move('x'))
        self.assertEqual(Move('R2').inverted, Move('R2'))
        self.assertEqual(Move('3R2').inverted, Move('3R2'))
        self.assertEqual(Move('3R@200').inverted, Move("3R'@200"))
        self.assertEqual(Move('.').inverted, Move('.'))

    def test_doubled(self):
        self.assertEqual(Move('R').doubled, Move('R2'))
        self.assertEqual(Move("R'").doubled, Move('R2'))
        self.assertEqual(Move("x'").doubled, Move('x2'))
        self.assertEqual(Move('R2').doubled, Move('R'))
        self.assertEqual(Move('3R2').doubled, Move('3R'))
        self.assertEqual(Move('3R2@200').doubled, Move('3R@200'))
        self.assertEqual(Move('.').doubled, Move('.'))

    def test_to_sign(self):
        self.assertEqual(Move('R').to_sign, Move('R'))
        self.assertEqual(Move('x').to_sign, Move('x'))
        self.assertEqual(Move('r').to_sign, Move('r'))
        self.assertEqual(Move('r2').to_sign, Move('r2'))
        self.assertEqual(Move('r@200').to_sign, Move('r@200'))
        self.assertEqual(Move('.').to_sign, Move('.'))

    def test_to_standard(self):
        self.assertEqual(Move('R').to_standard, Move('R'))
        self.assertEqual(Move('x').to_standard, Move('x'))
        self.assertEqual(Move('r').to_standard, Move('Rw'))
        self.assertEqual(Move('r2').to_standard, Move('Rw2'))
        self.assertEqual(Move('r@200').to_standard, Move('Rw@200'))
        self.assertEqual(Move('.').to_standard, Move('.'))

    def test_unlayered(self):
        self.assertEqual(Move('R').unlayered, Move('R'))
        self.assertEqual(Move('2R').unlayered, Move('R'))
        self.assertEqual(Move('2-4Rw').unlayered, Move('Rw'))
        self.assertEqual(Move('2-4r').unlayered, Move('r'))
        self.assertEqual(Move('Rw').unlayered, Move('Rw'))
        self.assertEqual(Move('4Rw').unlayered, Move('Rw'))
        self.assertEqual(Move('u').unlayered, Move('u'))
        self.assertEqual(Move('2u').unlayered, Move('u'))
        self.assertEqual(Move('4u@200').unlayered, Move('u@200'))
        self.assertEqual(Move('.').unlayered, Move('.'))

    def test_untimed(self):
        self.assertEqual(Move('R').untimed, Move('R'))
        self.assertEqual(Move('2R').untimed, Move('2R'))
        self.assertEqual(Move('2-4Rw').untimed, Move('2-4Rw'))
        self.assertEqual(Move('R@100').untimed, Move('R'))
        self.assertEqual(Move('2R@100').untimed, Move('2R'))
        self.assertEqual(Move('2-4Rw@100').untimed, Move('2-4Rw'))
        self.assertEqual(Move('.@100').untimed, Move('.'))

    def test_layer(self):
        self.assertEqual(Move('R').layer, '')
        self.assertEqual(Move('.').layer, '')

        self.assertEqual(Move('2R').layer, '2')

        self.assertEqual(Move('2Rw').layer, '2')
        self.assertEqual(Move('2r').layer, '2')

        self.assertEqual(Move('3Rw').layer, '3')
        self.assertEqual(Move('3r').layer, '3')

        self.assertEqual(Move('3-4Rw').layer, '3-4')
        self.assertEqual(Move('3-4r').layer, '3-4')

        self.assertEqual(Move('1-3-4r').layer, '1-3-4')

        self.assertEqual(Move('2Dw2').layer, '2')

    def test_big_moves_standard(self):
        move = Move('3Rw')

        self.assertEqual(move.layer, '3')
        self.assertEqual(move.to_sign, Move('3r'))
        self.assertEqual(move.to_standard, Move('3Rw'))
        self.assertEqual(move.doubled, Move('3Rw2'))
        self.assertEqual(move.inverted, Move("3Rw'"))
        self.assertEqual(move.unlayered, Move('Rw'))
        self.assertEqual(move.raw_base_move, 'Rw')
        self.assertEqual(move.base_move, 'R')
        self.assertEqual(move.modifier, '')
        self.assertFalse(move.is_sign_move)
        self.assertFalse(move.is_timed)
        self.assertTrue(move.is_layered)
        self.assertTrue(move.is_wide_move)
        self.assertTrue(move.is_outer_move)
        self.assertFalse(move.is_inner_move)
        self.assertTrue(move.is_face_move)
        self.assertFalse(move.is_rotation_move)
        self.assertTrue(move.is_clockwise)
        self.assertFalse(move.is_counter_clockwise)
        self.assertFalse(move.is_double)

    def test_big_moves_sign(self):
        move = Move('3r')

        self.assertEqual(move.layer, '3')
        self.assertEqual(move.to_sign, Move('3r'))
        self.assertEqual(move.to_standard, Move('3Rw'))
        self.assertEqual(move.doubled, Move('3r2'))
        self.assertEqual(move.inverted, Move("3r'"))
        self.assertEqual(move.unlayered, Move('r'))
        self.assertEqual(move.raw_base_move, 'r')
        self.assertEqual(move.base_move, 'R')
        self.assertEqual(move.modifier, '')
        self.assertTrue(move.is_sign_move)
        self.assertFalse(move.is_timed)
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

    def test_timed(self):
        self.assertEqual(Move('R').time, '')
        self.assertEqual(Move('R').timed, None)

        self.assertEqual(Move('.').time, '')
        self.assertEqual(Move('.').timed, None)

        self.assertEqual(Move('R@1500').time, '@1500')
        self.assertEqual(Move('R@1500').timed, 1500)

        self.assertEqual(Move('2-4r@200').time, '@200')
        self.assertEqual(Move('2-4r@200').timed, 200)

        self.assertEqual(Move('.@100').time, '@100')
        self.assertEqual(Move('.@100').timed, 100)
