import unittest

from cubing_algs.parsing import parse_moves


class MetricsTestCase(unittest.TestCase):

    def test_metrics(self):
        algo = parse_moves("M2UMU2M'UM2")
        self.assertEqual(
            algo.metrics,
            {
                'generators': ['M', 'U'],
                'inner_moves': 4,
                'outer_moves': 3,
                'rotations': 0,
                'htm': 11,
                'qtm': 16,
                'stm': 7,
                'etm': 7,
            },
        )
