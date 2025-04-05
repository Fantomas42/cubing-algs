import unittest

from cubing_algs.parsing import clean_moves as original_clean_moves
from cubing_algs.transform import compress_moves
from cubing_algs.transform import optimize_do_undo_moves
from cubing_algs.transform import optimize_double_moves
from cubing_algs.transform import optimize_repeat_three_moves
from cubing_algs.transform import optimize_triple_moves
from cubing_algs.transform import remove_final_rotations


def clean_moves(moves):
    return original_clean_moves(moves, keep_rotations=True)


class Transform(unittest.TestCase):

    def test_optimize_repeat_three_moves(self):
        provide = clean_moves('R R R')
        expect = clean_moves("R'")

        self.assertEqual(
            optimize_repeat_three_moves(provide),
            expect,
        )

        provide = clean_moves("R' R' R'")
        expect = clean_moves('R')

        self.assertEqual(
            optimize_repeat_three_moves(provide),
            expect,
        )

        provide = clean_moves('R R R U')
        expect = clean_moves("R' U")

        self.assertEqual(
            optimize_repeat_three_moves(provide),
            expect,
        )

        provide = clean_moves("R' R' R' U F")
        expect = clean_moves('R U F')

        self.assertEqual(
            optimize_repeat_three_moves(provide),
            expect,
        )

        provide = clean_moves("U F R' R' R' U F")
        expect = clean_moves('U F R U F')

        self.assertEqual(
            optimize_repeat_three_moves(provide),
            expect,
        )

    def test_optimize_do_undo_moves(self):
        provide = clean_moves("R R'")
        expect = []

        self.assertEqual(
            optimize_do_undo_moves(provide),
            expect,
        )

        provide = clean_moves("R' R")
        expect = []

        self.assertEqual(
            optimize_do_undo_moves(provide),
            expect,
        )

        provide = clean_moves("R R' U")
        expect = ['U']

        self.assertEqual(
            optimize_do_undo_moves(provide),
            expect,
        )

        provide = clean_moves("R' R U F")
        expect = ['U', 'F']

        self.assertEqual(
            optimize_do_undo_moves(provide),
            expect,
        )

        provide = clean_moves("U F R' R U F")
        expect = ['U', 'F', 'U', 'F']

        self.assertEqual(
            optimize_do_undo_moves(provide),
            expect,
        )

    def test_optimize_do_undo_double_moves(self):
        provide = clean_moves("R R R' R'")
        expect = []

        self.assertEqual(
            optimize_do_undo_moves(provide),
            expect,
        )

        provide = clean_moves("R' R' R R")
        expect = []

        self.assertEqual(
            optimize_do_undo_moves(provide),
            expect,
        )

        provide = clean_moves("R R R' R' U")
        expect = ['U']

        self.assertEqual(
            optimize_do_undo_moves(provide),
            expect,
        )

        provide = clean_moves("R' R' R R U F")
        expect = ['U', 'F']

        self.assertEqual(
            optimize_do_undo_moves(provide),
            expect,
        )

        provide = clean_moves("U F R' R' R R U F")
        expect = ['U', 'F', 'U', 'F']

        self.assertEqual(
            optimize_do_undo_moves(provide),
            expect,
        )

    def test_optimize_do_undo_double_double_moves(self):
        provide = clean_moves('R2 R2')
        expect = []

        self.assertEqual(
            optimize_do_undo_moves(provide),
            expect,
        )

        provide = clean_moves('R2 R2 U')
        expect = ['U']

        self.assertEqual(
            optimize_do_undo_moves(provide),
            expect,
        )

        provide = clean_moves('R2 R2 U F')
        expect = ['U', 'F']

        self.assertEqual(
            optimize_do_undo_moves(provide),
            expect,
        )

        provide = clean_moves('U F R2 R2 U F')
        expect = ['U', 'F', 'U', 'F']

        self.assertEqual(
            optimize_do_undo_moves(provide),
            expect,
        )

    def test_optimize_double_moves(self):
        provide = clean_moves('R R')
        expect = clean_moves('R2')

        self.assertEqual(
            optimize_double_moves(provide),
            expect,
        )

        provide = clean_moves("R' R'")
        expect = clean_moves('R2')

        self.assertEqual(
            optimize_double_moves(provide),
            expect,
        )

        provide = clean_moves('R R U')
        expect = clean_moves('R2 U')

        self.assertEqual(
            optimize_double_moves(provide),
            expect,
        )

        provide = clean_moves("R' R' U F")
        expect = clean_moves('R2 U F')

        self.assertEqual(
            optimize_double_moves(provide),
            expect,
        )

        provide = clean_moves('U F R R U F')
        expect = clean_moves('U F R2 U F')

        self.assertEqual(
            optimize_double_moves(provide),
            expect,
        )

    def test_optimize_triple_moves(self):
        provide = clean_moves('R R2')
        expect = clean_moves("R'")

        self.assertEqual(
            optimize_triple_moves(provide),
            expect,
        )

        provide = clean_moves("R' R2")
        expect = clean_moves('R')

        self.assertEqual(
            optimize_triple_moves(provide),
            expect,
        )

        provide = clean_moves('R2 R')
        expect = clean_moves("R'")

        self.assertEqual(
            optimize_triple_moves(provide),
            expect,
        )

        provide = clean_moves("R2 R'")
        expect = clean_moves('R')

        self.assertEqual(
            optimize_triple_moves(provide),
            expect,
        )

        provide = clean_moves("R' R2 U")
        expect = clean_moves('R U')

        self.assertEqual(
            optimize_triple_moves(provide),
            expect,
        )

        provide = clean_moves("R2 R' U F")
        expect = clean_moves('R U F')

        self.assertEqual(
            optimize_triple_moves(provide),
            expect,
        )

        provide = clean_moves('U F R2 R U F')
        expect = clean_moves("U F R' U F")

        self.assertEqual(
            optimize_triple_moves(provide),
            expect,
        )

    def test_compress_moves(self):
        provide = clean_moves("U (R U2 R' U' R U' R') (R U2 R' U' R U' R') (R U2 R' U' R U' R')")  # noqa: E501
        expect = clean_moves("U R U2 R' U' R U R' U' R U R' U' R U' R'")

        self.assertEqual(
            compress_moves(provide),
            expect,
        )

    def test_remove_final_rotations(self):
        provide = clean_moves('xRURUx')
        expect = clean_moves('xRURU')

        self.assertEqual(
            remove_final_rotations(provide),
            expect,
        )

        provide = clean_moves("xRURUx'yz")
        expect = clean_moves('xRURU')

        self.assertEqual(
            remove_final_rotations(provide),
            expect,
        )

        provide = clean_moves("xRURUx'Uyz")
        expect = clean_moves("xRURUx'U")

        self.assertEqual(
            remove_final_rotations(provide),
            expect,
        )


if __name__ == '__main__':
    unittest.main()
