"""Tests for binary mask operations."""

import unittest

from cubing_algs.constants import INITIAL_STATE
from cubing_algs.masks import _CACHE_SIZE_LIMIT
from cubing_algs.masks import _MASK_CACHE
from cubing_algs.masks import FULL_MASK
from cubing_algs.masks import facelets_masked
from cubing_algs.masks import intersection_masks
from cubing_algs.masks import negate_mask
from cubing_algs.masks import state_masked
from cubing_algs.masks import union_masks


class TestBinaryMasks(unittest.TestCase):  # noqa: PLR0904
    """Tests for binary mask operations on cube states."""

    def test_union(self) -> None:
        self.assertEqual(union_masks('1010', '0110'), '1110')
        self.assertEqual(union_masks('1111', '0000'), '1111')
        self.assertEqual(union_masks('0000', '0000'), '0000')

    def test_union_multiple(self) -> None:
        self.assertEqual(union_masks('1000', '0100', '0010', '0001'), '1111')
        self.assertEqual(union_masks('1010', '0101', '1100'), '1111')

    def test_union_single(self) -> None:
        self.assertEqual(union_masks('1010'), '1010')

    def test_union_empty(self) -> None:
        self.assertEqual(union_masks(), '')

    def test_intersection(self) -> None:
        self.assertEqual(intersection_masks('1010', '1100'), '1000')
        self.assertEqual(intersection_masks('1111', '0000'), '0000')
        self.assertEqual(intersection_masks('1111', '1111'), '1111')

    def test_intersection_multiple(self) -> None:
        self.assertEqual(intersection_masks('1111', '1110', '1100'), '1100')
        self.assertEqual(intersection_masks('1010', '0110', '1100'), '0000')

    def test_intersection_single(self) -> None:
        self.assertEqual(intersection_masks('1010'), '1010')

    def test_intersection_empty(self) -> None:
        self.assertEqual(intersection_masks(), '')

    def test_negate(self) -> None:
        self.assertEqual(negate_mask('1010'), '0101')
        self.assertEqual(negate_mask('0000'), '1111')
        self.assertEqual(negate_mask('1111'), '0000')

    def test_negate_single_bit(self) -> None:
        self.assertEqual(negate_mask('1'), '0')
        self.assertEqual(negate_mask('0'), '1')

    def test_negate_empty(self) -> None:
        self.assertEqual(negate_mask(''), '')

    def test_facelets_masked_basic(self) -> None:
        facelets = 'ABCD'
        mask = '1010'
        expected = 'A-C-'
        self.assertEqual(facelets_masked(facelets, mask), expected)

    def test_facelets_masked_all_ones(self) -> None:
        facelets = 'ABCD'
        mask = '1111'
        expected = 'ABCD'
        self.assertEqual(facelets_masked(facelets, mask), expected)

    def test_facelets_masked_all_zeros(self) -> None:
        facelets = 'ABCD'
        mask = '0000'
        expected = '----'
        self.assertEqual(facelets_masked(facelets, mask), expected)

    def test_facelets_masked_empty(self) -> None:
        facelets = ''
        mask = ''
        expected = ''
        self.assertEqual(facelets_masked(facelets, mask), expected)

    def test_facelets_masked_single_char(self) -> None:
        facelets = 'X'
        mask = '1'
        expected = 'X'
        self.assertEqual(facelets_masked(facelets, mask), expected)

        facelets = 'X'
        mask = '0'
        expected = '-'
        self.assertEqual(facelets_masked(facelets, mask), expected)

    def test_facelets_masked_real_cube_pattern(self) -> None:
        facelets = INITIAL_STATE[:9]
        mask = '101010101'
        expected = 'U-U-U-U-U'
        self.assertEqual(facelets_masked(facelets, mask), expected)

    def test_state_masked_basic(self) -> None:
        mask = FULL_MASK
        result = state_masked(INITIAL_STATE, mask)

        self.assertEqual(result, INITIAL_STATE)

    def test_state_masked_all_zeros(self) -> None:
        mask = '0' * 54
        result = state_masked(INITIAL_STATE, mask)

        self.assertTrue(result.replace('0', '-'), mask)

    def test_state_masked_partial(self) -> None:
        mask = '1' * 9 + '0' * 45
        result = state_masked(INITIAL_STATE, mask)

        self.assertEqual(
            result,
            'UUUUUUUUU---------------------------------------------',
        )

    def test_state_masked_different_state(self) -> None:
        scrambled_state = (
            'LUULUUFFFLBBRRRRRRUUUFFDFFDRRBDDBDDBFFRLLDLLDLLDUBBUBB'
        )
        mask = '1' * 27 + '0' * 27
        result = state_masked(scrambled_state, mask)

        self.assertEqual(
            result,
            '-UU-UUFFF---RRRRRRUUUFF-FF-RR-------FFR---------U--U--',
        )

    def test_facelets_masked_cache_hit(self) -> None:
        """Test cache hit path in optimized facelets_masked."""
        _MASK_CACHE.clear()

        facelets = 'ABCD'
        mask = '1010'

        # First call - cache miss
        result1 = facelets_masked(facelets, mask)
        self.assertEqual(result1, 'A-C-')
        self.assertIn(mask, _MASK_CACHE)

        # Second call - cache hit (covers lines 74-75)
        result2 = facelets_masked(facelets, mask)
        self.assertEqual(result2, 'A-C-')
        self.assertEqual(result1, result2)

    def test_facelets_masked_cache_eviction(self) -> None:
        """Test cache eviction when size limit is reached."""
        _MASK_CACHE.clear()

        # Directly manipulate cache to test eviction by filling it beyond limit
        # This allows us to test the eviction logic paths (lines 86-88)

        # Fill cache manually to exactly the limit
        for i in range(_CACHE_SIZE_LIMIT):
            # Create unique keys and dummy values
            key_prefix = f'test_mask_{i:04d}'
            mask_key = key_prefix + '0' * (54 - len(key_prefix))
            _MASK_CACHE[mask_key] = tuple(bool(j % 2) for j in range(54))

        # Verify cache is at limit
        self.assertEqual(len(_MASK_CACHE), _CACHE_SIZE_LIMIT)

        # Now call facelets_masked with a new unique mask to trigger eviction
        test_facelets = INITIAL_STATE
        trigger_mask = '1' + '0' * 53  # Unique mask not in cache

        result = facelets_masked(test_facelets, trigger_mask)

        # Verify eviction occurred - cache should be reduced and new mask added
        expected_size = _CACHE_SIZE_LIMIT // 2 + 1
        self.assertEqual(len(_MASK_CACHE), expected_size)

        # The triggering mask should be in the cache
        self.assertIn(trigger_mask, _MASK_CACHE)

        # Verify the result is correct
        expected_result = 'U' + '-' * 53
        self.assertEqual(result, expected_result)

    def test_facelets_masked_cache_behavior_with_repeated_patterns(
        self,
    ) -> None:
        """Test cache behavior with realistic repeated mask usage."""
        _MASK_CACHE.clear()

        # Test with cube-sized strings and common patterns
        facelets = INITIAL_STATE
        common_masks = [FULL_MASK, '0' * 54, '1' * 27 + '0' * 27]

        # First round - populate cache
        results1 = [facelets_masked(facelets, mask) for mask in common_masks]

        # Verify all masks are cached
        for mask in common_masks:
            self.assertIn(mask, _MASK_CACHE)

        # Second round - should hit cache
        results2 = [facelets_masked(facelets, mask) for mask in common_masks]

        # Results should be identical
        self.assertEqual(results1, results2)
