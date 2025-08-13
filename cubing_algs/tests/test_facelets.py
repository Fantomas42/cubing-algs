import unittest

from cubing_algs.facelets import cubies_to_facelets
from cubing_algs.facelets import facelets_to_cubies


class CubiesToFaceletsTestCase(unittest.TestCase):

    def test_cubies_to_facelets_solved(self):
        cp = [0, 1, 2, 3, 4, 5, 6, 7]
        co = [0, 0, 0, 0, 0, 0, 0, 0]
        ep = [0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11]
        eo = [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0]
        facelets = 'UUUUUUUUURRRRRRRRRFFFFFFFFFDDDDDDDDDLLLLLLLLLBBBBBBBBB'

        self.assertEqual(
            cubies_to_facelets(
                cp, co,
                ep, eo,
            ),
            facelets,
        )

    def test_cubies_to_facelets(self):
        cp = [0, 5, 2, 1, 7, 4, 6, 3]
        co = [1, 2, 0, 2, 1, 1, 0, 2]
        ep = [1, 9, 2, 3, 11, 8, 6, 7, 4, 5, 10, 0]
        eo = [1, 1, 0, 0, 0, 1, 0, 0, 0, 1, 0, 0]
        facelets = 'UUFUUFLLFUUURRRRRRFFRFFDFFDRRBDDBDDBLLDLLDLLDLBBUBBUBB'

        self.assertEqual(
            cubies_to_facelets(
                cp, co,
                ep, eo,
            ),
            facelets,
        )


class FaceletsToCubiesTestCase(unittest.TestCase):

    def test_facelets_to_cubies_solved(self):
        cp = [0, 1, 2, 3, 4, 5, 6, 7]
        co = [0, 0, 0, 0, 0, 0, 0, 0]
        ep = [0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11]
        eo = [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0]
        facelets = 'UUUUUUUUURRRRRRRRRFFFFFFFFFDDDDDDDDDLLLLLLLLLBBBBBBBBB'

        self.assertEqual(
            facelets_to_cubies(facelets),
            (
                cp, co,
                ep, eo,
            ),
        )

    def test_facelets_to_cubies(self):
        cp = [0, 5, 2, 1, 7, 4, 6, 3]
        co = [1, 2, 0, 2, 1, 1, 0, 2]
        ep = [1, 9, 2, 3, 11, 8, 6, 7, 4, 5, 10, 0]
        eo = [1, 1, 0, 0, 0, 1, 0, 0, 0, 1, 0, 0]
        facelets = 'UUFUUFLLFUUURRRRRRFFRFFDFFDRRBDDBDDBLLDLLDLLDLBBUBBUBB'

        self.assertEqual(
            facelets_to_cubies(facelets),
            (
                cp, co,
                ep, eo,
            ),
        )
