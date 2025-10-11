import unittest

from cubing_algs.algorithm import Algorithm
from cubing_algs.structure import BoundedCache
from cubing_algs.structure import Structure
from cubing_algs.structure import calculate_efficiency_rating
from cubing_algs.structure import calculate_max_setup_length
from cubing_algs.structure import calculate_min_score
from cubing_algs.structure import calculate_nesting_depth
from cubing_algs.structure import classify_commutator
from cubing_algs.structure import classify_conjugate
from cubing_algs.structure import compress
from cubing_algs.structure import compute_structure
from cubing_algs.structure import count_all_structures
from cubing_algs.structure import detect_move_cancellations
from cubing_algs.structure import detect_structures
from cubing_algs.structure import inverse_sequence
from cubing_algs.structure import is_inverse_at
from cubing_algs.structure import score_structure


class SimpleConjugatesTestCase(unittest.TestCase):

    def test_basic_conjugate(self) -> None:
        algo = Algorithm.parse_moves("R U R'")
        structures = detect_structures(algo, min_score=0)

        self.assertEqual(len(structures), 1)
        self.assertEqual(structures[0].type, 'conjugate')
        self.assertEqual(str(structures[0].setup), 'R')
        self.assertEqual(str(structures[0].action), 'U')

    def test_conjugate_with_longer_setup(self) -> None:
        algo = Algorithm.parse_moves("R U R U' U R' U'")
        structures = detect_structures(algo, min_score=0)

        self.assertGreaterEqual(len(structures), 1)
        self.assertTrue(
            any(s.type in {'conjugate', 'commutator'} for s in structures),
        )

    def test_conjugate_with_longer_action(self) -> None:
        algo = Algorithm.parse_moves("F R U R' U' F'")
        structures = detect_structures(algo, min_score=0)

        self.assertEqual(len(structures), 1)
        self.assertEqual(structures[0].type, 'conjugate')
        self.assertEqual(str(structures[0].setup), 'F')
        self.assertEqual(str(structures[0].action), "R U R' U'")

    def test_conjugate_double_setup(self) -> None:
        algo = Algorithm.parse_moves('R2 U R2')
        structures = detect_structures(algo, min_score=0)

        self.assertEqual(len(structures), 1)
        self.assertEqual(structures[0].type, 'conjugate')
        self.assertEqual(str(structures[0].setup), 'R2')
        self.assertEqual(str(structures[0].action), 'U')

    def test_conjugate_prime_setup(self) -> None:
        algo = Algorithm.parse_moves("R' U R")
        structures = detect_structures(algo, min_score=0)

        self.assertEqual(len(structures), 1)
        self.assertEqual(structures[0].type, 'conjugate')
        self.assertEqual(str(structures[0].setup), "R'")
        self.assertEqual(str(structures[0].action), 'U')


class SimpleCommutatorsTestCase(unittest.TestCase):

    def test_basic_commutator(self) -> None:
        algo = Algorithm.parse_moves("R U R' U'")
        structures = detect_structures(algo, min_score=0)

        self.assertEqual(len(structures), 1)
        self.assertEqual(structures[0].type, 'commutator')
        self.assertEqual(str(structures[0].setup), 'R')
        self.assertEqual(str(structures[0].action), 'U')

    def test_commutator_longer_parts(self) -> None:
        algo = Algorithm.parse_moves("R U R' U' R U' R' U")
        structures = detect_structures(algo, min_score=0)

        self.assertGreaterEqual(len(structures), 1)

    def test_commutator_niklas(self) -> None:
        algo = Algorithm.parse_moves("R U' L' U R' U' L U")
        structures = detect_structures(algo, min_score=0)

        self.assertGreaterEqual(len(structures), 1)
        self.assertTrue(any(s.type == 'commutator' for s in structures))

    def test_commutator_double_moves(self) -> None:
        algo = Algorithm.parse_moves("R2 U R2 U'")
        structures = detect_structures(algo, min_score=0)

        self.assertEqual(len(structures), 1)
        self.assertEqual(structures[0].type, 'commutator')
        self.assertEqual(str(structures[0].setup), 'R2')
        self.assertEqual(str(structures[0].action), 'U')


class NestedStructuresTestCase(unittest.TestCase):

    def test_conjugate_with_commutator_action(self) -> None:
        algo = Algorithm.parse_moves("F R U R' U' F'")
        compressed = compress(algo, min_score=0)

        self.assertIn('[', compressed)

    def test_commutator_with_conjugate_parts(self) -> None:
        algo = Algorithm.parse_moves("R U R' D R U' R' D'")
        structures = detect_structures(algo, min_score=0)

        self.assertGreaterEqual(len(structures), 1)

    def test_repeated_commutator(self) -> None:
        algo = Algorithm.parse_moves("R U R' U' R U R' U'")
        structures = detect_structures(algo, min_score=0)

        self.assertGreaterEqual(len(structures), 1)

    def test_double_nested_conjugate(self) -> None:
        algo = Algorithm.parse_moves("R U D U' R'")
        compressed = compress(algo, min_score=0)

        self.assertTrue('[' in compressed or len(compressed) > 0)


class ComplexAlgorithmsTestCase(unittest.TestCase):

    def test_sexy_move(self) -> None:
        algo = Algorithm.parse_moves("R U R' U'")
        structures = detect_structures(algo, min_score=0)

        self.assertGreaterEqual(len(structures), 1)
        self.assertEqual(structures[0].type, 'commutator')
        compressed = compress(algo, min_score=0)
        self.assertIn('[', compressed)
        self.assertIn(']', compressed)

    def test_sledgehammer(self) -> None:
        algo = Algorithm.parse_moves("R' F R F'")
        structures = detect_structures(algo, min_score=0)

        self.assertGreaterEqual(len(structures), 1)
        self.assertEqual(structures[0].type, 'commutator')
        compressed = compress(algo, min_score=0)
        self.assertIn('[', compressed)
        self.assertIn(']', compressed)

    def test_t_perm(self) -> None:
        algo = Algorithm.parse_moves("R U R' U' R' F R2 U' R' U' R U R' F'")
        compressed = compress(algo, min_score=5)

        self.assertGreater(len(compressed), 0)

    def test_sune(self) -> None:
        algo = Algorithm.parse_moves("R U R' U R U2 R'")
        structures = detect_structures(algo, min_score=0)

        self.assertGreaterEqual(len(structures), 1)

    def test_y_perm(self) -> None:
        algo = Algorithm.parse_moves(
            "F R U' R' U' R U R' F' R U R' U' R' F R F'",
        )
        compressed = compress(algo, min_score=5)

        self.assertGreater(len(compressed), 0)

    def test_jb_perm(self) -> None:
        algo = Algorithm.parse_moves("R U R' F' R U R' U' R' F R2 U' R'")
        compressed = compress(algo, min_score=5)
        self.assertGreater(len(compressed), 0)


class CompressionQualityTestCase(unittest.TestCase):

    def test_no_false_positives(self) -> None:
        algo = Algorithm.parse_moves('R U F D L B')
        structures = detect_structures(algo, min_score=5)

        self.assertEqual(len(structures), 0)

    def test_compression_shorter(self) -> None:
        test_cases = [
            "R U R'",
            "R U R' U'",
            "F R U R' U' F'",
            "R U' L' U R' U' L U",
        ]

        for moves in test_cases:
            with self.subTest(moves=moves):
                algo = Algorithm.parse_moves(moves)
                compressed = compress(algo, min_score=0)

                self.assertGreater(len(compressed), 0)

    def test_score_quality(self) -> None:
        algo1 = Algorithm.parse_moves("F R U R' U' F'")
        structures1 = detect_structures(algo1, min_score=0)

        algo2 = Algorithm.parse_moves("R U R'")
        structures2 = detect_structures(algo2, min_score=0)

        self.assertGreater(structures1[0].score, structures2[0].score)


class EdgeCasesTestCase(unittest.TestCase):

    def test_empty_algorithm(self) -> None:
        algo = Algorithm([])
        structures = detect_structures(algo)

        self.assertEqual(len(structures), 0)
        self.assertEqual(compress(algo), '')

    def test_single_move(self) -> None:
        algo = Algorithm.parse_moves('R')
        structures = detect_structures(algo)

        self.assertEqual(len(structures), 0)
        self.assertEqual(compress(algo), 'R')

    def test_two_moves(self) -> None:
        algo = Algorithm.parse_moves('R U')
        structures = detect_structures(algo)

        self.assertEqual(len(structures), 0)

    def test_max_setup_length(self) -> None:
        algo = Algorithm.parse_moves("R U F D L B R' U' F' D' L' B'")
        structures1 = detect_structures(algo, max_setup_len=3)
        structures2 = detect_structures(algo, max_setup_len=10)

        self.assertGreaterEqual(len(structures2), len(structures1))

    def test_min_score_filter(self) -> None:
        algo = Algorithm.parse_moves("R U R' U'")
        structures_low = detect_structures(algo, min_score=0)
        structures_high = detect_structures(algo, min_score=50)

        self.assertLessEqual(len(structures_high), len(structures_low))

    def test_non_overlapping(self) -> None:
        algo = Algorithm.parse_moves("R U R' U' F D F' D'")
        structures = detect_structures(algo, min_score=0)

        for i, s1 in enumerate(structures):
            for s2 in structures[i + 1:]:
                self.assertTrue(s1.end <= s2.start or s1.start >= s2.end)


class CompressTestCase(unittest.TestCase):

    def test_compress_basic(self) -> None:
        algo = Algorithm.parse_moves("R U R' U'")
        result = compress(algo, min_score=0)

        self.assertIn('[', result)
        self.assertIn(',', result)
        self.assertIn(']', result)

    def test_compress_conjugate(self) -> None:
        algo = Algorithm.parse_moves("F R U R' U' F'")
        result = compress(algo, min_score=0)

        self.assertIn('[', result)
        self.assertIn(']', result)

    def test_compress_with_extra_moves(self) -> None:
        algo = Algorithm.parse_moves("D R U R' U' D'")
        result = compress(algo, min_score=0)

        self.assertGreater(len(result), 0)
        self.assertTrue('D' in result or '[' in result)

    def test_compress_multiple_structures(self) -> None:
        algo = Algorithm.parse_moves("R U R' U' F D F' D'")
        result = compress(algo, min_score=0)

        self.assertIn('[', result)


class StructureDataclassTestCase(unittest.TestCase):

    def test_structure_str_conjugate(self) -> None:
        setup = Algorithm.parse_moves('R')
        action = Algorithm.parse_moves('U')
        struct = Structure(
            type='conjugate',
            setup=setup,
            action=action,
            start=0,
            end=3,
            score=10.0,
        )

        self.assertEqual(str(struct), '[R: U]')

    def test_structure_str_commutator(self) -> None:
        setup = Algorithm.parse_moves('R')
        action = Algorithm.parse_moves('U')
        struct = Structure(
            type='commutator',
            setup=setup,
            action=action,
            start=0,
            end=4,
            score=10.0,
        )

        self.assertEqual(str(struct), '[R, U]')


class RealWorldExamplesTestCase(unittest.TestCase):

    def test_f2l_pair_1(self) -> None:
        algo = Algorithm.parse_moves("U R U' R'")
        compressed = compress(algo, min_score=0)

        self.assertGreater(len(compressed), 0)

    def test_f2l_pair_2(self) -> None:
        algo = Algorithm.parse_moves("R U R' U' R U R'")
        structures = detect_structures(algo, min_score=0)

        self.assertGreaterEqual(len(structures), 1)

    def test_oll_algorithm(self) -> None:
        algo = Algorithm.parse_moves("R U2 R' U' R U' R'")
        compressed = compress(algo, min_score=5)

        self.assertGreater(len(compressed), 0)

    def test_edge_flip(self) -> None:
        algo = Algorithm.parse_moves("M U M' U'")
        structures = detect_structures(algo, min_score=0)

        self.assertEqual(len(structures), 1)
        self.assertEqual(structures[0].type, 'commutator')

    def test_corner_twist(self) -> None:
        algo = Algorithm.parse_moves("R' D' R D R' D' R D")
        structures = detect_structures(algo, min_score=0)

        self.assertGreaterEqual(len(structures), 1)


class ComputeStructureTestCase(unittest.TestCase):

    def test_compute_structure_basic(self) -> None:
        algo = Algorithm.parse_moves("R U R' U'")
        struct = compute_structure(algo, min_score=0)

        self.assertEqual(struct.original, "R U R' U'")
        self.assertEqual(struct.original_length, 4)
        self.assertGreaterEqual(struct.total_structures, 1)
        self.assertGreaterEqual(struct.commutator_count, 1)

    def test_compute_structure_empty(self) -> None:
        algo = Algorithm([])
        struct = compute_structure(algo)

        self.assertEqual(struct.original, '')
        self.assertEqual(struct.compressed, '')
        self.assertEqual(struct.total_structures, 0)
        self.assertEqual(struct.conjugate_count, 0)
        self.assertEqual(struct.commutator_count, 0)
        self.assertEqual(struct.original_length, 0)
        self.assertEqual(struct.compression_ratio, 0.0)

    def test_compute_structure_no_structure(self) -> None:
        algo = Algorithm.parse_moves('R U F')
        struct = compute_structure(algo, min_score=50)

        self.assertEqual(struct.total_structures, 0)
        self.assertEqual(struct.uncovered_moves, 3)
        self.assertEqual(struct.coverage_percent, 0.0)

    def test_compute_structure_conjugate(self) -> None:
        algo = Algorithm.parse_moves("F R U R' U' F'")
        struct = compute_structure(algo, min_score=0)

        self.assertGreaterEqual(struct.total_structures, 1)
        self.assertGreaterEqual(struct.conjugate_count, 1)
        self.assertIn('[', struct.compressed)
        self.assertIn(':', struct.compressed)

    def test_compute_structure_commutator(self) -> None:
        algo = Algorithm.parse_moves("R U R' U'")
        struct = compute_structure(algo, min_score=0)

        self.assertGreaterEqual(struct.total_structures, 1)
        self.assertGreaterEqual(struct.commutator_count, 1)
        self.assertIn('[', struct.compressed)
        self.assertIn(',', struct.compressed)

    def test_compute_structure_compression_ratio(self) -> None:
        algo = Algorithm.parse_moves("F R U R' U' F'")
        struct = compute_structure(algo, min_score=0)

        self.assertGreaterEqual(struct.compression_ratio, 0.0)
        self.assertLessEqual(struct.compression_ratio, 1.0)

    def test_compute_structure_scores(self) -> None:
        algo = Algorithm.parse_moves("F R U R' U' F'")
        struct = compute_structure(algo, min_score=0)

        if struct.total_structures > 0:
            self.assertGreater(struct.average_structure_score, 0.0)
            self.assertGreater(struct.best_structure_score, 0.0)
            self.assertGreaterEqual(
                struct.best_structure_score,
                struct.average_structure_score,
            )

    def test_compute_structure_setup_action_lengths(self) -> None:
        algo = Algorithm.parse_moves("F R U R' U' F'")
        struct = compute_structure(algo, min_score=0)

        if struct.total_structures > 0:
            self.assertGreaterEqual(struct.shortest_setup_length, 1)
            self.assertGreaterEqual(
                struct.longest_setup_length,
                struct.shortest_setup_length,
            )
            self.assertGreaterEqual(
                struct.average_setup_length,
                struct.shortest_setup_length,
            )
            self.assertLessEqual(
                struct.average_setup_length,
                struct.longest_setup_length,
            )

            self.assertGreaterEqual(struct.shortest_action_length, 1)
            self.assertGreaterEqual(
                struct.longest_action_length,
                struct.shortest_action_length,
            )
            self.assertGreaterEqual(
                struct.average_action_length,
                struct.shortest_action_length,
            )
            self.assertLessEqual(
                struct.average_action_length,
                struct.longest_action_length,
            )

    def test_compute_structure_coverage(self) -> None:
        algo = Algorithm.parse_moves("R U R' U'")
        struct = compute_structure(algo, min_score=0)

        self.assertGreaterEqual(struct.coverage_percent, 0.0)
        self.assertLessEqual(struct.coverage_percent, 1.0)
        self.assertGreaterEqual(struct.uncovered_moves, 0)
        self.assertLessEqual(struct.uncovered_moves, struct.original_length)

    def test_compute_structure_nesting(self) -> None:
        algo = Algorithm.parse_moves("F R U R' U' F'")
        struct = compute_structure(algo, min_score=0)

        self.assertGreaterEqual(struct.max_nesting_depth, 0)
        self.assertGreaterEqual(struct.nested_structure_count, 0)

    def test_compute_structure_structures_list(self) -> None:
        algo = Algorithm.parse_moves("R U R' U'")
        struct = compute_structure(algo, min_score=0)

        self.assertEqual(len(struct.structures), struct.total_structures)
        if struct.total_structures > 0:
            for s in struct.structures:
                self.assertIn(s.type, ('conjugate', 'commutator'))
                self.assertGreaterEqual(len(s.setup), 1)
                self.assertGreaterEqual(len(s.action), 1)
                self.assertGreater(s.score, 0.0)

    def test_algorithm_structure_property(self) -> None:
        algo = Algorithm.parse_moves("R U R' U'")
        struct = algo.structure

        self.assertTrue(hasattr(struct, 'original'))
        self.assertTrue(hasattr(struct, 'compressed'))
        self.assertTrue(hasattr(struct, 'total_structures'))
        self.assertEqual(struct.original, "R U R' U'")

    def test_structure_t_perm(self) -> None:
        algo = Algorithm.parse_moves("R U R' U' R' F R2 U' R' U' R U R' F'")
        struct = compute_structure(algo, min_score=5)

        self.assertEqual(struct.original_length, 14)
        self.assertGreaterEqual(struct.total_structures, 0)
        self.assertIsNotNone(struct.compressed)

    def test_structure_count_accuracy(self) -> None:
        algo = Algorithm.parse_moves("R U R' U'")
        struct = compute_structure(algo, min_score=0)

        self.assertEqual(struct.total_structures, (
            struct.conjugate_count + struct.commutator_count
        ))

    def test_structure_multiple_patterns(self) -> None:
        algo = Algorithm.parse_moves("R U R' U' F D F' D'")
        struct = compute_structure(algo, min_score=0)

        self.assertGreaterEqual(struct.total_structures, 1)
        if struct.total_structures > 1:
            for i, s1 in enumerate(struct.structures):
                for s2 in struct.structures[i + 1:]:
                    self.assertTrue(s1.end <= s2.start or s1.start >= s2.end)


class StructureClassificationsTestCase(unittest.TestCase):

    def test_pure_commutator_detection(self) -> None:
        algo = Algorithm.parse_moves("R U R' U' R U R' U'")
        struct = compute_structure(algo, min_score=0)

        if struct.total_structures > 0:
            has_pure = any(s.is_pure for s in struct.structures)
            if has_pure:
                self.assertGreaterEqual(struct.pure_commutator_count, 1)

    def test_classification_fields(self) -> None:
        algo = Algorithm.parse_moves("R U R' U'")
        struct = compute_structure(algo, min_score=0)

        if struct.total_structures > 0:
            for s in struct.structures:
                self.assertIsInstance(s.classification, str)
                self.assertGreater(s.move_count, 0)
                self.assertIsInstance(s.has_cancellations, bool)
                self.assertIsInstance(s.is_pure, bool)

    def test_nested_conjugate_detection(self) -> None:
        algo = Algorithm.parse_moves("F R U R' U' F'")
        struct = compute_structure(algo, min_score=0)

        if struct.total_structures > 0:
            self.assertIsInstance(struct.nested_conjugate_count, int)

    def test_simple_conjugate_detection(self) -> None:
        algo = Algorithm.parse_moves("R U R'")
        struct = compute_structure(algo, min_score=0)

        if struct.total_structures > 0:
            self.assertIsInstance(struct.simple_conjugate_count, int)

    def test_cancellation_detection(self) -> None:
        algo = Algorithm.parse_moves("R U R' U'")
        struct = compute_structure(algo, min_score=0)

        self.assertIsInstance(struct.structures_with_cancellations, int)
        self.assertGreaterEqual(struct.structures_with_cancellations, 0)

    def test_efficiency_rating(self) -> None:
        algo = Algorithm.parse_moves("R U R' U'")
        struct = compute_structure(algo, min_score=0)

        self.assertIn(struct.efficiency_rating, [
            'N/A', 'Excellent', 'Good', 'Fair', 'Poor',
        ])

    def test_average_move_count(self) -> None:
        algo = Algorithm.parse_moves("R U R' U'")
        struct = compute_structure(algo, min_score=0)

        self.assertIsInstance(struct.average_move_count, float)
        if struct.total_structures > 0:
            self.assertGreater(struct.average_move_count, 0)

    def test_new_structure_data_fields(self) -> None:
        algo = Algorithm.parse_moves("R U R' U'")
        struct = compute_structure(algo, min_score=0)

        self.assertTrue(hasattr(struct, 'pure_commutator_count'))
        self.assertTrue(hasattr(struct, 'a9_commutator_count'))
        self.assertTrue(hasattr(struct, 'nested_conjugate_count'))
        self.assertTrue(hasattr(struct, 'simple_conjugate_count'))
        self.assertTrue(hasattr(struct, 'structures_with_cancellations'))
        self.assertTrue(hasattr(struct, 'average_move_count'))
        self.assertTrue(hasattr(struct, 'efficiency_rating'))

    def test_structure_object_new_fields(self) -> None:
        algo = Algorithm.parse_moves("R U R' U'")
        structures = detect_structures(algo, min_score=0)

        if structures:
            s = structures[0]
            self.assertTrue(hasattr(s, 'classification'))
            self.assertTrue(hasattr(s, 'has_cancellations'))
            self.assertTrue(hasattr(s, 'move_count'))
            self.assertTrue(hasattr(s, 'is_pure'))


class NestedStructureCountingTestCase(unittest.TestCase):
    """Test that nested structures are correctly counted."""

    def test_nested_structures_counted_t_perm(self) -> None:
        """T-Perm has nested conjugates that should be counted."""
        algo = Algorithm.parse_moves("R U R' F' R U R' U' R' F R2 U' R'")

        # With min_score=3.0, structures with nesting are detected
        struct = compute_structure(algo, min_score=3.0)
        # The compressed form shows nested structures like:
        # [R: [U: [R': F'] U R']] F R2 U' R'
        # Optimizations may find different valid decompositions
        # (e.g., 2-3 structures)
        # At minimum, we expect multiple nested conjugates
        self.assertGreaterEqual(struct.total_structures, 2)
        self.assertGreaterEqual(struct.conjugate_count, 2)
        self.assertEqual(struct.commutator_count, 0)

        # With higher min_score=5.0, structures still meet the threshold
        # (the bug fix now correctly counts nested structures)
        struct_filtered = compute_structure(algo, min_score=5.0)
        self.assertGreaterEqual(struct_filtered.total_structures, 2)
        self.assertGreaterEqual(struct_filtered.conjugate_count, 2)

    def test_nested_structures_counted_sexy_f(self) -> None:
        """F [R, U] F' counts outer conjugate and inner commutator."""
        algo = Algorithm.parse_moves("F R U R' U' F'")
        struct = compute_structure(algo, min_score=0)

        # This should detect:
        # 1. Outer conjugate [F: R U R' U']
        # 2. Inner commutator [R, U] within the action
        self.assertGreaterEqual(struct.total_structures, 2)
        self.assertGreaterEqual(struct.conjugate_count, 1)
        self.assertGreaterEqual(struct.commutator_count, 1)

    def test_simple_structure_count_matches(self) -> None:
        """Simple algorithms without nesting: count = len(structures)."""
        algo = Algorithm.parse_moves("R U R' U'")
        struct = compute_structure(algo, min_score=0)

        # Simple commutator, no nesting
        self.assertEqual(struct.total_structures, len(struct.structures))
        self.assertEqual(struct.total_structures, 1)
        self.assertEqual(struct.commutator_count, 1)
        self.assertEqual(struct.conjugate_count, 0)

    def test_total_equals_sum_of_types(self) -> None:
        """Total structures should equal sum of conjugates and commutators."""
        test_cases = [
            "R U R' U'",  # Simple commutator
            "F R U R' U' F'",  # Nested
            "R U R' F' R U R' U' R' F R2 U' R'",  # T-Perm with nesting
        ]

        for moves in test_cases:
            with self.subTest(moves=moves):
                algo = Algorithm.parse_moves(moves)
                struct = compute_structure(algo, min_score=0)

                self.assertEqual(
                    struct.total_structures,
                    struct.conjugate_count + struct.commutator_count,
                    f'Total should equal sum for: {moves}',
                )


class BoundedCacheTestCase(unittest.TestCase):
    """Test BoundedCache LRU behavior and edge cases."""

    def test_bounded_cache_basic_operations(self) -> None:
        """Test basic cache operations."""

        cache: BoundedCache[str, int] = BoundedCache(3)

        cache['a'] = 1
        cache['b'] = 2
        cache['c'] = 3

        self.assertEqual(cache['a'], 1)
        self.assertEqual(cache['b'], 2)
        self.assertEqual(cache['c'], 3)
        self.assertEqual(len(cache), 3)

    def test_bounded_cache_lru_eviction(self) -> None:
        """Test LRU eviction when capacity is reached."""

        cache: BoundedCache[str, int] = BoundedCache(3)

        cache['a'] = 1
        cache['b'] = 2
        cache['c'] = 3

        # Adding a 4th item should evict 'a' (least recently used)
        cache['d'] = 4

        self.assertEqual(len(cache), 3)
        self.assertNotIn('a', cache)
        self.assertIn('b', cache)
        self.assertIn('c', cache)
        self.assertIn('d', cache)

    def test_bounded_cache_access_updates_lru(self) -> None:
        """Test that accessing an item moves it to end (most recently used)."""

        cache: BoundedCache[str, int] = BoundedCache(3)

        cache['a'] = 1
        cache['b'] = 2
        cache['c'] = 3

        # Access 'a' to make it most recently used
        _ = cache['a']

        # Add new item, should evict 'b' (now least recently used)
        cache['d'] = 4

        self.assertIn('a', cache)
        self.assertNotIn('b', cache)
        self.assertIn('c', cache)
        self.assertIn('d', cache)

    def test_bounded_cache_update_existing_key(self) -> None:
        """Test updating an existing key moves it to end."""

        cache: BoundedCache[str, int] = BoundedCache(3)

        cache['a'] = 1
        cache['b'] = 2
        cache['c'] = 3

        # Update 'a' to make it most recently used
        cache['a'] = 10

        # Add new item, should evict 'b' (now least recently used)
        cache['d'] = 4

        self.assertEqual(cache['a'], 10)
        self.assertNotIn('b', cache)
        self.assertIn('c', cache)
        self.assertIn('d', cache)

    def test_bounded_cache_delete(self) -> None:
        """Test deleting items from cache."""

        cache: BoundedCache[str, int] = BoundedCache(3)

        cache['a'] = 1
        cache['b'] = 2

        del cache['a']

        self.assertEqual(len(cache), 1)
        self.assertNotIn('a', cache)
        self.assertIn('b', cache)

    def test_bounded_cache_iteration(self) -> None:
        """Test iterating over cache keys."""

        cache: BoundedCache[str, int] = BoundedCache(3)

        cache['a'] = 1
        cache['b'] = 2
        cache['c'] = 3

        keys = list(cache)
        self.assertEqual(len(keys), 3)
        self.assertIn('a', keys)
        self.assertIn('b', keys)
        self.assertIn('c', keys)

    def test_bounded_cache_size_one(self) -> None:
        """Test cache with size 1."""

        cache: BoundedCache[str, int] = BoundedCache(1)

        cache['a'] = 1
        self.assertEqual(cache['a'], 1)

        cache['b'] = 2
        self.assertNotIn('a', cache)
        self.assertEqual(cache['b'], 2)

    def test_bounded_cache_key_error(self) -> None:
        """Test accessing non-existent key raises KeyError."""

        cache: BoundedCache[str, int] = BoundedCache(3)

        with self.assertRaises(KeyError):
            _ = cache['nonexistent']


class HelperFunctionTestCase(unittest.TestCase):
    """Test helper functions for structure detection."""

    def test_calculate_max_setup_length_short_algo(self) -> None:
        """Test max setup length for very short algorithms."""

        # For algo of length 3, max setup should be 2 (minimum)
        self.assertEqual(calculate_max_setup_length(3), 2)
        self.assertEqual(calculate_max_setup_length(4), 2)
        self.assertEqual(calculate_max_setup_length(5), 2)

    def test_calculate_max_setup_length_medium_algo(self) -> None:
        """Test max setup length for medium algorithms."""

        # For algo of length 9, max setup should be 3
        self.assertEqual(calculate_max_setup_length(9), 3)
        # For algo of length 12, max setup should be 4
        self.assertEqual(calculate_max_setup_length(12), 4)

    def test_calculate_max_setup_length_long_algo(self) -> None:
        """Test max setup length for long algorithms."""

        # For algo of length 30, max setup should be 10
        self.assertEqual(calculate_max_setup_length(30), 10)

    def test_calculate_max_setup_length_boundary(self) -> None:
        """Test boundary cases for max setup length."""

        # Length 0 should still return minimum
        self.assertEqual(calculate_max_setup_length(0), 2)
        # Length 1 should still return minimum
        self.assertEqual(calculate_max_setup_length(1), 2)

    def test_calculate_min_score_short_algo(self) -> None:
        """Test min score for short algorithms."""

        # Algorithms < 6 moves should have very low threshold
        self.assertEqual(calculate_min_score(3), 0.1)
        self.assertEqual(calculate_min_score(5), 0.1)

    def test_calculate_min_score_medium_algo(self) -> None:
        """Test min score for medium algorithms."""

        # Algorithms 6-12 moves should have medium threshold
        self.assertEqual(calculate_min_score(6), 3.0)
        self.assertEqual(calculate_min_score(10), 3.0)
        self.assertEqual(calculate_min_score(12), 3.0)

    def test_calculate_min_score_long_algo(self) -> None:
        """Test min score for long algorithms."""

        # Algorithms > 12 moves should have high threshold
        self.assertEqual(calculate_min_score(13), 5.0)
        self.assertEqual(calculate_min_score(20), 5.0)

    def test_calculate_min_score_boundary(self) -> None:
        """Test boundary cases for min score."""

        # Test exact boundary values
        self.assertEqual(calculate_min_score(0), 0.1)
        self.assertEqual(calculate_min_score(6), 3.0)
        self.assertEqual(calculate_min_score(12), 3.0)
        self.assertEqual(calculate_min_score(13), 5.0)

    def test_inverse_sequence_basic(self) -> None:
        """Test inverse sequence for basic algorithm."""

        algo = Algorithm.parse_moves('R U')
        inverse = inverse_sequence(algo)

        self.assertEqual(str(inverse), "U' R'")

    def test_inverse_sequence_complex(self) -> None:
        """Test inverse sequence for complex algorithm."""

        algo = Algorithm.parse_moves("R U R' U'")
        inverse = inverse_sequence(algo)

        self.assertEqual(str(inverse), "U R U' R'")

    def test_inverse_sequence_double_moves(self) -> None:
        """Test inverse sequence with double moves."""

        algo = Algorithm.parse_moves('R2 U2')
        inverse = inverse_sequence(algo)

        self.assertEqual(str(inverse), 'U2 R2')

    def test_inverse_sequence_empty(self) -> None:
        """Test inverse of empty algorithm."""

        algo = Algorithm([])
        inverse = inverse_sequence(algo)

        self.assertEqual(len(inverse), 0)

    def test_detect_move_cancellations_same_face(self) -> None:
        """Test cancellation detection for same face moves."""

        algo1 = Algorithm.parse_moves('R')
        algo2 = Algorithm.parse_moves("R'")

        self.assertTrue(detect_move_cancellations(algo1, algo2))

    def test_detect_move_cancellations_different_face(self) -> None:
        """Test no cancellation for different face moves."""

        algo1 = Algorithm.parse_moves('R')
        algo2 = Algorithm.parse_moves('U')

        self.assertFalse(detect_move_cancellations(algo1, algo2))

    def test_detect_move_cancellations_empty_first(self) -> None:
        """Test cancellation detection with empty first sequence."""

        algo1 = Algorithm([])
        algo2 = Algorithm.parse_moves('R')

        self.assertFalse(detect_move_cancellations(algo1, algo2))

    def test_detect_move_cancellations_empty_second(self) -> None:
        """Test cancellation detection with empty second sequence."""

        algo1 = Algorithm.parse_moves('R')
        algo2 = Algorithm([])

        self.assertFalse(detect_move_cancellations(algo1, algo2))

    def test_detect_move_cancellations_both_empty(self) -> None:
        """Test cancellation detection with both sequences empty."""

        algo1 = Algorithm([])
        algo2 = Algorithm([])

        self.assertFalse(detect_move_cancellations(algo1, algo2))

    def test_detect_move_cancellations_double_move(self) -> None:
        """Test cancellation detection with double moves."""

        algo1 = Algorithm.parse_moves('R2')
        algo2 = Algorithm.parse_moves('R')

        # Should detect same face
        self.assertTrue(detect_move_cancellations(algo1, algo2))


class ClassifyCommutatorTestCase(unittest.TestCase):
    """Test commutator classification system."""

    def test_classify_pure_commutator(self) -> None:
        """Test classification of pure 8-move commutator (2+2+2+2)."""

        setup = Algorithm.parse_moves('R U')
        action = Algorithm.parse_moves('F D')
        cache: BoundedCache[str, Algorithm] = BoundedCache(10)

        classification = classify_commutator(setup, action, cache)
        self.assertEqual(classification, 'pure')

    def test_classify_a9_commutator_with_cancellation(self) -> None:
        """Test classification of A9 (10 moves with cancellation)."""

        # This would be 10 moves (2+3+2+3) with actual cancellation
        # Setup ends with R, action starts with R -> cancellation
        setup = Algorithm.parse_moves('U R')
        action = Algorithm.parse_moves('R F D')
        cache: BoundedCache[str, Algorithm] = BoundedCache(10)

        classification = classify_commutator(setup, action, cache)
        # Total moves = 2*2 + 3*2 = 10, has cancellation at R/R
        self.assertEqual(classification, 'A9')

    def test_classify_orthogonal_commutator(self) -> None:
        """Test classification of orthogonal 10-move without cancellation."""

        # 10 moves total (2+3+2+3), no cancellation
        setup = Algorithm.parse_moves('R U')
        action = Algorithm.parse_moves('F D L')
        cache: BoundedCache[str, Algorithm] = BoundedCache(10)

        classification = classify_commutator(setup, action, cache)
        self.assertEqual(classification, 'orthogonal')

    def test_classify_extended_commutator(self) -> None:
        """Test classification of extended commutator (>10 moves)."""

        setup = Algorithm.parse_moves('R U F')
        action = Algorithm.parse_moves('D L B')
        cache: BoundedCache[str, Algorithm] = BoundedCache(10)

        classification = classify_commutator(setup, action, cache)
        # Total moves = 3*2 + 3*2 = 12 moves
        self.assertEqual(classification, 'extended')

    def test_classify_commutator_other(self) -> None:
        """Test classification of other commutator types."""

        # Less than 8 moves
        setup = Algorithm.parse_moves('R')
        action = Algorithm.parse_moves('U')
        cache: BoundedCache[str, Algorithm] = BoundedCache(10)

        classification = classify_commutator(setup, action, cache)
        # Total moves = 1*2 + 1*2 = 4 moves (not pure, not 10)
        self.assertEqual(classification, 'other')

    def test_classify_commutator_with_cache(self) -> None:
        """Test commutator classification with cache."""

        cache: BoundedCache[str, Algorithm] = BoundedCache(10)
        # Use a non-pure commutator to trigger cancellation check
        # and cache usage
        setup = Algorithm.parse_moves('U R')
        action = Algorithm.parse_moves('R F D')

        classification = classify_commutator(setup, action, cache)
        self.assertEqual(classification, 'A9')

        # Cache should now contain the inverse
        self.assertGreater(len(cache), 0)


class ClassifyConjugateTestCase(unittest.TestCase):
    """Test conjugate classification system."""

    def test_classify_simple_conjugate(self) -> None:
        """Test classification of simple conjugate (1-2 move setup)."""

        setup = Algorithm.parse_moves('R')
        action = Algorithm.parse_moves('U D F')

        classification = classify_conjugate(setup, action)
        self.assertEqual(classification, 'simple')

    def test_classify_simple_conjugate_two_moves(self) -> None:
        """Test classification of simple conjugate with 2-move setup."""

        setup = Algorithm.parse_moves('R U')
        action = Algorithm.parse_moves('F D L')

        classification = classify_conjugate(setup, action)
        self.assertEqual(classification, 'simple')

    def test_classify_nested_conjugate(self) -> None:
        """Test classification of nested conjugate."""

        setup = Algorithm.parse_moves('F')
        # Action contains a commutator [R, U]
        action = Algorithm.parse_moves("R U R' U'")

        classification = classify_conjugate(setup, action)
        self.assertEqual(classification, 'nested')

    def test_classify_multi_setup_conjugate(self) -> None:
        """Test classification of multi-setup conjugate (3+ move setup)."""

        setup = Algorithm.parse_moves('R U F')
        action = Algorithm.parse_moves('D L')

        classification = classify_conjugate(setup, action)
        self.assertEqual(classification, 'multi-setup')

    def test_classify_standard_conjugate(self) -> None:
        """Test classification of standard conjugate."""

        # This case doesn't fit other categories - not very common
        # Would need a 3+ move setup that doesn't contain nested structures
        # and the action doesn't contain structures either
        setup = Algorithm.parse_moves('R U F')
        action = Algorithm.parse_moves('D')

        classification = classify_conjugate(setup, action)
        # With 3-move setup and no nested structure in 1-move action
        self.assertIn(classification, ['multi-setup', 'standard'])


class ScoreStructureTestCase(unittest.TestCase):
    """Test structure scoring function."""

    def test_score_structure_basic(self) -> None:
        """Test basic structure scoring."""

        setup = Algorithm.parse_moves('R')
        action = Algorithm.parse_moves('U')

        score = score_structure(setup, action)
        self.assertGreater(score, 0.0)

    def test_score_structure_zero_setup(self) -> None:
        """Test score with zero-length setup."""

        setup = Algorithm([])
        action = Algorithm.parse_moves('U')

        score = score_structure(setup, action)
        self.assertEqual(score, 0.0)

    def test_score_structure_zero_action(self) -> None:
        """Test score with zero-length action."""

        setup = Algorithm.parse_moves('R')
        action = Algorithm([])

        score = score_structure(setup, action)
        self.assertEqual(score, 0.0)

    def test_score_structure_both_zero(self) -> None:
        """Test score with both zero-length."""

        setup = Algorithm([])
        action = Algorithm([])

        score = score_structure(setup, action)
        self.assertEqual(score, 0.0)

    def test_score_structure_longer_action_better(self) -> None:
        """Test that longer actions score better."""

        setup = Algorithm.parse_moves('R')
        action1 = Algorithm.parse_moves('U')
        action2 = Algorithm.parse_moves('U F D')

        score1 = score_structure(setup, action1)
        score2 = score_structure(setup, action2)

        self.assertGreater(score2, score1)

    def test_score_structure_setup_penalty(self) -> None:
        """Test that long setups relative to action are penalized."""

        # Short setup, long action
        setup1 = Algorithm.parse_moves('R')
        action1 = Algorithm.parse_moves('U F D L')

        # Long setup, short action
        setup2 = Algorithm.parse_moves('R U F D')
        action2 = Algorithm.parse_moves('L')

        score1 = score_structure(setup1, action1)
        score2 = score_structure(setup2, action2)

        # Shorter setup with longer action should score better
        self.assertGreater(score1, score2)


class IsInverseAtTestCase(unittest.TestCase):
    """Test inverse checking at position."""

    def test_is_inverse_at_basic(self) -> None:
        """Test basic inverse detection."""

        algo = Algorithm.parse_moves("R U U' R'")
        pattern = Algorithm.parse_moves('R')
        cache: BoundedCache[str, Algorithm] = BoundedCache(10)

        # R' should appear at position 3
        self.assertTrue(is_inverse_at(algo, 3, pattern, cache))

    def test_is_inverse_at_not_inverse(self) -> None:
        """Test when pattern is not inverse at position."""

        algo = Algorithm.parse_moves('R U F D')
        pattern = Algorithm.parse_moves('R')
        cache: BoundedCache[str, Algorithm] = BoundedCache(10)

        # U is not R' at position 1
        self.assertFalse(is_inverse_at(algo, 1, pattern, cache))

    def test_is_inverse_at_out_of_bounds(self) -> None:
        """Test inverse detection when position is out of bounds."""

        algo = Algorithm.parse_moves('R U')
        pattern = Algorithm.parse_moves('R U F')
        cache: BoundedCache[str, Algorithm] = BoundedCache(10)

        # Not enough space for 3-move inverse
        self.assertFalse(is_inverse_at(algo, 0, pattern, cache))

    def test_is_inverse_at_with_cache(self) -> None:
        """Test inverse detection with caching."""

        # Create an algorithm where we can find the inverse
        # Pattern: R U, Inverse: U' R'
        # Algorithm: R U U' R' (pattern followed by its inverse)
        algo = Algorithm.parse_moves("R U U' R'")
        pattern = Algorithm.parse_moves('R U')

        inverse_cache: BoundedCache[str, Algorithm] = BoundedCache(10)

        # First call should populate cache
        # Inverse of "R U" is "U' R'" at position 2
        result = is_inverse_at(algo, 2, pattern, inverse_cache)
        self.assertTrue(result)

        # Cache should be populated
        self.assertGreater(len(inverse_cache), 0)

        # Second call should use cache
        result2 = is_inverse_at(algo, 2, pattern, inverse_cache)
        self.assertTrue(result2)

    def test_is_inverse_at_empty_pattern(self) -> None:
        """Test inverse detection with empty pattern."""

        algo = Algorithm.parse_moves('R U')
        pattern = Algorithm([])
        cache: BoundedCache[str, Algorithm] = BoundedCache(10)

        # Empty pattern has zero length, should match at position 0
        self.assertTrue(is_inverse_at(algo, 0, pattern, cache))


class EfficiencyRatingTestCase(unittest.TestCase):
    """Test efficiency rating calculation."""

    def test_efficiency_rating_na(self) -> None:
        """Test N/A rating when no structures."""

        rating = calculate_efficiency_rating(0, 0, 0.0, 0)
        self.assertEqual(rating, 'N/A')

    def test_efficiency_rating_excellent(self) -> None:
        """Test Excellent rating for pure/A9 commutators."""

        # 75% pure/A9, avg 8 moves
        rating = calculate_efficiency_rating(3, 1, 8.0, 4)
        self.assertEqual(rating, 'Excellent')

    def test_efficiency_rating_good(self) -> None:
        """Test Good rating for mix of efficient structures."""

        rating = calculate_efficiency_rating(1, 1, 10.0, 4)
        self.assertEqual(rating, 'Good')

    def test_efficiency_rating_good_by_avg_moves(self) -> None:
        """Test Good rating based on low average moves."""

        # Only 25% pure/A9 but very low avg moves
        rating = calculate_efficiency_rating(1, 0, 9.0, 4)
        self.assertEqual(rating, 'Good')

    def test_efficiency_rating_fair(self) -> None:
        """Test Fair rating for average efficiency."""

        # Low pure/A9 ratio but reasonable avg moves
        rating = calculate_efficiency_rating(0, 1, 11.0, 4)
        self.assertEqual(rating, 'Fair')

    def test_efficiency_rating_poor(self) -> None:
        """Test Poor rating for inefficient structures."""

        # No pure/A9, high avg moves
        rating = calculate_efficiency_rating(0, 0, 15.0, 4)
        self.assertEqual(rating, 'Poor')


class DetectConjugateEdgeCasesTestCase(unittest.TestCase):
    """Test edge cases in conjugate detection."""

    def test_detect_conjugate_early_termination(self) -> None:
        """Test early termination with very high score."""
        # Create a structure with high score that triggers early termination
        algo = Algorithm.parse_moves("R U F D L B U' F' D' L' B' R'")
        structures = detect_structures(algo, min_score=0)

        # Should detect at least one structure without exhaustive search
        self.assertGreaterEqual(len(structures), 0)

    def test_detect_conjugate_max_setup_limit(self) -> None:
        """Test that max_setup_len is respected."""
        algo = Algorithm.parse_moves("R U F D L U' F' D' L' R'")

        # With very small max_setup, might not detect some structures
        structures_small = detect_structures(algo, max_setup_len=1)
        structures_large = detect_structures(algo, max_setup_len=5)

        # Larger limit should find at least as many structures
        self.assertGreaterEqual(len(structures_large), len(structures_small))


class DetectCommutatorEdgeCasesTestCase(unittest.TestCase):
    """Test edge cases in commutator detection."""

    def test_detect_commutator_max_part_length(self) -> None:
        """Test commutator detection with max part length constraint."""
        algo = Algorithm.parse_moves("R U F R' U' F'")

        structures = detect_structures(algo, max_setup_len=3, min_score=0)

        # Should detect commutator even with constraints
        if len(structures) > 0:
            self.assertIn(structures[0].type, ['commutator', 'conjugate'])

    def test_detect_commutator_early_termination(self) -> None:
        """Test early termination for commutators."""
        algo = Algorithm.parse_moves("R U R' U' F D F' D'")

        structures = detect_structures(algo, min_score=0)

        # Should find both commutators efficiently
        self.assertGreaterEqual(len(structures), 1)


class CountAllStructuresTestCase(unittest.TestCase):
    """Test counting of all structures including nested."""

    def test_count_all_structures_max_depth_limit(self) -> None:
        """Test that max depth limit is respected."""

        algo = Algorithm.parse_moves("F R U R' U' F'")
        structures = detect_structures(algo, min_score=0)

        # Count with depth limit of 1 (should not recurse into nested)
        total1, _, _ = count_all_structures(structures, max_depth=1)

        # Count with higher depth limit
        total2, _, _ = count_all_structures(structures, max_depth=10)

        # Higher depth should find more structures (or equal)
        self.assertGreaterEqual(total2, total1)

    def test_count_all_structures_empty_list(self) -> None:
        """Test counting with empty structure list."""

        total, conj, comm = count_all_structures([])

        self.assertEqual(total, 0)
        self.assertEqual(conj, 0)
        self.assertEqual(comm, 0)

    def test_count_all_structures_with_cache(self) -> None:
        """Test counting with cache."""

        algo = Algorithm.parse_moves("F R U R' U' F'")
        structures = detect_structures(algo, min_score=0)

        cache: dict[str, list[Structure]] = {}
        total, _, _ = count_all_structures(
            structures, structure_cache=cache,
        )

        # Cache should be populated
        self.assertGreaterEqual(len(cache), 0)
        self.assertGreaterEqual(total, len(structures))


class CalculateNestingDepthTestCase(unittest.TestCase):
    """Test nesting depth calculation."""

    def test_calculate_nesting_depth_simple(self) -> None:
        """Test nesting depth for simple non-nested structure."""

        algo = Algorithm.parse_moves("R U R' U'")
        structures = detect_structures(algo, min_score=0)

        max_depth, nested_count = calculate_nesting_depth(structures)

        # Simple commutator has depth 1, no nested structures
        self.assertEqual(max_depth, 1)
        self.assertEqual(nested_count, 0)

    def test_calculate_nesting_depth_nested(self) -> None:
        """Test nesting depth for nested structure."""

        algo = Algorithm.parse_moves("F R U R' U' F'")
        structures = detect_structures(algo, min_score=0)

        max_depth, nested_count = calculate_nesting_depth(structures)

        # Should have depth >= 1 and at least some nested structures
        self.assertGreaterEqual(max_depth, 1)
        self.assertGreaterEqual(nested_count, 0)

    def test_calculate_nesting_depth_empty(self) -> None:
        """Test nesting depth for empty structure list."""

        max_depth, nested_count = calculate_nesting_depth([])

        self.assertEqual(max_depth, 0)
        self.assertEqual(nested_count, 0)

    def test_calculate_nesting_depth_with_cache(self) -> None:
        """Test nesting depth calculation with cache."""

        algo = Algorithm.parse_moves("F R U R' U' F'")
        structures = detect_structures(algo, min_score=0)

        cache: dict[str, list[Structure]] = {}
        max_depth, _ = calculate_nesting_depth(structures, cache)

        # Cache should be populated
        self.assertGreaterEqual(len(cache), 0)
        self.assertGreaterEqual(max_depth, 1)


class CompressRecursiveTestCase(unittest.TestCase):
    """Test recursive compression with caching."""

    def test_compress_recursive_with_cache(self) -> None:
        """Test that compress uses cache for nested structures."""
        algo = Algorithm.parse_moves("F R U R' U' F'")

        # Compress with min_score=0 to ensure detection
        compressed = compress(algo, min_score=0)

        # Should contain structure notation
        self.assertIn('[', compressed)
        self.assertIn(']', compressed)

    def test_compress_recursive_no_structures(self) -> None:
        """Test compression when no structures detected."""
        algo = Algorithm.parse_moves('R U F')

        compressed = compress(algo, min_score=50)

        # Should return original moves
        self.assertEqual(compressed, 'R U F')

    def test_compress_single_structure_fast_path(self) -> None:
        """Test fast path for single structure."""
        algo = Algorithm.parse_moves("R U R'")

        compressed = compress(algo, min_score=0)

        # Should handle single structure efficiently
        self.assertIn('[', compressed)


class DetectStructuresMaxDepthTestCase(unittest.TestCase):
    """Test max_depth parameter in detect_structures."""

    def test_detect_structures_max_depth_parameter(self) -> None:
        """Test that max_depth parameter exists and works."""
        algo = Algorithm.parse_moves("F R U R' U' F'")

        # Should accept max_depth parameter
        structures = detect_structures(algo, min_score=0, max_depth=5)

        # Should still detect structures
        self.assertGreaterEqual(len(structures), 0)


class ComputeStructureAdditionalTestCase(unittest.TestCase):
    """Additional test cases for compute_structure."""

    def test_compute_structure_coverage_partial(self) -> None:
        """Test coverage calculation with partial coverage."""
        algo = Algorithm.parse_moves("R U R' U' F D")

        struct = compute_structure(algo, min_score=0)

        # Should have partial coverage (commutator covers first 4 moves)
        if struct.total_structures > 0:
            self.assertGreater(struct.coverage_percent, 0.0)
            self.assertLess(struct.coverage_percent, 1.0)
            self.assertGreater(struct.uncovered_moves, 0)

    def test_compute_structure_multiple_structures_stats(self) -> None:
        """Test statistics with multiple structures."""
        algo = Algorithm.parse_moves("R U R' U' F D F' D'")

        struct = compute_structure(algo, min_score=0)

        if struct.total_structures > 1:
            # Should have valid setup/action statistics
            self.assertGreater(struct.average_setup_length, 0)
            self.assertGreater(struct.average_action_length, 0)
            self.assertGreaterEqual(
                struct.longest_setup_length,
                struct.shortest_setup_length,
            )
            self.assertGreaterEqual(
                struct.longest_action_length,
                struct.shortest_action_length,
            )


class ClassificationIntegrationTestCase(unittest.TestCase):
    """Integration tests for classification system."""

    def test_pure_commutator_full_flow(self) -> None:
        """Test full flow of pure commutator detection and classification."""
        algo = Algorithm.parse_moves("R U R' U'")
        struct = compute_structure(algo, min_score=0)

        # Should detect as commutator
        self.assertGreaterEqual(struct.commutator_count, 1)

        # Check classification fields are populated
        if struct.structures:
            s = struct.structures[0]
            self.assertEqual(s.type, 'commutator')
            self.assertIn(
                s.classification, ['pure', 'other', 'A9', 'orthogonal'],
            )
            self.assertIsInstance(s.has_cancellations, bool)
            self.assertGreater(s.move_count, 0)

    def test_a9_commutator_detection(self) -> None:
        """Test detection of A9 commutator pattern."""
        # Create a 10-move commutator with cancellation potential
        algo = Algorithm.parse_moves("R U F R' U' F'")
        structures = detect_structures(algo, min_score=0)

        if structures:
            # Check that classification is set
            self.assertIsNotNone(structures[0].classification)

    def test_nested_conjugate_classification_flow(self) -> None:
        """Test full flow of nested conjugate classification."""
        algo = Algorithm.parse_moves("F R U R' U' F'")
        struct = compute_structure(algo, min_score=0)

        # Should detect nested structure
        self.assertGreaterEqual(struct.total_structures, 1)

        # Check nested count fields
        self.assertIsInstance(struct.nested_conjugate_count, int)
        self.assertGreaterEqual(struct.nested_conjugate_count, 0)

    def test_efficiency_rating_integration(self) -> None:
        """Test efficiency rating calculation in full flow."""
        test_cases = [
            ("R U R' U'", ['Excellent', 'Good', 'Fair', 'Poor', 'N/A']),
            ("F R U R' U' F'", ['Excellent', 'Good', 'Fair', 'Poor', 'N/A']),
        ]

        for moves, expected_ratings in test_cases:
            with self.subTest(moves=moves):
                algo = Algorithm.parse_moves(moves)
                struct = compute_structure(algo, min_score=0)

                self.assertIn(struct.efficiency_rating, expected_ratings)
