import unittest

from cubing_algs.exceptions import InvalidBracketError
from cubing_algs.exceptions import InvalidMoveError
from cubing_algs.exceptions import InvalidOperatorError
from cubing_algs.move import Move
from cubing_algs.parsing import check_moves
from cubing_algs.parsing import clean_moves
from cubing_algs.parsing import parse_moves
from cubing_algs.parsing import parse_moves_cfop
from cubing_algs.parsing import split_moves


class CleanMovesTestCase(unittest.TestCase):

    def test_clean_moves(self):
        moves = "R2 L2  (y):F B2' e U R` U’  "  # noqa RUF001
        expect = "R2 L2 y F B2 E U R' U'"
        self.assertEqual(clean_moves(moves), expect)


class SplitMovesTestCase(unittest.TestCase):

    def test_split_moves(self):
        moves = "R2L2yFB2EU'R'U'"
        expect = ['R2', 'L2', 'y', 'F', 'B2', 'E', "U'", "R'", "U'"]
        self.assertEqual(split_moves(moves), expect)

    def test_split_big_moves(self):
        moves = "3R 3Uw' 3b 2-3Dw 3-4d"
        expect = ['3R', "3Uw'", '3b', '2-3Dw', '3-4d']
        self.assertEqual(split_moves(moves), expect)

        moves = "3R3Uw'3b2-3Dw3-4d"
        expect = ['3R', "3Uw'", '3b', '2-3Dw', '3-4d']
        self.assertEqual(split_moves(moves), expect)

    def test_split_timed_moves(self):
        moves = "3R 3Uw'@1500 3b 2-3Dw 3-4d"
        expect = ['3R', "3Uw'@1500", '3b', '2-3Dw', '3-4d']
        self.assertEqual(split_moves(moves), expect)

    def test_split_timed_pauses(self):
        moves = "3R 3Uw'@1500 .@2000 3b 2-3Dw 3-4d"
        expect = ['3R', "3Uw'@1500", '.@2000', '3b', '2-3Dw', '3-4d']
        self.assertEqual(split_moves(moves), expect)

    def test_split_timed_moves_with_pauses(self):
        moves = "3R 3Uw'@1500 . 3b 2-3Dw 3-4d"
        expect = ['3R', "3Uw'@1500", '.', '3b', '2-3Dw', '3-4d']
        self.assertEqual(split_moves(moves), expect)


class CheckMovesTestCase(unittest.TestCase):

    def test_check_moves(self):
        moves = split_moves('R2 L2')
        self.assertTrue(check_moves(moves))

    def test_check_moves_invalid_move(self):
        moves = [Move('T2'), Move('R')]
        self.assertFalse(check_moves(moves))

    def test_check_moves_invalid_wide_standard_move(self):
        moves = [Move('Rw')]
        self.assertTrue(check_moves(moves))
        moves = [Move('Rw3')]
        self.assertFalse(check_moves(moves))
        moves = [Move("Rw2'")]
        self.assertFalse(check_moves(moves))

    def test_check_moves_invalid_wide_sign_move(self):
        moves = [Move('r')]
        self.assertTrue(check_moves(moves))
        moves = [Move('r3')]
        self.assertFalse(check_moves(moves))
        moves = [Move("r2'")]
        self.assertFalse(check_moves(moves))

    def test_check_moves_invalid_modifier(self):
        moves = [Move('R5')]
        self.assertFalse(check_moves(moves))

    def test_check_moves_invalid_too_long(self):
        moves = [Move("R2'")]
        self.assertFalse(check_moves(moves))

    def test_check_moves_invalid_layer(self):
        moves = [Move('2-4R')]
        self.assertFalse(check_moves(moves))


class ParseMovesTestCase(unittest.TestCase):

    def test_parse_moves(self):
        moves = 'R2 L2'
        expect = ['R2', 'L2']
        self.assertEqual(
            parse_moves(moves),
            expect,
        )

    def test_parse_moves_with_pauses(self):
        moves = 'R2 . L2 .'
        expect = ['R2', '.', 'L2', '.']
        self.assertEqual(
            parse_moves(moves),
            expect,
        )

        moves = 'R2 ... L2 .'
        expect = ['R2', '.', '.', '.', 'L2', '.']
        self.assertEqual(
            parse_moves(moves),
            expect,
        )

    def test_parse_list(self):
        moves = ['R2 L2']
        expect = ['R2', 'L2']
        self.assertEqual(
            parse_moves(moves),
            expect,
        )

        moves = ['R2', 'L2']
        expect = ['R2', 'L2']
        self.assertEqual(
            parse_moves(moves),
            expect,
        )

    def test_parse_moves_invalid(self):
        moves = 'R2 T2'
        self.assertRaises(
            InvalidMoveError,
            parse_moves, moves,
            secure=False,
        )

    def test_parse_moves_list_moves(self):
        moves = 'R2 L2'
        expect = ['R2', 'L2']
        self.assertEqual(
            parse_moves(parse_moves(moves)),
            expect,
        )

    def test_parse_moves_algorithm(self):
        moves = 'R2 L2'
        expect = ['R2', 'L2']
        self.assertEqual(
            parse_moves(parse_moves(moves)),
            expect,
        )

    def test_parse_moves_conjugate(self):
        moves = 'F [R, U] F'
        expect = ['F', 'R', 'U', "R'", "U'", 'F']
        self.assertEqual(
            parse_moves(parse_moves(moves)),
            expect,
        )

        moves = 'F[R,U]F'
        self.assertEqual(
            parse_moves(parse_moves(moves)),
            expect,
        )

    def test_parse_moves_conjugate_malformed(self):
        moves = 'F [R, U F'

        self.assertRaises(
            InvalidBracketError,
            parse_moves, moves,
            secure=False,
        )

    def test_parse_moves_conjugate_invalid_moves(self):
        moves = 'F [T, U] F'

        self.assertRaises(
            InvalidMoveError,
            parse_moves, moves,
            secure=False,
        )

        self.assertRaises(
            InvalidMoveError,
            parse_moves, moves,
            secure=True,
        )

    def test_parse_moves_conjugate_nested(self):
        moves = 'F [[R, U], B] F'
        expect = [
            'F',
            'R', 'U', "R'", "U'",
            'B',
            'U', 'R', "U'", "R'",
            "B'",
            'F',
        ]
        self.assertEqual(
            parse_moves(parse_moves(moves)),
            expect,
        )

    def test_parse_moves_commutator(self):
        moves = 'F [R: U] F'
        expect = ['F', 'R', 'U', "R'", 'F']
        self.assertEqual(
            parse_moves(parse_moves(moves)),
            expect,
        )

        moves = 'F[R:U]F'
        self.assertEqual(
            parse_moves(parse_moves(moves)),
            expect,
        )

    def test_parse_moves_commutator_malformed(self):
        moves = 'F [R: U F'

        self.assertRaises(
            InvalidBracketError,
            parse_moves, moves,
            secure=False,
        )

    def test_parse_moves_commutator_invalid_moves(self):
        moves = 'F [T: U] F'

        self.assertRaises(
            InvalidMoveError,
            parse_moves, moves,
            secure=False,
        )

        self.assertRaises(
            InvalidMoveError,
            parse_moves, moves,
            secure=True,
        )

    def test_parse_moves_commutator_nested(self):
        moves = 'F [[R: U]: B] F'
        expect = [
            'F',
            'R', 'U', "R'",
            'B',
            'R', "U'", "R'",
            'F',
        ]
        self.assertEqual(
            parse_moves(parse_moves(moves)),
            expect,
        )

    def test_parse_moves_invalid_operator(self):
        moves = 'F [R; U] F'

        self.assertRaises(
            InvalidOperatorError,
            parse_moves, moves,
            secure=False,
        )

    def test_parse_moves_complex_1(self):
        moves = '[[R: U], D] B [F: [U, R]]'
        expect = [
            'R', 'U', "R'", 'D',
            'R', "U'", "R'", "D'",
            'B',
            'F', 'U', 'R', "U'", "R'", "F'",
        ]
        self.assertEqual(
            parse_moves(parse_moves(moves)),
            expect,
        )

    def test_parse_moves_complex_2(self):
        moves = '[[R F: U L], D] B'
        expect = [
            'R', 'F', 'U', 'L', "F'", "R'",
            'D',
            'R', 'F', "L'", "U'", "F'", "R'",
            "D'",
            'B',
        ]
        self.assertEqual(
            parse_moves(parse_moves(moves)),
            expect,
        )


class ParseMovesCFOPTestCase(unittest.TestCase):

    def test_parse_moves_cfop(self):
        moves = 'R2 L2'
        expect = ['R2', 'L2']
        self.assertEqual(
            parse_moves_cfop(moves),
            expect,
        )

    def test_parse_moves_cfop_cleaned(self):
        moves = 'U R2 L2 y'
        expect = ['R2', 'L2']
        self.assertEqual(
            parse_moves_cfop(moves),
            expect,
        )
