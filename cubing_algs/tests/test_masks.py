import unittest

from cubing_algs.constants import INITIAL_STATE
from cubing_algs.masks import FULL_MASK
from cubing_algs.masks import facelets_masked
from cubing_algs.masks import intersection_masks
from cubing_algs.masks import negate_mask
from cubing_algs.masks import state_masked
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

    def test_facelets_masked_basic(self):
        facelets = 'ABCD'
        mask = '1010'
        expected = 'A-C-'
        self.assertEqual(facelets_masked(facelets, mask), expected)

    def test_facelets_masked_all_ones(self):
        facelets = 'ABCD'
        mask = '1111'
        expected = 'ABCD'
        self.assertEqual(facelets_masked(facelets, mask), expected)

    def test_facelets_masked_all_zeros(self):
        facelets = 'ABCD'
        mask = '0000'
        expected = '----'
        self.assertEqual(facelets_masked(facelets, mask), expected)

    def test_facelets_masked_empty(self):
        facelets = ''
        mask = ''
        expected = ''
        self.assertEqual(facelets_masked(facelets, mask), expected)

    def test_facelets_masked_single_char(self):
        facelets = 'X'
        mask = '1'
        expected = 'X'
        self.assertEqual(facelets_masked(facelets, mask), expected)

        facelets = 'X'
        mask = '0'
        expected = '-'
        self.assertEqual(facelets_masked(facelets, mask), expected)

    def test_facelets_masked_real_cube_pattern(self):
        facelets = INITIAL_STATE[:9]
        mask = '101010101'
        expected = 'U-U-U-U-U'
        self.assertEqual(facelets_masked(facelets, mask), expected)

    def test_state_masked_basic(self):
        mask = FULL_MASK
        result = state_masked(INITIAL_STATE, mask)

        self.assertEqual(result, INITIAL_STATE)

    def test_state_masked_all_zeros(self):
        mask = '0' * 54
        result = state_masked(INITIAL_STATE, mask)

        self.assertTrue(result.replace('0', '-'), mask)

    def test_state_masked_partial(self):
        mask = '1' * 9 + '0' * 45
        result = state_masked(INITIAL_STATE, mask)

        self.assertEqual(
            result,
            'UUUUUUUUU---------------------------------------------',
        )

    def test_state_masked_different_state(self):
        scrambled_state = (
            'LUULUUFFFLBBRRRRRRUUUFFDFFDRRBDDBDDBFFRLLDLLDLLDUBBUBB'
        )
        mask = '1' * 27 + '0' * 27
        result = state_masked(scrambled_state, mask)

        self.assertEqual(
            result,
            '-UU-UUFFF---RRRRRRUUUFF-FF-RR-------FFR---------U--U--',
        )
