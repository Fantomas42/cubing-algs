import unittest

from cubing_algs.parsing import parse_moves


class MetricsTestCase(unittest.TestCase):

    def test_metrics(self):
        algo = parse_moves("yM2UMU2M'UM2")
        self.assertEqual(
            algo.metrics,
            {
                'generators': ['M', 'U'],
                'inner_moves': 4,
                'outer_moves': 3,
                'rotations': 1,
                'htm': 11,
                'qtm': 16,
                'stm': 7,
                'etm': 8,
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
