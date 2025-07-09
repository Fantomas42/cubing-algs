import unittest

from cubing_algs.move import Move
from cubing_algs.parsing import parse_moves
from cubing_algs.transform.pause import pause_moves
from cubing_algs.transform.pause import unpause_moves


class TransformUnpauseTestCase(unittest.TestCase):

    def test_unpause_moves(self):
        provide = parse_moves(
            "F@1 R@2 .@3 U2@4 F'@5",
        )
        expect = parse_moves("F@1 R@2 U2@4 F'@5")

        result = unpause_moves(provide)

        self.assertEqual(
            result,
            expect,
        )

        for m in result:
            self.assertTrue(isinstance(m, Move))

    def test_unpause_moves_untimed(self):
        provide = parse_moves(
            "F@1 R . U2 F'@4",
        )
        expect = parse_moves("F@1 R U2 F'@4")

        result = unpause_moves(provide)

        self.assertEqual(
            result,
            expect,
        )

        for m in result:
            self.assertTrue(isinstance(m, Move))


class TransformPauseTestCase(unittest.TestCase):

    def test_pause_moves(self):
        provide = parse_moves(
            "F@0 R@300 U2@1300 F'@1450",
        )
        expect = parse_moves(
            "F@0 R@300 .@800 U2@1300 F'@1450",
        )

        result = pause_moves()(provide)

        self.assertEqual(
            result,
            expect,
        )

        for m in result:
            self.assertTrue(isinstance(m, Move))

    def test_pause_moves_empty(self):
        provide = parse_moves('')

        result = pause_moves()(provide)

        self.assertEqual(
            result,
            provide,
        )

        for m in result:
            self.assertTrue(isinstance(m, Move))

    def test_pause_moves_untimed(self):
        provide = parse_moves(
            "F R U2 F'",
        )
        expect = parse_moves(
            "F R U2 F'",
        )

        result = pause_moves()(provide)

        self.assertEqual(
            result,
            expect,
        )

        for m in result:
            self.assertTrue(isinstance(m, Move))

    def test_pause_moves_untimed_partial(self):
        provide = parse_moves(
            "F@0 R@300 U2@1300 F'",
        )
        expect = parse_moves(
            "F@0 R@300 U2@1300 F'",
        )

        result = pause_moves()(provide)

        self.assertEqual(
            result,
            expect,
        )

        for m in result:
            self.assertTrue(isinstance(m, Move))


class TransformPauseConfigTestCase(unittest.TestCase):

    def test_pause_moves(self):
        provide = parse_moves(
            "F@0 R@300 U2@1300 F'@1450",
        )
        expect = parse_moves(
            "F@0 R@300 .@800 U2@1300 F'@1450",
        )

        result = provide.transform(pause_moves())

        self.assertEqual(
            result,
            expect,
        )

        for m in result:
            self.assertTrue(isinstance(m, Move))

    def test_pause_moves_configured(self):
        provide = parse_moves(
            "F@0 R@300 U2@1300 F'@1450",
        )
        expect = parse_moves(
            "F@0 R@300 .@800 U2@1300 F'@1450",
        )

        result = provide.transform(pause_moves(300, 2))

        self.assertEqual(
            result,
            expect,
        )

        for m in result:
            self.assertTrue(isinstance(m, Move))

    def test_pause_moves_configured_multiple(self):
        provide = parse_moves(
            "F@0 R@300 U2@1300 F'@1450",
        )
        expect = parse_moves(
            "F@0 R@300 .@800 .@1200 U2@1300 F'@1450",
        )

        result = provide.transform(pause_moves(200, 2, multiple=True))

        self.assertEqual(
            result,
            expect,
        )

        for m in result:
            self.assertTrue(isinstance(m, Move))
