# ruff: noqa: E241 E501
import unittest

from cubing_algs.constants import INNER_MOVES
from cubing_algs.constants import ROTATIONS
from cubing_algs.move import Move
from cubing_algs.parsing import split_moves
from cubing_algs.transform.degrip import degrip_full_moves
from cubing_algs.transform.degrip import degrip_x_moves
from cubing_algs.transform.degrip import degrip_y_moves
from cubing_algs.transform.degrip import degrip_z_moves
from cubing_algs.transform.rotation import remove_final_rotations
from cubing_algs.transform.size import compress_moves


class TransformDegripTestCase(unittest.TestCase):
    maxDiff = None

    def check_basic_grip_degrip(self, provide, expect, dimension,
                                function, invert):
        if invert:
            provide = split_moves(f"{ dimension }'{ provide }{ dimension }")
        else:
            provide = split_moves(f"{ dimension }{ provide }{ dimension }'")

        expect = [expect]

        with self.subTest(provide=provide, expect=expect):
            degripped = remove_final_rotations(
                function(provide),
            )

            self.assertEqual(
                degripped,
                remove_final_rotations(
                    expect,
                ),
            )

    def check_degrip(self, provide, expect, function, name):
        provide = split_moves(provide)
        expect = split_moves(expect)

        with self.subTest(name=name, provide=provide, expect=expect):

            degripped = compress_moves(
                remove_final_rotations(
                    function(provide),
                ),
            )

            self.assertEqual(
                degripped,
                compress_moves(
                    remove_final_rotations(
                        expect,
                    ),
                ),
            )
            for m in degripped:
                self.assertTrue(isinstance(m, Move))

    def test_basic_x_grip_degrip(self):
        for _move, _expected in zip(
                ('R', 'F', 'U', 'L', 'B', 'D', 'M', 'S', 'E', 'x', 'y', 'z'),
                ('R', 'D', 'F', 'L', 'U', 'B', 'M', 'E', "S'", 'x', 'z', "y'"),
                strict=True,
        ):
            move = Move(_move)
            expected = Move(_expected)

            self.check_basic_grip_degrip(
                move, expected,
                'x', degrip_x_moves,
                invert=False,
            )
            self.check_basic_grip_degrip(
                move.inverted, expected.inverted,
                'x', degrip_x_moves,
                invert=False,
            )

            if move not in ROTATIONS + INNER_MOVES:
                self.check_basic_grip_degrip(
                    move.lower(), expected.lower(),
                    'x', degrip_x_moves,
                    invert=False,
                )

        for _move, _expected in zip(
                ('R', 'F', 'U', 'L', 'B', 'D', 'M', 'S', 'E', 'x', 'y', 'z'),
                ('R', 'U', 'B', 'L', 'D', 'F', 'M', "E'", 'S', 'x', "z'", 'y'),
                strict=True,
        ):
            move = Move(_move)
            expected = Move(_expected)

            self.check_basic_grip_degrip(
                move, expected,
                'x', degrip_x_moves,
                invert=True,
            )
            self.check_basic_grip_degrip(
                move.inverted, expected.inverted,
                'x', degrip_x_moves,
                invert=True,
            )

            if move not in ROTATIONS + INNER_MOVES:
                self.check_basic_grip_degrip(
                    move.lower(), expected.lower(),
                    'x', degrip_x_moves,
                    invert=True,
                )

    def test_basic_y_grip_degrip(self):
        for _move, _expected in zip(
                ('R', 'F', 'U', 'L', 'B', 'D', 'M', 'S', 'E', 'x', 'y', 'z'),
                ('B', 'R', 'U', 'F', 'L', 'D', 'S', "M'", 'E', "z'", 'y', 'x'),
                strict=True,
        ):
            move = Move(_move)
            expected = Move(_expected)

            self.check_basic_grip_degrip(
                move, expected,
                'y', degrip_y_moves,
                invert=False,
            )
            self.check_basic_grip_degrip(
                move.inverted, expected.inverted,
                'y', degrip_y_moves,
                invert=False,
            )
            if move not in ROTATIONS + INNER_MOVES:
                self.check_basic_grip_degrip(
                    move.lower(), expected.lower(),
                    'y', degrip_y_moves,
                    invert=False,
                )

        for _move, _expected in zip(
                ('R', 'F', 'U', 'L', 'B', 'D', 'M', 'S', 'E', 'x', 'y', 'z'),
                ('F', 'L', 'U', 'B', 'R', 'D', "S'", 'M', 'E', 'z', 'y', "x'"),
                strict=True,
        ):
            move = Move(_move)
            expected = Move(_expected)

            self.check_basic_grip_degrip(
                move, expected,
                'y', degrip_y_moves,
                invert=True,
            )
            self.check_basic_grip_degrip(
                move.inverted, expected.inverted,
                'y', degrip_y_moves,
                invert=True,
            )
            if move not in ROTATIONS + INNER_MOVES:
                self.check_basic_grip_degrip(
                    move.lower(), expected.lower(),
                    'y', degrip_y_moves,
                    invert=True,
                )

    def test_basic_z_grip_degrip(self):
        for _move, _expected in zip(
                ('R', 'F', 'U', 'L', 'B', 'D', 'M', 'S', 'E', 'x', 'y', 'z'),
                ('U', 'F', 'L', 'D', 'B', 'R', 'E', 'S', "M'", 'y', "x'", 'z'),
                strict=True,
        ):
            move = Move(_move)
            expected = Move(_expected)

            self.check_basic_grip_degrip(
                move, expected,
                'z', degrip_z_moves,
                invert=False,
            )
            self.check_basic_grip_degrip(
                move.inverted, expected.inverted,
                'z', degrip_z_moves,
                invert=False,
            )
            if move not in ROTATIONS + INNER_MOVES:
                self.check_basic_grip_degrip(
                    move.lower(), expected.lower(),
                    'z', degrip_z_moves,
                    invert=False,
                )

        for _move, _expected in zip(
                ('R', 'F', 'U', 'L', 'B', 'D', 'M', 'S', 'E', 'x', 'y', 'z'),
                ('D', 'F', 'R', 'U', 'B', 'L', "E'", 'S', 'M', "y'", 'x', 'z'),
                strict=True,
        ):
            move = Move(_move)
            expected = Move(_expected)

            self.check_basic_grip_degrip(
                move, expected,
                'z', degrip_z_moves,
                invert=True,
            )
            self.check_basic_grip_degrip(
                move.inverted, expected.inverted,
                'z', degrip_z_moves,
                invert=True,
            )
            if move not in ROTATIONS + INNER_MOVES:
                self.check_basic_grip_degrip(
                    move.lower(), expected.lower(),
                    'z', degrip_z_moves,
                    invert=True,
                )

    def test_start_degrip_x(self):
        basic_moves = 'RF'
        provide = 'x' + basic_moves
        expect = 'RD'

        self.check_degrip(
            provide, expect,
            degrip_x_moves,
            'Start Degrip X',
        )

    def test_end_degrip_x(self):
        basic_moves = 'RF'
        provide = basic_moves + 'x'
        expect = 'RF'

        self.check_degrip(
            provide, expect,
            degrip_x_moves,
            'End Degrip X',
        )

    def test_middle_degrip_x(self):
        provide = 'R' + 'x' + 'F'
        expect = 'RD'

        self.check_degrip(
            provide, expect,
            degrip_x_moves,
            'Middle Degrip X',
        )

    def test_degrip_x(self):
        base_algo = "RUR'U'"

        for prefix, suffix, expect, name in [
                ('', '',               "RUR'U'",             'No Degrip'),
                ('x', '',              "RFR'F'x",            'Start'),
                ('', "x'",             "RUR'U'x'",           'End'),
                ('x', "x'",            "RFR'F'",             'Start/End'),
                ("x'", 'x',            "RBR'B'",             'Start/End/Revert'),
                ('Rx', '',             "R2FR'F'x",           'Prefix'),
                ('RUFLDBx', '',        "RUFLDBRFR'F'x",      'Prefix Bis'),
                ("RUFLDBx'", '',       "RUFLDBRBR'B'x'",     'Prefix Bis Inverted'),
                ('', "x'R",            "RUR'U'Rx'",          'Suffix'),
                ('', "x'RUFLDB",       "RUR'U'RBULFDx'",     'Suffix Bis'),
                ('', 'xRUFLDB',        "RUR'U'RFDLBUx",      'Suffix Bis Inverted'),
                ('Fx', "x'F'",         "FRFR'F2",            'Enclosed'),
                ('FRUx', "x'F'R'U'",   "FRURFR'F2R'U'",      'Enclosed Bis'),
                ("FRUx'", "xF'R'U'",   "FRURBR'B'F'R'U'",    'Enclosed Bis Inverted'),
                ("FRUx'", "x'F'R'U'",  "FRURBR'B2R'D'x2",    'Enclosed Bis Double'),
                ('Rx', "x'FRUxFRU",    'R2FUDRFx',           'Triple'),
                ("Rx'", "x'FRUx'FRU",  'R2BD2RFx',           'Triple Bis'),
        ]: # noqa E241
            algo = f'{ prefix }{ base_algo }{ suffix }'
            self.check_degrip(
                algo,
                expect,
                degrip_x_moves,
                name,
            )

    def test_degrip_y(self):
        base_algo = "RUR'U'"

        for prefix, suffix, expect, name in [
                ('', '',               "RUR'U'",             'No Degrip'),
                ('y', '',              "BUB'U'y",            'Start'),
                ('', "y'",             "RUR'U'y'",           'End'),
                ('y', "y'",            "BUB'U'",             'Start/End'),
                ("y'", 'y',            "FUF'U'",             'Start/End/Revert'),
                ('Ry', '',             "RBUB'U'y",           'Prefix'),
                ('RUFLDBy', '',        "RUFLDB2UB'U'y",      'Prefix Bis'),
                ("RUFLDBy'", '',       "RUFLDBFUF'U'y'",     'Prefix Bis Inverted'),
                ('', "y'R",            "RUR'U'Fy'",          'Suffix'),
                ('', "y'RUFLDB",       "RUR'U'FULBDRy'",     'Suffix Bis'),
                ('', 'yRUFLDB',        "RUR'U'BURFDLy",      'Suffix Bis Inverted'),
                ('Fy', "y'F'",         "FBUB'U'F'",          'Enclosed'),
                ('FRUy', "y'F'R'U'",   "FRUBUB'U'F'R'U'",    'Enclosed Bis'),
                ("FRUy'", "yF'R'U'",   "FRUFUF'U'F'R'U'",    'Enclosed Bis Inverted'),
                ("FRUy'", "y'F'R'U'",  "FRUFUF'U'B'L'U'y2",  'Enclosed Bis Double'),
                ('Ry', "y'FRUyFRU",    "RBUB'U'FRURBUy",     'Triple'),
        ]:
            algo = f'{ prefix }{ base_algo }{ suffix }'
            self.check_degrip(
                algo,
                expect,
                degrip_y_moves,
                name,
            )

    def test_degrip_z(self):
        base_algo = "RUR'U'"

        for prefix, suffix, expect, name in [
                ('', '',               "RUR'U'",             'No Degrip'),
                ('z', '',              "ULU'L'z",            'Start'),
                ('', "z'",             "RUR'U'z'",           'End'),
                ('z', "z'",            "ULU'L'",             'Start/End'),
                ("z'", 'z',            "DRD'R'",             'Start/End/Revert'),
                ('Rz', '',             "RULU'L'z",           'Prefix'),
                ('RUFLDBz', '',        "RUFLDBULU'L'z",      'Prefix Bis'),
                ("RUFLDBz'", '',       "RUFLDBDRD'R'z'",     'Prefix Bis Inverted'),
                ('', "z'R",            "RUR'U'Dz'",          'Suffix'),
                ('', "z'RUFLDB",       "RUR'U'DRFULBz'",     'Suffix Bis'),
                ('', 'zRUFLDB',        "RUR'LFDRBz",         'Suffix Bis Inverted'),
                ('Fz', "z'F'",         "FULU'L'F'",          'Enclosed'),
                ('FRUz', "z'F'R'U'",   "FRU2LU'L'F'R'U'",    'Enclosed Bis'),
                ("FRUz'", "zF'R'U'",   "FRUDRD'R'F'R'U'",    'Enclosed Bis Inverted'),
                ("FRUz'", "z'F'R'U'",  "FRUDRD'R'F'L'D'z2",  'Enclosed Bis Double'),
                ('Rz', "z'FRUzFRU",    "RULU'L'FRUFULz",     'Triple'),
        ]:
            algo = f'{ prefix }{ base_algo }{ suffix }'
            self.check_degrip(
                algo,
                expect,
                degrip_z_moves,
                name,
            )

    def test_multi_degrip_full_moves(self):
        self.check_degrip(
            ''.join(['y2', 'z2', 'M2', "D'", 'M2', 'D2', 'M2', "D'", 'M2', 'z2']),  # noqa: FLY002
            ''.join(['M2', "U'", 'M2', 'U2', 'M2', "U'", 'M2', 'z2', 'y2', 'z2']),  # noqa: FLY002
            degrip_full_moves,
            'Multi move degrip OK',
        )

        self.check_degrip(
            ''.join(['z2', 'y2', 'z2', 'M2', "U'", 'M2', 'U2', 'M2', "U'", 'M2']),  # noqa: FLY002
            ''.join(['M2', "U'", 'M2', 'U2', 'M2', "U'", 'M2', 'z2', 'y2', 'z2']),  # noqa: FLY002
            degrip_full_moves,
            'Multi move degrip KO',
        )

    def test_degrip_full_moves(self):
        for provide, expect, name in [
                ("RUR'U'", "RUR'U'", 'No Degrip'),
                ("R2U'R'URU'x'U'z'U'RU'R'U'rB", "R2U'R'URU'B'R'FR'F'R'fDz'y'", 'Complex 1'),
                ("x'U'R'UL'U'R2U'R'U2r", "B'R'BL'B'R2B'R'B2rx'", 'Complex 2'),
        ]:
            self.check_degrip(
                provide,
                expect,
                degrip_full_moves,
                name,
            )

    def test_degrip_big_moves(self):
        provide = split_moves('z2 3R')
        expect = split_moves('3L')

        self.assertEqual(
            remove_final_rotations(
                degrip_full_moves(provide),
            ),
            expect,
        )

        provide = split_moves("z2 3R'")
        expect = split_moves("3L'")

        self.assertEqual(
            remove_final_rotations(
                degrip_full_moves(provide),
            ),
            expect,
        )

        provide = split_moves('z2 3R2')
        expect = split_moves('3L2')

        self.assertEqual(
            remove_final_rotations(
                degrip_full_moves(provide),
            ),
            expect,
        )

    def test_degrip_big_moves_timed(self):
        provide = split_moves('z2@100 3R@200')
        expect = split_moves('3L@200')

        self.assertEqual(
            remove_final_rotations(
                degrip_full_moves(provide),
            ),
            expect,
        )

        provide = split_moves("z2@100 3R'@200")
        expect = split_moves("3L'@200")

        self.assertEqual(
            remove_final_rotations(
                degrip_full_moves(provide),
            ),
            expect,
        )

        provide = split_moves('z2@100 3R2@200')
        expect = split_moves('3L2@200')

        self.assertEqual(
            remove_final_rotations(
                degrip_full_moves(provide),
            ),
            expect,
        )

    def test_degrip_big_moves_timed_paused(self):
        provide = split_moves('z2@100 .@150 3R@200')
        expect = split_moves('.@150 3L@200')

        self.assertEqual(
            remove_final_rotations(
                degrip_full_moves(provide),
            ),
            expect,
        )
