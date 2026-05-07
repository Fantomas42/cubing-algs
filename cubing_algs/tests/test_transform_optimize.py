"""Tests for move optimization transformation functions."""
import unittest

from cubing_algs.algorithm import Algorithm
from cubing_algs.parsing import parse_moves
from cubing_algs.transform.optimize import optimize_do_undo_moves
from cubing_algs.transform.optimize import optimize_double_moves
from cubing_algs.transform.optimize import optimize_repeat_three_moves
from cubing_algs.transform.optimize import optimize_triple_moves


class TransformOptimizeTestCase(unittest.TestCase):
    """Tests for move optimization transformations."""

    def test_optimize_repeat_three_moves(self) -> None:
        """Test optimize repeat three moves."""
        provide = parse_moves('R R R')
        expect = parse_moves("R'")

        self.assertEqual(
            optimize_repeat_three_moves(provide),
            expect,
        )

        provide = parse_moves("R' R' R'")
        expect = parse_moves('R')

        self.assertEqual(
            optimize_repeat_three_moves(provide),
            expect,
        )

        provide = parse_moves('R R R U')
        expect = parse_moves("R' U")

        self.assertEqual(
            optimize_repeat_three_moves(provide),
            expect,
        )

        provide = parse_moves("R' R' R' U F")
        expect = parse_moves('R U F')

        self.assertEqual(
            optimize_repeat_three_moves(provide),
            expect,
        )

        provide = parse_moves("2R' 2R' 2R' U F")
        expect = parse_moves('2R U F')

        self.assertEqual(
            optimize_repeat_three_moves(provide),
            expect,
        )

        provide = parse_moves("2R'@100 2R'@200 2R'@300 U@400 F@500")
        expect = parse_moves('2R@300 U@400 F@500')

        self.assertEqual(
            optimize_repeat_three_moves(provide),
            expect,
        )

        provide = parse_moves("2R'@100 .@150 2R'@200 2R'@300 U@400 F@500")
        expect = parse_moves("2R'@100 .@150 2R'@200 2R'@300 U@400 F@500")

        self.assertEqual(
            optimize_repeat_three_moves(provide),
            expect,
        )

        provide = parse_moves("U F R' R' R' U F")
        expect = parse_moves('U F R U F')

        self.assertEqual(
            optimize_repeat_three_moves(provide),
            expect,
        )

        self.assertEqual(
            optimize_repeat_three_moves(provide, 0),
            provide,
        )

        provide = parse_moves('U . . . U')
        expect = parse_moves('U . . . U')

        self.assertEqual(
            optimize_repeat_three_moves(provide),
            expect,
        )

    def test_optimize_do_undo_moves(self) -> None:
        """Test optimize do undo moves."""
        provide = parse_moves("R R'")
        expect = Algorithm()

        self.assertEqual(
            optimize_do_undo_moves(provide),
            expect,
        )

        provide = parse_moves("R' R")

        self.assertEqual(
            optimize_do_undo_moves(provide),
            expect,
        )

        provide = parse_moves("R R' U")
        expect = parse_moves('U')

        self.assertEqual(
            optimize_do_undo_moves(provide),
            expect,
        )

        provide = parse_moves("R' R U F")
        expect = parse_moves('U F')

        self.assertEqual(
            optimize_do_undo_moves(provide),
            expect,
        )

        provide = parse_moves("2R' 2R U F")
        expect = parse_moves('U F')

        self.assertEqual(
            optimize_do_undo_moves(provide),
            expect,
        )

        provide = parse_moves("2R'@100 2R@200 U@300 F@400")
        expect = parse_moves('U@300 F@400')

        self.assertEqual(
            optimize_do_undo_moves(provide),
            expect,
        )

        provide = parse_moves("2R'@100 .@150 2R@200 U@300 F@400")
        expect = parse_moves("2R'@100 .@150 2R@200 U@300 F@400")

        self.assertEqual(
            optimize_do_undo_moves(provide),
            expect,
        )

        provide = parse_moves("U F R' R U F")
        expect = parse_moves('U F U F')

        self.assertEqual(
            optimize_do_undo_moves(provide),
            expect,
        )

        self.assertEqual(
            optimize_do_undo_moves(provide, 0),
            provide,
        )

        provide = parse_moves('U . . . U')
        expect = parse_moves('U . . . U')

        self.assertEqual(
            optimize_do_undo_moves(provide),
            expect,
        )

    def test_optimize_do_undo_double_moves(self) -> None:
        """Test optimize do undo double moves."""
        provide = parse_moves("R R R' R'")
        expect = Algorithm()

        self.assertEqual(
            optimize_do_undo_moves(provide),
            expect,
        )

        provide = parse_moves("R' R' R R")

        self.assertEqual(
            optimize_do_undo_moves(provide),
            expect,
        )

        provide = parse_moves("R R R' R' U")
        expect = parse_moves('U')

        self.assertEqual(
            optimize_do_undo_moves(provide),
            expect,
        )

        provide = parse_moves("R' R' R R U F")
        expect = parse_moves('U F')

        self.assertEqual(
            optimize_do_undo_moves(provide),
            expect,
        )

        provide = parse_moves("2R' 2R' 2R 2R U F")
        expect = parse_moves('U F')

        self.assertEqual(
            optimize_do_undo_moves(provide),
            expect,
        )

        provide = parse_moves("2R'@100 2R'@200 2R@300 2R@400 U@500 F@600")
        expect = parse_moves('U@500 F@600')

        self.assertEqual(
            optimize_do_undo_moves(provide),
            expect,
        )

        provide = parse_moves("2R'@100 2R'@200 .@250 2R@300 2R@400 U@500 F@600")
        expect = parse_moves("2R'@100 2R'@200 .@250 2R@300 2R@400 U@500 F@600")

        self.assertEqual(
            optimize_do_undo_moves(provide),
            expect,
        )

        provide = parse_moves("U F R' R' R R U F")
        expect = parse_moves('U F U F')

        self.assertEqual(
            optimize_do_undo_moves(provide),
            expect,
        )

    def test_optimize_do_undo_double_double_moves(self) -> None:
        """Test optimize do undo double double moves."""
        provide = parse_moves('R2 R2')
        expect = Algorithm()

        self.assertEqual(
            optimize_do_undo_moves(provide),
            expect,
        )

        provide = parse_moves('R2 R2 U')
        expect = parse_moves('U')

        self.assertEqual(
            optimize_do_undo_moves(provide),
            expect,
        )

        provide = parse_moves('R2 R2 U F')
        expect = parse_moves('U F')

        self.assertEqual(
            optimize_do_undo_moves(provide),
            expect,
        )

        provide = parse_moves('2R2 2R2 U F')
        expect = parse_moves('U F')

        self.assertEqual(
            optimize_do_undo_moves(provide),
            expect,
        )

        provide = parse_moves('2R2@100 2R2@200 U@300 F@400')
        expect = parse_moves('U@300 F@400')

        self.assertEqual(
            optimize_do_undo_moves(provide),
            expect,
        )

        provide = parse_moves('2R2@100 .@150 2R2@200 U@300 F@400')
        expect = parse_moves('2R2@100 .@150 2R2@200 U@300 F@400')

        self.assertEqual(
            optimize_do_undo_moves(provide),
            expect,
        )

        provide = parse_moves('U F R2 R2 U F')
        expect = parse_moves('U F U F')

        self.assertEqual(
            optimize_do_undo_moves(provide),
            expect,
        )

    def test_optimize_double_moves(self) -> None:
        """Test optimize double moves."""
        provide = parse_moves('R R')
        expect = parse_moves('R2')

        self.assertEqual(
            optimize_double_moves(provide),
            expect,
        )

        provide = parse_moves("R' R'")
        expect = parse_moves('R2')

        self.assertEqual(
            optimize_double_moves(provide),
            expect,
        )

        provide = parse_moves('R R U')
        expect = parse_moves('R2 U')

        self.assertEqual(
            optimize_double_moves(provide),
            expect,
        )

        provide = parse_moves("R' R' U F")
        expect = parse_moves('R2 U F')

        self.assertEqual(
            optimize_double_moves(provide),
            expect,
        )

        provide = parse_moves("2R' 2R' U F")
        expect = parse_moves('2R2 U F')

        self.assertEqual(
            optimize_double_moves(provide),
            expect,
        )

        provide = parse_moves("2R'@100 2R'@200 U@300 F@400")
        expect = parse_moves('2R2@200 U@300 F@400')

        self.assertEqual(
            optimize_double_moves(provide),
            expect,
        )

        provide = parse_moves("2R'@100 .@150 2R'@200 U@300 F@400")
        expect = parse_moves("2R'@100 .@150 2R'@200 U@300 F@400")

        self.assertEqual(
            optimize_double_moves(provide),
            expect,
        )

        provide = parse_moves("2R'@100 .@150 .@175 2R'@200 U@300 F@400")
        expect = parse_moves("2R'@100 .@150 .@175 2R'@200 U@300 F@400")

        self.assertEqual(
            optimize_double_moves(provide),
            expect,
        )

        provide = parse_moves('U . . U')
        expect = parse_moves('U . . U')

        self.assertEqual(
            optimize_double_moves(provide),
            expect,
        )

        provide = parse_moves('U F R R U F')
        expect = parse_moves('U F R2 U F')

        self.assertEqual(
            optimize_double_moves(provide),
            expect,
        )

        self.assertEqual(
            optimize_double_moves(provide, 0),
            provide,
        )

    def test_optimize_double_moves_issue_1(self) -> None:
        """Test optimize double moves issue 1."""
        provide = parse_moves('R R R2 F')
        expect = parse_moves('R2 R2 F')

        self.assertEqual(
            optimize_double_moves(provide),
            expect,
        )

    def test_optimize_triple_moves(self) -> None:
        """Test optimize triple moves."""
        provide = parse_moves('R R2')
        expect = parse_moves("R'")

        self.assertEqual(
            optimize_triple_moves(provide),
            expect,
        )

        provide = parse_moves("R' R2")
        expect = parse_moves('R')

        self.assertEqual(
            optimize_triple_moves(provide),
            expect,
        )

        provide = parse_moves('R2 R')
        expect = parse_moves("R'")

        self.assertEqual(
            optimize_triple_moves(provide),
            expect,
        )

        provide = parse_moves("R2 R'")
        expect = parse_moves('R')

        self.assertEqual(
            optimize_triple_moves(provide),
            expect,
        )

        provide = parse_moves("R' R2 U")
        expect = parse_moves('R U')

        self.assertEqual(
            optimize_triple_moves(provide),
            expect,
        )

        provide = parse_moves("R2 R' U F")
        expect = parse_moves('R U F')

        self.assertEqual(
            optimize_triple_moves(provide),
            expect,
        )

        provide = parse_moves("R2 R' U F F")
        expect = parse_moves('R U F F')

        self.assertEqual(
            optimize_triple_moves(provide),
            expect,
        )

        provide = parse_moves("2R2 2R' U F F")
        expect = parse_moves('2R U F F')

        self.assertEqual(
            optimize_triple_moves(provide),
            expect,
        )

        provide = parse_moves("2R2@100 2R'@200 U@300 F@400 F@500")
        expect = parse_moves('2R@200 U@300 F@400 F@500')

        self.assertEqual(
            optimize_triple_moves(provide),
            expect,
        )

        provide = parse_moves("2R'@100 2R2@200 U@300 F@400 F@500")
        expect = parse_moves('2R@100 U@300 F@400 F@500')

        self.assertEqual(
            optimize_triple_moves(provide),
            expect,
        )

        provide = parse_moves("2R'@100 .@150 2R2@200 U@300 F@400 F@500")
        expect = parse_moves("2R'@100 .@150 2R2@200 U@300 F@400 F@500")

        self.assertEqual(
            optimize_triple_moves(provide),
            expect,
        )

        provide = parse_moves('U F R2 R U F')
        expect = parse_moves("U F R' U F")

        self.assertEqual(
            optimize_triple_moves(provide),
            expect,
        )

        # Moves on different layers must not be combined
        provide = parse_moves('R2 3R')
        expect = parse_moves('R2 3R')

        self.assertEqual(
            optimize_triple_moves(provide),
            expect,
        )

        provide = parse_moves('2R 3R2')
        expect = parse_moves('2R 3R2')

        self.assertEqual(
            optimize_triple_moves(provide),
            expect,
        )

        provide = parse_moves('2R 2R2')
        expect = parse_moves("2R'")

        self.assertEqual(
            optimize_triple_moves(provide),
            expect,
        )

        self.assertEqual(
            optimize_triple_moves(provide, 0),
            provide,
        )

        provide = parse_moves('U . . . U')
        expect = parse_moves('U . . . U')

        self.assertEqual(
            optimize_triple_moves(provide),
            expect,
        )

    def test_optimize_triple_moves_consecutive_pauses(self) -> None:
        """Consecutive pauses must not be combined by optimize_triple_moves."""
        provide = parse_moves('. . R')
        expect = parse_moves('. . R')

        self.assertEqual(
            optimize_triple_moves(provide),
            expect,
        )

        provide = parse_moves('R . . R2')
        expect = parse_moves('R . . R2')

        self.assertEqual(
            optimize_triple_moves(provide),
            expect,
        )

        provide = parse_moves('. .')
        expect = parse_moves('. .')

        self.assertEqual(
            optimize_triple_moves(provide),
            expect,
        )

    def test_optimize_wide_vs_normal_moves_not_combined(self) -> None:
        """Wide and normal moves on the same face must never be combined."""
        # optimize_triple_moves: r' R2 and r R2 must not simplify
        for alg in ("r' R2", 'r R2', 'R2 r', "R2 r'"):
            provide = parse_moves(alg)
            self.assertEqual(
                optimize_triple_moves(provide),
                provide,
                msg=f'optimize_triple_moves incorrectly simplified {alg!r}',
            )

        # optimize_repeat_three_moves: mixed wide/normal triplets must not simplify
        for alg in ('r r R', 'r R R', "r' r' R'", "r' R' R'"):
            provide = parse_moves(alg)
            self.assertEqual(
                optimize_repeat_three_moves(provide),
                provide,
                msg=f'optimize_repeat_three_moves incorrectly simplified {alg!r}',
            )

        # optimize_do_undo_moves: r R' and R r' are not inverse pairs
        for alg in ("r R'", "R r'", 'r R', 'R r'):
            provide = parse_moves(alg)
            self.assertEqual(
                optimize_do_undo_moves(provide),
                provide,
                msg=f'optimize_do_undo_moves incorrectly simplified {alg!r}',
            )

        # optimize_double_moves: r R and R r are not the same move
        for alg in ('r R', 'R r', "r' R'", "R' r'"):
            provide = parse_moves(alg)
            self.assertEqual(
                optimize_double_moves(provide),
                provide,
                msg=f'optimize_double_moves incorrectly simplified {alg!r}',
            )
