import unittest

from cubing_algs.parsing import clean_moves


class Clean(unittest.TestCase):

    def test_clean(self):
        provide = clean_moves('R', keep_rotations=True)
        expect = ['R']

        self.assertEqual(
            provide,
            expect,
        )

        provide = clean_moves("R'", keep_rotations=True)
        expect = ["R'"]

        self.assertEqual(
            provide,
            expect,
        )

        provide = clean_moves("R' U", keep_rotations=True)
        expect = ["R'", 'U']

        self.assertEqual(
            provide,
            expect,
        )

        provide = clean_moves('R R R', keep_rotations=True)
        expect = ['R', 'R', 'R']

        self.assertEqual(
            provide,
            expect,
        )

        provide = clean_moves("R' R' U", keep_rotations=True)
        expect = ["R'", "R'", 'U']

        self.assertEqual(
            provide,
            expect,
        )


if __name__ == '__main__':
    unittest.main()
