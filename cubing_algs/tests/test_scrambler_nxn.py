"""Tests for NxNxN scramble generation."""
import time
import unittest
from collections import Counter
from random import Random
from statistics import mean
from statistics import stdev

from cubing_algs.algorithm import Algorithm
from cubing_algs.constants import FACE_ORDER
from cubing_algs.constants import OPPOSITE_FACES
from cubing_algs.scrambler.nxn import scramble
from cubing_algs.vcube import VCube


class TestScramble(unittest.TestCase):
    """Tests for scramble generation."""

    def test_scramble_3x3x3(self) -> None:
        """Test scramble 3x3x3."""
        moves = scramble(3)

        self.assertGreaterEqual(
            len(moves), 25,
        )

        self.assertLessEqual(
            len(moves), 30,
        )

    def test_scramble_3x3x3_iterations(self) -> None:
        """Test scramble 3x3x3 iterations."""
        moves = scramble(3, 5)

        self.assertEqual(
            len(moves), 5,
        )


class TestScrambleEffectivenessByLength(unittest.TestCase):
    """
    Test suite measuring scramble effectiveness across different lengths.

    Tests randomness, state space coverage, consistency, and performance
    characteristics of scrambles at various lengths.
    """

    def setUp(self) -> None:
        """Set up test fixtures."""
        self.test_lengths = [5, 10, 15, 20, 25, 30, 50]
        self.sample_size = 100  # Number of scrambles to test per length
        self.small_sample_size = 20  # For performance tests

    @staticmethod
    def get_face_from_move(move: str) -> str:
        """
        Extract the face character from a move string.

        Args:
            move: Move string to extract face from.

        Returns:
            Face character (U, R, F, D, L, B) or empty string.

        """
        for face in FACE_ORDER:
            if move.startswith((face, face.lower())):
                return face
        return ''

    @staticmethod
    def calculate_move_distribution(algorithm: Algorithm) -> dict[
            str, float]:
        """
        Calculate the distribution of face moves in an algorithm.

        Args:
            algorithm: Algorithm to analyze.

        Returns:
            Dictionary mapping face names to their percentage distribution.

        """
        face_counts: Counter[str] = Counter()
        total_moves = len(algorithm)

        for move in algorithm:
            face = TestScrambleEffectivenessByLength.get_face_from_move(
                str(move),
            )
            if face:
                face_counts[face] += 1

        # Convert to percentages
        return {
            face: (count / total_moves) * 100
            for face, count in face_counts.items()
        }

    @staticmethod
    def calculate_state_scrambledness(algorithm: Algorithm) -> float:
        """
        Calculate how scrambled a cube becomes after applying an algorithm.

        Returns a value between 0.0 (solved) and 1.0 (maximally scrambled).

        Args:
            algorithm: Algorithm to evaluate.

        Returns:
            Scrambledness score between 0.0 and 1.0.

        """
        # Count how many facelets are not in their original position
        cube = VCube()
        solved_state = cube.state
        cube.rotate(algorithm)
        scrambled_state = cube.state

        different_facelets = sum(
            1
            for i, j in zip(solved_state, scrambled_state, strict=False)
            if i != j
        )

        # Normalize by total number of facelets (54 for a 3x3x3 cube)
        return different_facelets / 54.0

    @staticmethod
    def has_consecutive_same_or_opposite_faces(algorithm: Algorithm) -> bool:
        """
        Check if algorithm has consecutive moves on same
        or opposite faces.

        Args:
            algorithm: Algorithm to check.

        Returns:
            True if consecutive same or opposite face moves found.

        """
        moves = [str(move) for move in algorithm]

        for i in range(len(moves) - 1):
            current_face = TestScrambleEffectivenessByLength.get_face_from_move(
                moves[i],
            )
            next_face = TestScrambleEffectivenessByLength.get_face_from_move(
                moves[i + 1],
            )

            if current_face and next_face:
                # Check same face
                if current_face == next_face:
                    return True
                # Check opposite faces
                if OPPOSITE_FACES.get(current_face) == next_face:
                    return True

        return False

    def test_scramble_length_consistency(self) -> None:
        """Test that scrambles generate the requested length consistently."""
        for length in self.test_lengths:
            with self.subTest(length=length):
                for _ in range(10):  # Test multiple samples
                    scramble_alg = scramble(3, length)
                    self.assertEqual(
                        len(scramble_alg), length,
                        f'Scramble should be exactly {length} moves',
                    )

    def test_move_distribution_randomness(self) -> None:
        """Test that move distributions approach uniform across face types."""
        for length in [15, 25, 50]:  # Test representative lengths
            with self.subTest(length=length):
                all_distributions = []

                for _ in range(self.sample_size):
                    scramble_alg = scramble(3, length)
                    distribution = self.calculate_move_distribution(
                        scramble_alg,
                    )
                    all_distributions.append(distribution)

                # Calculate average distribution across all scrambles
                face_averages = {}
                for face in FACE_ORDER:
                    face_percentages = [
                        d.get(face, 0) for d in all_distributions
                    ]
                    face_averages[face] = mean(face_percentages)

                # For longer scrambles, distribution should be more uniform
                if length >= 25:
                    # Each face should appear roughly 16.67% of the time (1/6)
                    expected_percentage = 100.0 / 6
                    tolerance = 5.0  # Allow 5% deviation

                    for face, avg_percentage in face_averages.items():
                        self.assertGreater(
                            avg_percentage,
                            expected_percentage - tolerance,
                            f'Face {face} appears too rarely: '
                            f'{avg_percentage:.1f}%',
                        )
                        self.assertLess(
                            avg_percentage, expected_percentage + tolerance,
                            f'Face {face} appears too frequently: '
                            f'{avg_percentage:.1f}%',
                        )

    def test_state_space_coverage_by_length(self) -> None:
        """Test that longer scrambles achieve better state space coverage."""
        scrambledness_by_length = {}

        for length in self.test_lengths:
            scrambledness_values = []

            for _ in range(self.sample_size):
                scramble_alg = scramble(3, length)
                scrambledness = self.calculate_state_scrambledness(scramble_alg)
                scrambledness_values.append(scrambledness)

            avg_scrambledness = mean(scrambledness_values)
            scrambledness_by_length[length] = avg_scrambledness

        # Test that scrambledness generally increases with length
        lengths = sorted(scrambledness_by_length.keys())
        for i in range(len(lengths) - 1):
            current_length = lengths[i]
            next_length = lengths[i + 1]

            current_scrambledness = scrambledness_by_length[current_length]
            next_scrambledness = scrambledness_by_length[next_length]

            # Allow some variance, but general trend should be increasing
            self.assertGreaterEqual(
                next_scrambledness,
                current_scrambledness - 0.05,
                f'Scrambledness should increase with length: '
                f'{current_length}({current_scrambledness:.3f}) vs '
                f'{next_length}({next_scrambledness:.3f})',
            )

    def test_no_consecutive_invalid_moves(self) -> None:
        """Test that scrambles never contain consecutive invalid moves."""
        for length in self.test_lengths:
            with self.subTest(length=length):
                for _ in range(self.sample_size):
                    scramble_alg = scramble(3, length)
                    self.assertFalse(
                        self.has_consecutive_same_or_opposite_faces(scramble_alg),
                        f'Scramble of length {length} contains '
                        'consecutive invalid moves',
                    )

    def test_scramble_uniqueness(self) -> None:
        """Test that repeated scramble calls produce different results."""
        for length in [15, 25]:
            with self.subTest(length=length):
                scrambles = set()

                for _ in range(50):  # Generate 50 scrambles
                    scramble_alg = scramble(3, length)
                    scrambles.add(str(scramble_alg))

                # Should have high uniqueness (at least 90% unique)
                uniqueness_ratio = len(scrambles) / 50
                self.assertGreater(
                    uniqueness_ratio, 0.9,
                    f'Scrambles of length {length} not unique enough: '
                    f'{uniqueness_ratio:.2f}',
                )

    def test_very_short_scrambles(self) -> None:
        """Test edge cases with very short scrambles (1-5 moves)."""
        for length in range(1, 6):
            with self.subTest(length=length):
                scramble_alg = scramble(3, length)

                # Should generate exactly the requested length
                self.assertEqual(len(scramble_alg), length)

                # Should not have invalid consecutive moves
                self.assertFalse(
                    self.has_consecutive_same_or_opposite_faces(scramble_alg),
                )

                # Should produce some scrambling effect
                if length >= 3:
                    scrambledness = self.calculate_state_scrambledness(
                        scramble_alg,
                    )
                    self.assertGreater(
                        scrambledness, 0.0,
                        'Even short scrambles should change cube state',
                    )

    def test_very_long_scrambles(self) -> None:
        """Test edge cases with very long scrambles (50+ moves)."""
        rng = Random(42)  # noqa: S311
        long_lengths = [50, 75, 100]

        for length in long_lengths:
            with self.subTest(length=length):
                scramble_alg = scramble(3, length, rng=rng)

                # Should generate exactly the requested length
                self.assertEqual(len(scramble_alg), length)

                # Should not have invalid consecutive moves
                self.assertFalse(
                    self.has_consecutive_same_or_opposite_faces(scramble_alg),
                )

                # Should achieve high scrambledness
                scrambledness = self.calculate_state_scrambledness(scramble_alg)
                self.assertGreater(
                    scrambledness, 0.6,
                    'Long scrambles should achieve '
                    f'high scrambledness: {scrambledness:.3f}',
                )

    def test_scramble_performance_by_length(self) -> None:
        """Test performance characteristics of scramble generation."""
        performance_results = {}

        for length in [10, 25, 50, 100]:
            start_time = time.time()

            for _ in range(self.small_sample_size):
                scramble(3, length)

            end_time = time.time()
            avg_time_per_scramble = (
                (end_time - start_time) / self.small_sample_size
            )
            performance_results[length] = avg_time_per_scramble

        # Performance should scale reasonably with length
        for length, avg_time in performance_results.items():
            # Should generate scrambles quickly (under 10ms each)
            self.assertLess(
                avg_time, 0.01,
                'Scramble generation too slow '
                f'for length {length}: {avg_time:.4f}s',
            )

    def test_scramble_consistency_across_runs(self) -> None:
        """
        Test that scramble quality metrics are consistent
        across multiple runs.
        """
        length = 25  # Test with a representative length

        run_scrambledness = []
        run_uniqueness = []

        # Run multiple test batches
        for _ in range(5):
            batch_scrambledness = []
            batch_scrambles = set()

            for _ in range(20):
                scramble_alg = scramble(3, length)
                batch_scrambledness.append(
                    self.calculate_state_scrambledness(scramble_alg),
                )
                batch_scrambles.add(str(scramble_alg))

            run_scrambledness.append(mean(batch_scrambledness))
            run_uniqueness.append(len(batch_scrambles) / 20)

        # Consistency check: standard deviation should be reasonably low
        scrambledness_stdev = stdev(run_scrambledness)
        uniqueness_stdev = stdev(run_uniqueness)

        self.assertLess(
            scrambledness_stdev, 0.05,
            'Scrambledness too inconsistent across runs: '
            f'{scrambledness_stdev:.4f}')
        self.assertLess(
            uniqueness_stdev, 0.1,
            'Uniqueness too inconsistent across runs: '
            f'{uniqueness_stdev:.4f}')

    def test_move_type_distribution(self) -> None:
        """
        Test that different move types (normal, prime, double)
        are well distributed.
        """
        length = 30

        move_type_counts = {'normal': 0, 'prime': 0, 'double': 0}
        total_moves = 0

        for _ in range(self.sample_size):
            scramble_alg = scramble(3, length)

            for move in scramble_alg:
                total_moves += 1

                if move.is_counter_clockwise:
                    move_type_counts['prime'] += 1
                elif move.is_double:
                    move_type_counts['double'] += 1
                else:
                    move_type_counts['normal'] += 1

        # Convert to percentages
        move_type_percentages = {}
        for move_type, count in move_type_counts.items():
            move_type_percentages[move_type] = (count / total_moves) * 100

        # Each move type should appear roughly equally (around 33% each)
        expected_percentage = 100.0 / 3
        tolerance = 8.0  # Allow 8% deviation

        for move_type, percentage in move_type_percentages.items():
            self.assertGreater(
                percentage, expected_percentage - tolerance,
                f'Move type {move_type} appears too rarely: {percentage:.1f}%',
            )
            self.assertLess(
                percentage, expected_percentage + tolerance,
                f'Move type {move_type} appears '
                f'too frequently: {percentage:.1f}%',
            )


class TestRNGParameter(unittest.TestCase):
    """Tests for random number generator parameter functionality."""

    def test_scramble_deterministic_with_seed(self) -> None:
        """Test that scramble produces identical results with same seed."""
        rng1 = Random(42)  # noqa: S311
        rng2 = Random(42)  # noqa: S311

        result1 = scramble(3, 15, rng=rng1)
        result2 = scramble(3, 15, rng=rng2)

        self.assertEqual(
            str(result1),
            str(result2),
            'Same seed should produce identical scrambles',
        )
        self.assertEqual(
            len(result1),
            15,
            'Scramble should have correct length',
        )

    def test_scramble_different_seeds_produce_different_results(self) -> None:
        """Test scramble produces different results with different seeds."""
        rng1 = Random(42)  # noqa: S311
        rng2 = Random(999)  # noqa: S311

        result1 = scramble(3, 15, rng=rng1)
        result2 = scramble(3, 15, rng=rng2)

        self.assertNotEqual(
            str(result1),
            str(result2),
            'Different seeds should produce different scrambles',
        )

    def test_scramble_uses_default_rng_when_none(self) -> None:
        """Test that scramble works without explicit rng parameter."""
        result = scramble(3, 10)

        self.assertEqual(
            len(result),
            10,
            'Should generate correct scramble with default RNG',
        )

    def test_scramble_with_options_and_seeded_rng(self) -> None:
        """Test scramble with options using seeded RNG."""
        rng1 = Random(42)  # noqa: S311
        rng2 = Random(42)  # noqa: S311

        result1 = scramble(
            5,
            12,
            inner_layers=True,
            right_handed=False,
            rng=rng1,
        )
        result2 = scramble(
            5,
            12,
            inner_layers=True,
            right_handed=False,
            rng=rng2,
        )

        self.assertEqual(
            str(result1),
            str(result2),
            'Same seed with options should produce identical results',
        )
        self.assertEqual(
            len(result1),
            12,
            'Scramble should have correct length',
        )

    def test_scramble_automatic_iterations_with_seeded_rng(self) -> None:
        """Test scramble with automatic iterations using seeded RNG."""
        rng1 = Random(42)  # noqa: S311
        rng2 = Random(42)  # noqa: S311

        result1 = scramble(3, 0, rng=rng1)
        result2 = scramble(3, 0, rng=rng2)

        self.assertEqual(
            len(result1),
            len(result2),
            'Same seed should produce same length with automatic iterations',
        )
        self.assertEqual(
            str(result1),
            str(result2),
            'Same seed should produce identical scrambles',
        )

    def test_rng_state_advances_with_multiple_calls(self) -> None:
        """Test RNG state advances correctly with multiple sequential calls."""
        rng = Random(42)  # noqa: S311

        result1 = scramble(3, 5, rng=rng)
        result2 = scramble(3, 5, rng=rng)
        result3 = scramble(3, 5, rng=rng)

        self.assertNotEqual(
            str(result1),
            str(result2),
            'Sequential calls should produce different results',
        )
        self.assertNotEqual(
            str(result2),
            str(result3),
            'Sequential calls should produce different results',
        )
        self.assertNotEqual(
            str(result1),
            str(result3),
            'Sequential calls should produce different results',
        )

    def test_resetting_rng_seed_resets_sequence(self) -> None:
        """Test that resetting RNG seed produces the same sequence again."""
        seed = 42

        rng1 = Random(seed)  # noqa: S311
        result1_first = scramble(3, 10, rng=rng1)
        result1_second = scramble(3, 10, rng=rng1)

        rng2 = Random(seed)  # noqa: S311
        result2_first = scramble(3, 10, rng=rng2)

        self.assertEqual(
            str(result1_first),
            str(result2_first),
            'Resetting seed should restart sequence',
        )
        self.assertNotEqual(
            str(result1_first),
            str(result1_second),
            'Continued sequence should differ from start',
        )

    def test_rng_parameter_edge_case_very_short_scramble(self) -> None:
        """Test RNG parameter with very short scrambles."""
        rng1 = Random(42)  # noqa: S311
        rng2 = Random(42)  # noqa: S311

        result1 = scramble(3, 1, rng=rng1)
        result2 = scramble(3, 1, rng=rng2)

        self.assertEqual(
            str(result1),
            str(result2),
            'Same seed should produce identical single-move scrambles',
        )
        self.assertEqual(
            len(result1),
            1,
            'Should generate exactly 1 move',
        )

    def test_rng_parameter_edge_case_very_long_scramble(self) -> None:
        """Test RNG parameter with very long scrambles."""
        rng1 = Random(42)  # noqa: S311
        rng2 = Random(42)  # noqa: S311

        iterations = 100
        result1 = scramble(3, iterations, rng=rng1)
        result2 = scramble(3, iterations, rng=rng2)

        self.assertEqual(
            str(result1),
            str(result2),
            'Same seed should produce identical long scrambles',
        )
        self.assertEqual(
            len(result1),
            iterations,
            'Should generate correct number of moves',
        )

    def test_rng_parameter_with_different_cube_sizes(self) -> None:
        """Test RNG parameter consistency across different cube sizes."""
        seed = 42

        for cube_size in [2, 3, 4, 5, 6]:
            with self.subTest(cube_size=cube_size):
                rng1 = Random(seed)  # noqa: S311
                rng2 = Random(seed)  # noqa: S311

                result1 = scramble(cube_size, 10, rng=rng1)
                result2 = scramble(cube_size, 10, rng=rng2)

                self.assertEqual(
                    str(result1),
                    str(result2),
                    f'Same seed should produce identical '
                    f'scrambles for {cube_size}x{cube_size}x{cube_size}',
                )

    def test_default_rng_produces_different_results_each_call(self) -> None:
        """Test that default RNG produces different results on each call."""
        results = []

        for _ in range(5):
            result = scramble(3, 10)
            results.append(str(result))

        unique_results = set(results)
        self.assertGreater(
            len(unique_results),
            1,
            'Default RNG should produce different results across calls',
        )
