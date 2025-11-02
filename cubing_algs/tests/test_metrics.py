"""Tests for algorithm metrics computation."""

import unittest

from cubing_algs.metrics import MetricsData
from cubing_algs.parsing import parse_moves
from cubing_algs.transform.optimize import optimize_double_moves


class MetricsTestCase(unittest.TestCase):
    """Tests for algorithm metrics computation."""

    maxDiff = None

    def test_metrics(self) -> None:
        """Test metrics."""
        algo = parse_moves("yM2UMU2M'UM2")
        self.assertEqual(
            algo.metrics,
            MetricsData(
                generators=['M', 'U'],
                inner_moves=4,
                outer_moves=3,
                pauses=0,
                rotations=1,
                htm=11,
                qtm=16,
                stm=7,
                etm=8,
                rtm=1,
                qstm=10,
            ),
        )

    def test_htm(self) -> None:
        """Test htm."""
        moves = [
            'R', 'R2', 'M', 'M2', 'x2', "f'", 'Fw',
            '2R', '2-3Rw', '2-3Rw2',
        ]
        scores = [1, 1, 2, 2, 0, 1, 1, 2, 2, 2]

        for move, score in zip(moves, scores, strict=True):
            with self.subTest(move=move, score=score):
                self.assertEqual(parse_moves(move).metrics.htm, score)

    def test_qtm(self) -> None:
        """Test qtm."""
        moves = [
            'R', 'R2', 'M', 'M2', 'x2', "f'", 'Fw',
            '2R', '2-3Rw', '2-3Rw2',
        ]
        scores = [1, 2, 2, 4, 0, 1, 1, 2, 2, 4]

        for move, score in zip(moves, scores, strict=True):
            with self.subTest(move=move, score=score):
                self.assertEqual(parse_moves(move).metrics.qtm, score)

    def test_stm(self) -> None:
        """Test stm."""
        moves = [
            'R', 'R2', 'M', 'M2', 'x2', "f'", 'Fw',
            '2R', '2-3Rw', '2-3Rw2',
        ]
        scores = [1, 1, 1, 1, 0, 1, 1, 1, 1, 1]

        for move, score in zip(moves, scores, strict=True):
            with self.subTest(move=move, score=score):
                self.assertEqual(parse_moves(move).metrics.stm, score)

    def test_etm(self) -> None:
        """Test etm."""
        moves = [
            'R', 'R2', 'M', 'M2', 'x2', "f'", 'Fw',
            '2R', '2-3Rw', '2-3Rw2',
        ]
        scores = [1, 1, 1, 1, 1, 1, 1, 1, 1, 1]

        for move, score in zip(moves, scores, strict=True):
            with self.subTest(move=move, score=score):
                self.assertEqual(parse_moves(move).metrics.etm, score)

    def test_qstm(self) -> None:
        """Test qstm."""
        moves = [
            'R', 'R2', 'M', 'M2', 'x2', "f'", 'Fw',
            '2R', '2-3Rw', '2-3Rw2',
        ]
        scores = [1, 2, 1, 2, 0, 1, 1, 1, 1, 2]

        for move, score in zip(moves, scores, strict=True):
            with self.subTest(move=move, score=score):
                self.assertEqual(parse_moves(move).metrics.qstm, score)

    def test_rtm(self) -> None:
        """Test rtm."""
        moves = [
            'R', 'R2', 'M', 'M2', 'x2', "f'", 'Fw',
            '2R', '2-3Rw', '2-3Rw2', 'x y2',
        ]
        scores = [0, 0, 0, 0, 2, 0, 0, 0, 0, 0, 3]

        for move, score in zip(moves, scores, strict=True):
            with self.subTest(move=move, score=score):
                self.assertEqual(parse_moves(move).metrics.rtm, score)

    def test_obtm(self) -> None:
        """Test obtm."""
        moves = [
            'R', 'R2', 'M', 'M2', "f'", 'Fw',
            '2R', '2-3Rw', '2-3Rw2', 'x y z',
        ]
        scores = [1, 1, 2, 2, 1, 1, 2, 2, 2, 0]

        for move, score in zip(moves, scores, strict=True):
            with self.subTest(move=move, score=score):
                self.assertEqual(parse_moves(move).metrics.obtm, score)

    def test_btm(self) -> None:
        """Test btm."""
        moves = [
            'R', 'R2', 'M', 'M2', 'x2', "f'", 'Fw',
            '2R', '2-3Rw', '2-3Rw2',
        ]
        scores = [1, 1, 1, 1, 0, 1, 1, 1, 1, 1]

        for move, score in zip(moves, scores, strict=True):
            with self.subTest(move=move, score=score):
                self.assertEqual(parse_moves(move).metrics.btm, score)

    def test_bqtm(self) -> None:
        """Test bqtm."""
        moves = [
            'R', 'R2', 'M', 'M2', 'x2', "f'", 'Fw',
            '2R', '2-3Rw', '2-3Rw2',
        ]
        scores = [1, 2, 1, 2, 0, 1, 1, 1, 1, 2]

        for move, score in zip(moves, scores, strict=True):
            with self.subTest(move=move, score=score):
                self.assertEqual(parse_moves(move).metrics.bqtm, score)

    def test_issue_11(self) -> None:
        """Test issue 11."""
        moves = "R U F' B R' U F' U' F D F' D' F' D' F D' L D L' R D' R' D' B D' B' D' D' R D' D' R' D B' D' B D' D' F D' F' D F D F' D' D D' D' L D B D' B' L' D R F D F' D' R' R F D' F' D' F D F' R' F D F' D' F' R F R' D"  # noqa: E501

        algo = parse_moves(moves)
        self.assertEqual(
            algo.metrics,
            MetricsData(
                generators=['D', 'F', 'R', 'B', 'L', 'U'],
                inner_moves=0,
                outer_moves=80,
                pauses=0,
                rotations=0,
                htm=80,
                qtm=80,
                stm=80,
                etm=80,
                rtm=0,
                qstm=80,
            ),
        )

        compress = algo.transform(optimize_double_moves)

        self.assertEqual(
            compress.metrics,
            MetricsData(
                generators=['D', 'F', 'R', 'B', 'L', 'U'],
                inner_moves=0,
                outer_moves=76,
                pauses=0,
                rotations=0,
                htm=76,
                qtm=80,
                stm=76,
                etm=76,
                rtm=0,
                qstm=80,
            ),
        )

    def test_metrics_wide_sign(self) -> None:
        """Test metrics wide sign."""
        algo = parse_moves('RFu')
        self.assertEqual(
            algo.metrics,
            MetricsData(
                generators=['R', 'F', 'u'],
                inner_moves=0,
                outer_moves=3,
                pauses=0,
                rotations=0,
                htm=3,
                qtm=3,
                stm=3,
                etm=3,
                rtm=0,
                qstm=3,
            ),
        )

    def test_metrics_wide_standard(self) -> None:
        """Test metrics wide standard."""
        algo = parse_moves('RFUw')
        self.assertEqual(
            algo.metrics,
            MetricsData(
                generators=['R', 'F', 'Uw'],
                inner_moves=0,
                outer_moves=3,
                pauses=0,
                rotations=0,
                htm=3,
                qtm=3,
                stm=3,
                etm=3,
                rtm=0,
                qstm=3,
            ),
        )

    def test_metrics_pauses(self) -> None:
        """Test metrics pauses."""
        algo = parse_moves('R..Fu.')
        self.assertEqual(
            algo.metrics,
            MetricsData(
                generators=['R', 'F', 'u'],
                inner_moves=0,
                outer_moves=3,
                pauses=3,
                rotations=0,
                htm=3,
                qtm=3,
                stm=3,
                etm=3,
                rtm=0,
                qstm=3,
            ),
        )

    def test_obtm_alias(self) -> None:
        """Test OBTM alias for HTM."""
        # OBTM should always equal HTM
        test_cases = [
            "R U R' U'",       # Simple algorithm
            'M2 U M2 U2',      # With slice moves
            "R U2 F' D2",      # With double moves
            "Rw U Rw' U'",     # With wide moves
            "x R U R' U' x'",  # With rotations
        ]

        for moves_str in test_cases:
            algo = parse_moves(moves_str)
            self.assertEqual(
                algo.metrics.obtm,
                algo.metrics.htm,
                f'OBTM should equal HTM for { moves_str }',
            )

    def test_btm_equals_stm(self) -> None:
        """Test BTM equals STM for 3x3x3."""
        # BTM should equal STM for 3x3x3 cubes
        test_cases = [
            "R U R' U'",       # Simple algorithm
            'M2 U M2 U2',      # With slice moves
            "R U2 F' D2",      # With double moves
            "Rw U Rw' U'",     # With wide moves
            "x R U R' U' x'",  # With rotations
            '2R 2-3Rw U',      # Big cube moves
        ]

        for moves_str in test_cases:
            algo = parse_moves(moves_str)
            self.assertEqual(
                algo.metrics.btm,
                algo.metrics.stm,
                f'BTM should equal STM for { moves_str }',
            )

    def test_bqtm_equals_qstm(self) -> None:
        """Test BQTM equals QSTM for 3x3x3."""
        # BQTM should equal QSTM for 3x3x3 cubes
        test_cases = [
            "R U R' U'",       # Simple algorithm
            'M2 U M2 U2',      # With slice moves
            "R U2 F' D2",      # With double moves
            "Rw U Rw' U'",     # With wide moves
            "x R U R' U' x'",  # With rotations
            '2R 2-3Rw U',      # Big cube moves
        ]

        for moves_str in test_cases:
            algo = parse_moves(moves_str)
            self.assertEqual(
                algo.metrics.bqtm,
                algo.metrics.qstm,
                f'BQTM should equal QSTM for { moves_str }',
            )
