import unittest

from cubing_algs.parsing import parse_moves
from cubing_algs.transform.optimize import optimize_double_moves


class MetricsTestCase(unittest.TestCase):
    maxDiff = None

    def test_metrics(self):
        algo = parse_moves("yM2UMU2M'UM2")
        self.assertEqual(
            algo.metrics,
            {
                'generators': ['M', 'U'],
                'inner_moves': 4,
                'outer_moves': 3,
                'pauses': 0,
                'rotations': 1,
                'htm': 11,
                'qtm': 16,
                'stm': 7,
                'etm': 8,
                'rtm': 1,
                'qstm': 10,
            },
        )

    def test_htm(self):
        moves = ['R', 'R2', 'M', 'M2', 'x2', "f'"]
        scores = [1, 1, 2, 2, 0, 1]

        for move, score in zip(moves, scores, strict=True):
            self.assertEqual(parse_moves(move).metrics['htm'], score)

    def test_qtm(self):
        moves = ['R', 'R2', 'M', 'M2', 'x2', "f'"]
        scores = [1, 2, 2, 4, 0, 1]

        for move, score in zip(moves, scores, strict=True):
            self.assertEqual(parse_moves(move).metrics['qtm'], score)

    def test_stm(self):
        moves = ['R', 'R2', 'M', 'M2', 'x2', "f'"]
        scores = [1, 1, 1, 1, 0, 1]

        for move, score in zip(moves, scores, strict=True):
            self.assertEqual(parse_moves(move).metrics['stm'], score)

    def test_etm(self):
        moves = ['R', 'R2', 'M', 'M2', 'x2', "f'"]
        scores = [1, 1, 1, 1, 1, 1]

        for move, score in zip(moves, scores, strict=True):
            self.assertEqual(parse_moves(move).metrics['etm'], score)

    def test_qstm(self):
        moves = ['R', 'R2', 'M', 'M2', 'x2', "f'"]
        scores = [1, 2, 1, 2, 0, 1]

        for move, score in zip(moves, scores, strict=True):
            self.assertEqual(parse_moves(move).metrics['qstm'], score)

    def test_rtm(self):
        moves = ['R', 'R2', 'M', 'M2', 'x2', "f'", 'x y2']
        scores = [0, 0, 0, 0, 2, 0, 3]

        for move, score in zip(moves, scores, strict=True):
            self.assertEqual(parse_moves(move).metrics['rtm'], score)

    def test_issue_11(self):
        moves = "R U F' B R' U F' U' F D F' D' F' D' F D' L D L' R D' R' D' B D' B' D' D' R D' D' R' D B' D' B D' D' F D' F' D F D F' D' D D' D' L D B D' B' L' D R F D F' D' R' R F D' F' D' F D F' R' F D F' D' F' R F R' D"  # noqa: E501

        algo = parse_moves(moves)
        self.assertEqual(
            algo.metrics,
            {
                'generators': ['D', 'F', 'R', 'B', 'L', 'U'],
                'inner_moves': 0,
                'outer_moves': 80,
                'pauses': 0,
                'rotations': 0,
                'htm': 80,
                'qtm': 80,
                'stm': 80,
                'etm': 80,
                'rtm': 0,
                'qstm': 80,
            },
        )

        compress = algo.transform(optimize_double_moves)

        self.assertEqual(
            compress.metrics,
            {
                'generators': ['D', 'F', 'R', 'B', 'L', 'U'],
                'inner_moves': 0,
                'outer_moves': 76,
                'pauses': 0,
                'rotations': 0,
                'htm': 76,
                'qtm': 80,
                'stm': 76,
                'etm': 76,
                'rtm': 0,
                'qstm': 80,
            },
        )

    def test_metrics_wide_sign(self):
        algo = parse_moves('RFu')
        self.assertEqual(
            algo.metrics,
            {
                'generators': ['R', 'F', 'u'],
                'inner_moves': 0,
                'outer_moves': 3,
                'pauses': 0,
                'rotations': 0,
                'htm': 3,
                'qtm': 3,
                'stm': 3,
                'etm': 3,
                'rtm': 0,
                'qstm': 3,
            },
        )

    def test_metrics_wide_standard(self):
        algo = parse_moves('RFUw')
        self.assertEqual(
            algo.metrics,
            {
                'generators': ['R', 'F', 'Uw'],
                'inner_moves': 0,
                'outer_moves': 3,
                'pauses': 0,
                'rotations': 0,
                'htm': 3,
                'qtm': 3,
                'stm': 3,
                'etm': 3,
                'rtm': 0,
                'qstm': 3,
            },
        )

    def test_metrics_pauses(self):
        algo = parse_moves('R..Fu.')
        self.assertEqual(
            algo.metrics,
            {
                'generators': ['R', 'F', 'u'],
                'inner_moves': 0,
                'outer_moves': 3,
                'pauses': 3,
                'rotations': 0,
                'htm': 3,
                'qtm': 3,
                'stm': 3,
                'etm': 3,
                'rtm': 0,
                'qstm': 3,
            },
        )
