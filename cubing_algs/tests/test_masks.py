import unittest

from cubing_algs.masks import intersection_masks
from cubing_algs.masks import negate_mask
from cubing_algs.masks import union_masks


class TestBinaryMasks(unittest.TestCase):

    def test_union(self):
        self.assertEqual(union_masks('1010', '0110'), '1110')
        self.assertEqual(union_masks('1111', '0000'), '1111')
        self.assertEqual(union_masks('0000', '0000'), '0000')

    def test_union_multiple(self):
        self.assertEqual(union_masks('1000', '0100', '0010', '0001'), '1111')
        self.assertEqual(union_masks('1010', '0101', '1100'), '1111')

    def test_union_single(self):
        self.assertEqual(union_masks('1010'), '1010')

    def test_union_empty(self):
        self.assertEqual(union_masks(), '')

    def test_intersection(self):
        self.assertEqual(intersection_masks('1010', '1100'), '1000')
        self.assertEqual(intersection_masks('1111', '0000'), '0000')
        self.assertEqual(intersection_masks('1111', '1111'), '1111')

    def test_intersection_multiple(self):
        self.assertEqual(intersection_masks('1111', '1110', '1100'), '1100')
        self.assertEqual(intersection_masks('1010', '0110', '1100'), '0000')

    def test_intersection_single(self):
        self.assertEqual(intersection_masks('1010'), '1010')

    def test_intersection_empty(self):
        self.assertEqual(intersection_masks(), '')

    def test_negate(self):
        self.assertEqual(negate_mask('1010'), '0101')
        self.assertEqual(negate_mask('0000'), '1111')
        self.assertEqual(negate_mask('1111'), '0000')

    def test_negate_single_bit(self):
        self.assertEqual(negate_mask('1'), '0')
        self.assertEqual(negate_mask('0'), '1')

    def test_negate_empty(self):
        self.assertEqual(negate_mask(''), '')
