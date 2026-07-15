"""Tests for memorability analysis."""
import unittest
from typing import ClassVar
from unittest.mock import patch

from cubing_algs.algorithm import Algorithm
from cubing_algs.memory import MemoryData
from cubing_algs.memory import compute_chunk_score
from cubing_algs.memory import compute_face_familiarity_score
from cubing_algs.memory import compute_flow_memory_score
from cubing_algs.memory import compute_length_score
from cubing_algs.memory import compute_memory
from cubing_algs.memory import compute_move_familiarity_score
from cubing_algs.memory import compute_repetition_score
from cubing_algs.memory import compute_structure_score
from cubing_algs.memory import compute_unfamiliar_percent
from cubing_algs.memory import find_repeated_subsequences
from cubing_algs.memory import get_memory_rating
from cubing_algs.transform.timing import time_moves


class LengthScoreTestCase(unittest.TestCase):
    """Tests for compute_length_score."""

    def test_zero_moves(self) -> None:
        """Zero moves should give very high score."""
        score = compute_length_score(0)
        self.assertGreater(score, 0.95)

    def test_short_algorithm(self) -> None:
        """Short algorithm (4 HTM) → ~0.9."""
        score = compute_length_score(4)
        self.assertGreater(score, 0.8)
        self.assertLess(score, 0.97)

    def test_medium_algorithm(self) -> None:
        """Medium algorithm (12 HTM) → ~0.5."""
        score = compute_length_score(12)
        self.assertAlmostEqual(score, 0.5, delta=0.01)

    def test_long_algorithm(self) -> None:
        """Long algorithm (20 HTM) → ~0.1."""
        score = compute_length_score(20)
        self.assertLess(score, 0.15)

    def test_very_long_algorithm(self) -> None:
        """Very long algorithm → approaches 0."""
        score = compute_length_score(30)
        self.assertLess(score, 0.05)
        self.assertGreaterEqual(score, 0.0)

    def test_monotonically_decreasing(self) -> None:
        """Score should decrease with move count."""
        scores = [compute_length_score(i) for i in range(25)]
        for i in range(1, len(scores)):
            self.assertLess(scores[i], scores[i - 1])


class ChunkScoreTestCase(unittest.TestCase):
    """Tests for compute_chunk_score."""

    def test_single_chunk(self) -> None:
        """Single chunk should be easy."""
        score = compute_chunk_score(1, 1)
        self.assertGreater(score, 0.8)

    def test_miller_easy(self) -> None:
        """5 chunks should be moderate."""
        score = compute_chunk_score(5, 1)
        self.assertAlmostEqual(score, 0.6, delta=0.05)

    def test_miller_hard(self) -> None:
        """9 chunks should be hard."""
        score = compute_chunk_score(9, 1)
        self.assertAlmostEqual(score, 0.2, delta=0.05)

    def test_beyond_miller(self) -> None:
        """Beyond 9 chunks → very hard."""
        score = compute_chunk_score(12, 1)
        self.assertLess(score, 0.15)

    def test_variety_penalty(self) -> None:
        """More distinct triggers should decrease score."""
        score_1 = compute_chunk_score(5, 1)
        score_3 = compute_chunk_score(5, 3)
        self.assertLess(score_3, score_1)

    def test_floored_at_0(self) -> None:
        """Score should not go below 0."""
        score = compute_chunk_score(20, 5)
        self.assertGreaterEqual(score, 0.0)

    def test_negative_chunks_capped_at_1(self) -> None:
        """Defensive: a negative chunk count must not break the 0-1 range."""
        score = compute_chunk_score(-2, 1)
        self.assertLessEqual(score, 1.0)


class StructureScoreTestCase(unittest.TestCase):
    """Tests for compute_structure_score."""

    def test_no_structure(self) -> None:
        """No structure → score 0."""
        score = compute_structure_score(0.0, 0.0, has_structure=False)
        self.assertEqual(score, 0.0)

    def test_full_coverage(self) -> None:
        """Full coverage + high compression → maximum score."""
        score = compute_structure_score(1.0, 1.0, has_structure=True)
        self.assertEqual(score, 1.0)

    def test_partial_coverage(self) -> None:
        """Partial coverage → moderate score."""
        score = compute_structure_score(0.5, 0.3, has_structure=True)
        self.assertGreater(score, 0.2)
        self.assertLess(score, 0.8)

    def test_zero_coverage_with_structure(self) -> None:
        """Zero coverage with structure → score 0."""
        score = compute_structure_score(0.0, 0.0, has_structure=True)
        self.assertEqual(score, 0.0)


class RepetitionScoreTestCase(unittest.TestCase):
    """Tests for find_repeated_subsequences and compute_repetition_score."""

    def test_no_repeats(self) -> None:
        """No repeated subsequences."""
        repeats = find_repeated_subsequences(['R', 'U', 'F', 'L'])
        self.assertEqual(repeats, 0)

    def test_simple_repeat(self) -> None:
        """Detect simple 2-move repeat."""
        moves = ['R', 'U', "R'", "U'", 'R', 'U', "R'", "U'"]
        repeats = find_repeated_subsequences(moves)
        self.assertGreater(repeats, 0)

    def test_too_short(self) -> None:
        """Too few moves for any repeat."""
        repeats = find_repeated_subsequences(['R', 'U'])
        self.assertEqual(repeats, 0)

    def test_repetition_score_no_repeats(self) -> None:
        """No repeats → score 0 (no help from repetition)."""
        score = compute_repetition_score(0, 10)
        self.assertEqual(score, 0.0)

    def test_repetition_score_many_repeats(self) -> None:
        """Many repeats → higher score (easier)."""
        score = compute_repetition_score(10, 10)
        self.assertGreater(score, 0.6)

    def test_repetition_score_capped(self) -> None:
        """Repeats alone cannot push the score beyond the cap."""
        score = compute_repetition_score(100, 10)
        self.assertEqual(score, 0.7)

    def test_repetition_score_zero_stm(self) -> None:
        """Zero STM → nothing to repeat → score 1."""
        score = compute_repetition_score(0, 0)
        self.assertEqual(score, 1.0)


class FaceFamiliarityScoreTestCase(unittest.TestCase):
    """Tests for compute_face_familiarity_score."""

    def test_ru_only(self) -> None:
        """R and U only → high score."""
        algo = Algorithm.parse_moves("R U R' U'")
        moves = [m for m in algo if not m.is_pause]
        score = compute_face_familiarity_score(moves)
        self.assertGreater(score, 0.75)

    def test_all_faces(self) -> None:
        """All 6 faces → minimum score."""
        algo = Algorithm.parse_moves('R U F L D B')
        moves = [m for m in algo if not m.is_pause]
        score = compute_face_familiarity_score(moves)
        self.assertEqual(score, 0.0)

    def test_empty(self) -> None:
        """No face moves → score 1."""
        score = compute_face_familiarity_score([])
        self.assertEqual(score, 1.0)

    def test_fully_familiar_faces_cost_nothing(self) -> None:
        """Faces with familiarity 1.0 add no unfamiliarity cost."""
        weights = {'R': 1.0, 'U': 1.0, 'F': 1.0, 'L': 0.5, 'D': 0.5, 'B': 0.5}
        algo = Algorithm.parse_moves('R U F')
        moves = [m for m in algo if not m.is_pause]
        with patch('cubing_algs.memory.FACE_FAMILIARITY', weights):
            score = compute_face_familiarity_score(moves)
        # Only the face count cost applies (1 - 3/6 * 0.6 = 0.7)
        self.assertAlmostEqual(score, 0.7, delta=0.01)

    def test_unfamiliar_faces_penalized(self) -> None:
        """B and D moves should score lower than R and U."""
        algo_ru = Algorithm.parse_moves("R U R' U'")
        algo_bd = Algorithm.parse_moves("B D B' D'")
        moves_ru = [m for m in algo_ru if not m.is_pause]
        moves_bd = [m for m in algo_bd if not m.is_pause]
        score_ru = compute_face_familiarity_score(moves_ru)
        score_bd = compute_face_familiarity_score(moves_bd)
        self.assertLess(score_bd, score_ru)


class FlowMemoryScoreTestCase(unittest.TestCase):
    """Tests for compute_flow_memory_score."""

    def test_zero_stm(self) -> None:
        """Zero STM → nothing to interrupt → score 1."""
        score = compute_flow_memory_score(0, 0)
        self.assertEqual(score, 1.0)

    def test_no_interruptions(self) -> None:
        """No interruptions → score 1."""
        score = compute_flow_memory_score(0, 10)
        self.assertEqual(score, 1.0)

    def test_many_interruptions(self) -> None:
        """Many interruptions → low score."""
        score = compute_flow_memory_score(10, 10)
        self.assertLess(score, 0.5)

    def test_floored_at_0(self) -> None:
        """Score should not go below 0."""
        score = compute_flow_memory_score(100, 10)
        self.assertEqual(score, 0.0)


class MoveFamiliarityScoreTestCase(unittest.TestCase):
    """Tests for compute_move_familiarity_score."""

    def test_all_familiar(self) -> None:
        """All R/U moves → score 1."""
        algo = Algorithm.parse_moves("R U R' U'")
        moves = [m for m in algo if not m.is_pause]
        score = compute_move_familiarity_score(moves)
        self.assertEqual(score, 1.0)

    def test_all_unfamiliar(self) -> None:
        """All B/D moves → score 0."""
        algo = Algorithm.parse_moves("B D B' D'")
        moves = [m for m in algo if not m.is_pause]
        score = compute_move_familiarity_score(moves)
        self.assertEqual(score, 0.0)

    def test_mixed(self) -> None:
        """Mix of familiar and unfamiliar → between 0 and 1."""
        algo = Algorithm.parse_moves('R U B D')
        moves = [m for m in algo if not m.is_pause]
        score = compute_move_familiarity_score(moves)
        self.assertGreater(score, 0.0)
        self.assertLess(score, 1.0)

    def test_empty(self) -> None:
        """No moves → score 1."""
        score = compute_move_familiarity_score([])
        self.assertEqual(score, 1.0)

    def test_rotations_unfamiliar(self) -> None:
        """Rotation moves count as unfamiliar."""
        algo = Algorithm.parse_moves('x y z')
        moves = [m for m in algo if not m.is_pause]
        score = compute_move_familiarity_score(moves)
        self.assertEqual(score, 0.0)

    def test_slice_moves_unfamiliar(self) -> None:
        """Slice moves count as unfamiliar."""
        algo = Algorithm.parse_moves('M E S')
        moves = [m for m in algo if not m.is_pause]
        score = compute_move_familiarity_score(moves)
        self.assertEqual(score, 0.0)

    def test_unfamiliar_percent_empty(self) -> None:
        """No moves → 0% unfamiliar."""
        self.assertEqual(compute_unfamiliar_percent([]), 0.0)

    def test_unfamiliar_percent_mixed(self) -> None:
        """Half unfamiliar moves → 50%."""
        algo = Algorithm.parse_moves('R U B D')
        moves = [m for m in algo if not m.is_pause]
        self.assertEqual(compute_unfamiliar_percent(moves), 0.5)


class MemoryRatingTestCase(unittest.TestCase):
    """Tests for get_memory_rating."""

    def test_trivial(self) -> None:
        """Score 0.8-1.0 → Trivial."""
        self.assertEqual(get_memory_rating(1.0), 'Trivial')
        self.assertEqual(get_memory_rating(0.9), 'Trivial')
        self.assertEqual(get_memory_rating(0.8), 'Trivial')

    def test_easy(self) -> None:
        """Score 0.6-0.8 → Easy."""
        self.assertEqual(get_memory_rating(0.799), 'Easy')
        self.assertEqual(get_memory_rating(0.6), 'Easy')

    def test_moderate(self) -> None:
        """Score 0.4-0.6 → Moderate."""
        self.assertEqual(get_memory_rating(0.599), 'Moderate')
        self.assertEqual(get_memory_rating(0.4), 'Moderate')

    def test_hard(self) -> None:
        """Score 0.2-0.4 → Hard."""
        self.assertEqual(get_memory_rating(0.399), 'Hard')
        self.assertEqual(get_memory_rating(0.2), 'Hard')

    def test_very_hard(self) -> None:
        """Score 0-0.2 → Very Hard."""
        self.assertEqual(get_memory_rating(0.199), 'Very Hard')
        self.assertEqual(get_memory_rating(0.0), 'Very Hard')

    def test_negative_score(self) -> None:
        """Negative score → Very Hard (fallback)."""
        self.assertEqual(get_memory_rating(-1.0), 'Very Hard')


# --- Integration Tests ---


class ComputeMemoryIntegrationTestCase(unittest.TestCase):
    """Integration tests for compute_memory with real algorithms."""

    def test_sexy_move(self) -> None:
        """R U R' U' → Trivial (1 trigger, RU only)."""
        algo = Algorithm.parse_moves("R U R' U'")
        mem = algo.memory
        self.assertIsInstance(mem, MemoryData)
        self.assertGreater(mem.memory_score, 0.75)
        self.assertIn(mem.memory_rating, ('Trivial', 'Easy'))

    def test_sune(self) -> None:
        """Sune → Easy."""
        algo = Algorithm.parse_moves("R U R' U R U2 R'")
        mem = algo.memory
        self.assertGreater(mem.memory_score, 0.55)
        self.assertIn(mem.memory_rating, ('Trivial', 'Easy'))

    def test_timing_does_not_change_memory_analysis(self) -> None:
        """
        Test that timing an algorithm leaves every metric untouched.

        Algorithms carrying repetitions are the discriminating ones:
        repetition counting compares move strings, and a timestamp makes
        every move string unique.
        """
        for moves in [
            "R U R' U' R' F R F'",
            'M2 U M2 U2 M2 U M2',
            "R U R' U' R' F R2 U' R' U' R U R' F'",
            "R U R' U R U2 R'",
        ]:
            with self.subTest(moves=moves):
                algo = Algorithm.parse_moves(moves)
                timed = algo.transform(time_moves(150))

                self.assertEqual(compute_memory(timed), compute_memory(algo))

    def test_timed_moves_keep_their_repetitions(self) -> None:
        """Test that repeated patterns are still found on timed moves."""
        algo = Algorithm.parse_moves('M2 U M2 U2 M2 U M2')
        timed = algo.transform(time_moves(150))

        self.assertGreater(compute_memory(timed).repeated_patterns, 0)

    def test_t_perm(self) -> None:
        """T-Perm → Moderate."""
        algo = Algorithm.parse_moves("R U R' U' R' F R2 U' R' U' R U R' F'")
        mem = algo.memory
        self.assertGreater(mem.memory_score, 0.35)
        self.assertLess(mem.memory_score, 0.7)

    def test_empty_algorithm(self) -> None:
        """Empty algorithm → maximum scores, Trivial."""
        algo = Algorithm.parse_moves('')
        mem = compute_memory(algo)
        self.assertEqual(mem.memory_score, 1.0)
        self.assertEqual(mem.memory_rating, 'Trivial')
        self.assertEqual(mem.move_count, 0)
        self.assertEqual(mem.effective_chunks, 0)
        for field in (
            'length_score', 'chunk_score', 'structure_score',
            'repetition_score', 'face_familiarity_score',
            'flow_score', 'move_familiarity_score',
        ):
            self.assertEqual(getattr(mem, field), 1.0, msg=field)

    def test_single_move(self) -> None:
        """Single move → easy."""
        algo = Algorithm.parse_moves('R')
        mem = algo.memory
        self.assertGreater(mem.memory_score, 0.6)
        self.assertEqual(mem.move_count, 1)

    def test_all_pauses(self) -> None:
        """All-pause algorithm → treated as empty."""
        algo = Algorithm.parse_moves('. . .')
        mem = compute_memory(algo)
        self.assertEqual(mem.memory_score, 1.0)
        self.assertEqual(mem.memory_rating, 'Trivial')

    def test_only_rotations(self) -> None:
        """Only rotations → maximum familiarity penalty."""
        algo = Algorithm.parse_moves("x y z x' y' z'")
        mem = algo.memory
        self.assertEqual(mem.move_familiarity_score, 0.0)
        self.assertEqual(mem.distinct_faces, 0)


# --- Comparison Tests ---


class MemoryComparisonTestCase(unittest.TestCase):
    """Verify relative ordering of memorability."""

    def test_sexy_easier_than_sune(self) -> None:
        """Sexy move should be easier than Sune."""
        sexy = Algorithm.parse_moves("R U R' U'").memory
        sune = Algorithm.parse_moves("R U R' U R U2 R'").memory
        self.assertGreater(sexy.memory_score, sune.memory_score)

    def test_sune_easier_than_t_perm(self) -> None:
        """Sune should be easier than T-Perm."""
        sune = Algorithm.parse_moves("R U R' U R U2 R'").memory
        t_perm = Algorithm.parse_moves(
            "R U R' U' R' F R2 U' R' U' R U R' F'",
        ).memory
        self.assertGreater(sune.memory_score, t_perm.memory_score)

    def test_short_easier_than_long(self) -> None:
        """Short algorithm should be easier than long one."""
        short = Algorithm.parse_moves("R U R'").memory
        long_alg = Algorithm.parse_moves(
            "R U R' U R U2 R' U2 R' F R F' R U R' U' R' F R F'",
        ).memory
        self.assertGreater(short.memory_score, long_alg.memory_score)


# --- Anchor Tests for higher-is-easier semantics ---


class MemorySemanticsAnchorTestCase(unittest.TestCase):
    """Anchor the 0.0-1.0 higher-is-easier semantics of memory scores."""

    def test_sexy_move_scores_high(self) -> None:
        """R U R' U' is very easy to memorize → high score."""
        mem = Algorithm.parse_moves("R U R' U'").memory
        self.assertGreater(mem.memory_score, 0.75)
        self.assertIn(mem.memory_rating, ('Trivial', 'Easy'))

    def test_sune_scores_high(self) -> None:
        """Sune is easy to memorize → score above midpoint."""
        mem = Algorithm.parse_moves("R U R' U R U2 R'").memory
        self.assertGreater(mem.memory_score, 0.55)

    def test_long_multi_face_scores_low(self) -> None:
        """Long algorithm over many faces is hard → low score."""
        mem = Algorithm.parse_moves(
            "F B' D L' B U D' R F' L U2 B' D2 R' F2 L' B2 D' R2 U'",
        ).memory
        self.assertLess(mem.memory_score, 0.4)

    def test_empty_algorithm_scores_max(self) -> None:
        """Nothing to memorize is trivially easy → maximum score."""
        mem = compute_memory(Algorithm.parse_moves(''))
        self.assertEqual(mem.memory_score, 1.0)
        self.assertEqual(mem.memory_rating, 'Trivial')

    def test_unfamiliar_moves_lower_score(self) -> None:
        """Same shape on unfamiliar faces → lower score."""
        familiar = Algorithm.parse_moves("R U R' U'").memory
        unfamiliar = Algorithm.parse_moves("B D B' D'").memory
        self.assertLess(unfamiliar.memory_score, familiar.memory_score)

    def test_easier_algorithms_rank_higher(self) -> None:
        """Sexy > Sune > T-Perm in memorability."""
        sexy = Algorithm.parse_moves("R U R' U'").memory
        sune = Algorithm.parse_moves("R U R' U R U2 R'").memory
        t_perm = Algorithm.parse_moves(
            "R U R' U' R' F R2 U' R' U' R U R' F'",
        ).memory
        self.assertGreater(sexy.memory_score, sune.memory_score)
        self.assertGreater(sune.memory_score, t_perm.memory_score)


# --- Property Tests ---


class MemoryPropertyTestCase(unittest.TestCase):
    """Property-based tests for memory scores."""

    ALGORITHMS: ClassVar[list[str]] = [
        '',
        'R',
        "R U R' U'",
        "R U R' U R U2 R'",
        "R U R' U' R' F R2 U' R' U' R U R' F'",
        "F R U R' U' F'",
        "R' D' R D R' D' R D",
        'x y z',
        'M E S',
        "B D B' D'",
        '. . .',
    ]

    def test_score_in_range(self) -> None:
        """Memory score always in [0, 1]."""
        for alg_str in self.ALGORITHMS:
            with self.subTest(alg=alg_str):
                algo = Algorithm.parse_moves(alg_str)
                mem = compute_memory(algo)
                self.assertGreaterEqual(mem.memory_score, 0.0)
                self.assertLessEqual(mem.memory_score, 1.0)

    def test_rating_always_valid(self) -> None:
        """Rating is always one of the valid strings."""
        valid_ratings = {'Trivial', 'Easy', 'Moderate', 'Hard', 'Very Hard'}
        for alg_str in self.ALGORITHMS:
            with self.subTest(alg=alg_str):
                algo = Algorithm.parse_moves(alg_str)
                mem = compute_memory(algo)
                self.assertIn(mem.memory_rating, valid_ratings)

    def test_sub_scores_in_range(self) -> None:
        """All sub-scores should be in [0, 1]."""
        for alg_str in self.ALGORITHMS:
            with self.subTest(alg=alg_str):
                algo = Algorithm.parse_moves(alg_str)
                mem = compute_memory(algo)
                for field in (
                    'length_score', 'chunk_score', 'structure_score',
                    'repetition_score', 'face_familiarity_score',
                    'flow_score', 'move_familiarity_score',
                ):
                    value = getattr(mem, field)
                    self.assertGreaterEqual(
                        value, 0.0, msg=f'{field}={value} < 0',
                    )
                    self.assertLessEqual(
                        value, 1.0, msg=f'{field}={value} > 1',
                    )
