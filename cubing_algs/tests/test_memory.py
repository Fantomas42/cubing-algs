"""Tests for memory difficulty analysis."""
import unittest
from typing import ClassVar
from unittest.mock import patch

from cubing_algs.algorithm import Algorithm
from cubing_algs.memory import MemoryData
from cubing_algs.memory import compute_chunk_score
from cubing_algs.memory import compute_face_diversity_score
from cubing_algs.memory import compute_flow_memory_score
from cubing_algs.memory import compute_length_score
from cubing_algs.memory import compute_memory
from cubing_algs.memory import compute_move_familiarity_score
from cubing_algs.memory import compute_repetition_score
from cubing_algs.memory import compute_structure_score
from cubing_algs.memory import find_repeated_subsequences
from cubing_algs.memory import get_memory_rating


class LengthScoreTestCase(unittest.TestCase):
    """Tests for compute_length_score."""

    def test_zero_moves(self) -> None:
        """Zero moves should give very low score."""
        score = compute_length_score(0)
        self.assertLess(score, 5.0)

    def test_short_algorithm(self) -> None:
        """Short algorithm (4 HTM) → ~10."""
        score = compute_length_score(4)
        self.assertGreater(score, 3.0)
        self.assertLess(score, 20.0)

    def test_medium_algorithm(self) -> None:
        """Medium algorithm (12 HTM) → ~50."""
        score = compute_length_score(12)
        self.assertAlmostEqual(score, 50.0, delta=1.0)

    def test_long_algorithm(self) -> None:
        """Long algorithm (20 HTM) → ~90+."""
        score = compute_length_score(20)
        self.assertGreater(score, 85.0)

    def test_very_long_algorithm(self) -> None:
        """Very long algorithm → approaches 100."""
        score = compute_length_score(30)
        self.assertGreater(score, 95.0)
        self.assertLessEqual(score, 100.0)

    def test_monotonically_increasing(self) -> None:
        """Score should increase with move count."""
        scores = [compute_length_score(i) for i in range(25)]
        for i in range(1, len(scores)):
            self.assertGreater(scores[i], scores[i - 1])


class ChunkScoreTestCase(unittest.TestCase):
    """Tests for compute_chunk_score."""

    def test_single_chunk(self) -> None:
        """Single chunk should be easy."""
        score = compute_chunk_score(1, 1)
        self.assertLess(score, 20.0)

    def test_miller_easy(self) -> None:
        """5 chunks should be moderate."""
        score = compute_chunk_score(5, 1)
        self.assertAlmostEqual(score, 40.0, delta=5.0)

    def test_miller_hard(self) -> None:
        """9 chunks should be hard."""
        score = compute_chunk_score(9, 1)
        self.assertAlmostEqual(score, 80.0, delta=5.0)

    def test_beyond_miller(self) -> None:
        """Beyond 9 chunks → very hard."""
        score = compute_chunk_score(12, 1)
        self.assertGreater(score, 85.0)

    def test_variety_penalty(self) -> None:
        """More distinct triggers should increase score."""
        score_1 = compute_chunk_score(5, 1)
        score_3 = compute_chunk_score(5, 3)
        self.assertGreater(score_3, score_1)

    def test_capped_at_100(self) -> None:
        """Score should not exceed 100."""
        score = compute_chunk_score(20, 5)
        self.assertLessEqual(score, 100.0)


class StructureScoreTestCase(unittest.TestCase):
    """Tests for compute_structure_score."""

    def test_no_structure(self) -> None:
        """No structure → score 100."""
        score = compute_structure_score(0.0, 0.0, has_structure=False)
        self.assertEqual(score, 100.0)

    def test_full_coverage(self) -> None:
        """Full coverage + high compression → very low score."""
        score = compute_structure_score(1.0, 1.0, has_structure=True)
        self.assertLess(score, 5.0)

    def test_partial_coverage(self) -> None:
        """Partial coverage → moderate score."""
        score = compute_structure_score(0.5, 0.3, has_structure=True)
        self.assertGreater(score, 20.0)
        self.assertLess(score, 80.0)

    def test_zero_coverage_with_structure(self) -> None:
        """Zero coverage with structure → score 100."""
        score = compute_structure_score(0.0, 0.0, has_structure=True)
        self.assertEqual(score, 100.0)


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
        """No repeats → score 100 (hard, no help from repetition)."""
        score = compute_repetition_score(0, 10)
        self.assertEqual(score, 100.0)

    def test_repetition_score_many_repeats(self) -> None:
        """Many repeats → lower score (easier)."""
        score = compute_repetition_score(10, 10)
        self.assertLess(score, 40.0)

    def test_repetition_score_zero_stm(self) -> None:
        """Zero STM → score 0."""
        score = compute_repetition_score(0, 0)
        self.assertEqual(score, 0.0)


class FaceDiversityScoreTestCase(unittest.TestCase):
    """Tests for compute_face_diversity_score."""

    def test_ru_only(self) -> None:
        """R and U only → low score."""
        algo = Algorithm.parse_moves("R U R' U'")
        moves = [m for m in algo if not m.is_pause]
        score = compute_face_diversity_score(moves)
        self.assertLess(score, 25.0)

    def test_all_faces(self) -> None:
        """All 6 faces → high score."""
        algo = Algorithm.parse_moves('R U F L D B')
        moves = [m for m in algo if not m.is_pause]
        score = compute_face_diversity_score(moves)
        self.assertGreater(score, 70.0)

    def test_empty(self) -> None:
        """No moves → score 0."""
        score = compute_face_diversity_score([])
        self.assertEqual(score, 0.0)

    def test_all_faces_fully_familiar(self) -> None:
        """When all face familiarity weights are 1.0, normalized is 0."""
        all_familiar = dict.fromkeys('RUFLDB', 1.0)
        algo = Algorithm.parse_moves('R U F')
        moves = [m for m in algo if not m.is_pause]
        with patch('cubing_algs.memory.FACE_FAMILIARITY', all_familiar):
            score = compute_face_diversity_score(moves)
        # Only the face_count_score component contributes (3/6 * 60 = 30)
        self.assertAlmostEqual(score, 30.0, delta=1.0)

    def test_unfamiliar_faces_penalized(self) -> None:
        """B and D moves should increase score more than R and U."""
        algo_ru = Algorithm.parse_moves("R U R' U'")
        algo_bd = Algorithm.parse_moves("B D B' D'")
        moves_ru = [m for m in algo_ru if not m.is_pause]
        moves_bd = [m for m in algo_bd if not m.is_pause]
        score_ru = compute_face_diversity_score(moves_ru)
        score_bd = compute_face_diversity_score(moves_bd)
        self.assertGreater(score_bd, score_ru)


class FlowMemoryScoreTestCase(unittest.TestCase):
    """Tests for compute_flow_memory_score."""

    def test_zero_stm(self) -> None:
        """Zero STM → score 0."""
        score = compute_flow_memory_score(0, 0, 0)
        self.assertEqual(score, 0.0)

    def test_no_interruptions(self) -> None:
        """No interruptions → score 0."""
        score = compute_flow_memory_score(0, 0, 10)
        self.assertEqual(score, 0.0)

    def test_many_interruptions(self) -> None:
        """Many interruptions → high score."""
        score = compute_flow_memory_score(5, 5, 10)
        self.assertGreater(score, 50.0)

    def test_capped_at_100(self) -> None:
        """Score should not exceed 100."""
        score = compute_flow_memory_score(100, 100, 10)
        self.assertLessEqual(score, 100.0)


class MoveFamiliarityScoreTestCase(unittest.TestCase):
    """Tests for compute_move_familiarity_score."""

    def test_all_familiar(self) -> None:
        """All R/U moves → score 0."""
        algo = Algorithm.parse_moves("R U R' U'")
        moves = [m for m in algo if not m.is_pause]
        score = compute_move_familiarity_score(moves)
        self.assertEqual(score, 0.0)

    def test_all_unfamiliar(self) -> None:
        """All B/D moves → score 100."""
        algo = Algorithm.parse_moves("B D B' D'")
        moves = [m for m in algo if not m.is_pause]
        score = compute_move_familiarity_score(moves)
        self.assertEqual(score, 100.0)

    def test_mixed(self) -> None:
        """Mix of familiar and unfamiliar → between 0 and 100."""
        algo = Algorithm.parse_moves('R U B D')
        moves = [m for m in algo if not m.is_pause]
        score = compute_move_familiarity_score(moves)
        self.assertGreater(score, 0.0)
        self.assertLess(score, 100.0)

    def test_empty(self) -> None:
        """No moves → score 0."""
        score = compute_move_familiarity_score([])
        self.assertEqual(score, 0.0)

    def test_rotations_unfamiliar(self) -> None:
        """Rotation moves count as unfamiliar."""
        algo = Algorithm.parse_moves('x y z')
        moves = [m for m in algo if not m.is_pause]
        score = compute_move_familiarity_score(moves)
        self.assertEqual(score, 100.0)

    def test_slice_moves_unfamiliar(self) -> None:
        """Slice moves count as unfamiliar."""
        algo = Algorithm.parse_moves('M E S')
        moves = [m for m in algo if not m.is_pause]
        score = compute_move_familiarity_score(moves)
        self.assertEqual(score, 100.0)


class MemoryRatingTestCase(unittest.TestCase):
    """Tests for get_memory_rating."""

    def test_trivial(self) -> None:
        """Score 0-20 → Trivial."""
        self.assertEqual(get_memory_rating(0.0), 'Trivial')
        self.assertEqual(get_memory_rating(10.0), 'Trivial')
        self.assertEqual(get_memory_rating(19.9), 'Trivial')

    def test_negative_score(self) -> None:
        """Negative score → Trivial (fallback)."""
        self.assertEqual(get_memory_rating(-1.0), 'Trivial')

    def test_easy(self) -> None:
        """Score 20-40 → Easy."""
        self.assertEqual(get_memory_rating(20.0), 'Easy')
        self.assertEqual(get_memory_rating(30.0), 'Easy')

    def test_moderate(self) -> None:
        """Score 40-60 → Moderate."""
        self.assertEqual(get_memory_rating(40.0), 'Moderate')
        self.assertEqual(get_memory_rating(50.0), 'Moderate')

    def test_hard(self) -> None:
        """Score 60-80 → Hard."""
        self.assertEqual(get_memory_rating(60.0), 'Hard')
        self.assertEqual(get_memory_rating(70.0), 'Hard')

    def test_very_hard(self) -> None:
        """Score 80-100 → Very Hard."""
        self.assertEqual(get_memory_rating(80.0), 'Very Hard')
        self.assertEqual(get_memory_rating(100.0), 'Very Hard')


# --- Integration Tests ---


class ComputeMemoryIntegrationTestCase(unittest.TestCase):
    """Integration tests for compute_memory with real algorithms."""

    def test_sexy_move(self) -> None:
        """R U R' U' → Trivial (1 trigger, RU only)."""
        algo = Algorithm.parse_moves("R U R' U'")
        mem = algo.memory
        self.assertIsInstance(mem, MemoryData)
        self.assertLess(mem.memory_score, 25.0)
        self.assertIn(mem.memory_rating, ('Trivial', 'Easy'))

    def test_sune(self) -> None:
        """Sune → Easy."""
        algo = Algorithm.parse_moves("R U R' U R U2 R'")
        mem = algo.memory
        self.assertLess(mem.memory_score, 45.0)
        self.assertIn(mem.memory_rating, ('Easy', 'Moderate'))

    def test_t_perm(self) -> None:
        """T-Perm → Easy/Moderate."""
        algo = Algorithm.parse_moves("R U R' U' R' F R2 U' R' U' R U R' F'")
        mem = algo.memory
        self.assertGreater(mem.memory_score, 15.0)
        self.assertLess(mem.memory_score, 60.0)

    def test_empty_algorithm(self) -> None:
        """Empty algorithm → zeroed MemoryData, Trivial."""
        algo = Algorithm.parse_moves('')
        mem = compute_memory(algo)
        self.assertEqual(mem.memory_score, 0.0)
        self.assertEqual(mem.memory_rating, 'Trivial')
        self.assertEqual(mem.move_count, 0)
        self.assertEqual(mem.effective_chunks, 0)

    def test_single_move(self) -> None:
        """Single move → very easy."""
        algo = Algorithm.parse_moves('R')
        mem = algo.memory
        self.assertLess(mem.memory_score, 30.0)
        self.assertEqual(mem.move_count, 1)

    def test_all_pauses(self) -> None:
        """All-pause algorithm → treated as empty."""
        algo = Algorithm.parse_moves('. . .')
        mem = compute_memory(algo)
        self.assertEqual(mem.memory_score, 0.0)
        self.assertEqual(mem.memory_rating, 'Trivial')

    def test_only_rotations(self) -> None:
        """Only rotations → high familiarity penalty."""
        algo = Algorithm.parse_moves("x y z x' y' z'")
        mem = algo.memory
        self.assertEqual(mem.move_familiarity_score, 100.0)
        self.assertEqual(mem.distinct_faces, 0)


# --- Comparison Tests ---


class MemoryComparisonTestCase(unittest.TestCase):
    """Verify relative ordering of memory difficulty."""

    def test_sexy_easier_than_sune(self) -> None:
        """Sexy move should be easier than Sune."""
        sexy = Algorithm.parse_moves("R U R' U'").memory
        sune = Algorithm.parse_moves("R U R' U R U2 R'").memory
        self.assertLess(sexy.memory_score, sune.memory_score)

    def test_sune_easier_than_t_perm(self) -> None:
        """Sune should be easier than T-Perm."""
        sune = Algorithm.parse_moves("R U R' U R U2 R'").memory
        t_perm = Algorithm.parse_moves(
            "R U R' U' R' F R2 U' R' U' R U R' F'",
        ).memory
        self.assertLess(sune.memory_score, t_perm.memory_score)

    def test_short_easier_than_long(self) -> None:
        """Short algorithm should be easier than long one."""
        short = Algorithm.parse_moves("R U R'").memory
        long_alg = Algorithm.parse_moves(
            "R U R' U R U2 R' U2 R' F R F' R U R' U' R' F R F'",
        ).memory
        self.assertLess(short.memory_score, long_alg.memory_score)


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
        """Memory score always in [0, 100]."""
        for alg_str in self.ALGORITHMS:
            with self.subTest(alg=alg_str):
                algo = Algorithm.parse_moves(alg_str)
                mem = compute_memory(algo)
                self.assertGreaterEqual(mem.memory_score, 0.0)
                self.assertLessEqual(mem.memory_score, 100.0)

    def test_rating_always_valid(self) -> None:
        """Rating is always one of the valid strings."""
        valid_ratings = {'Trivial', 'Easy', 'Moderate', 'Hard', 'Very Hard'}
        for alg_str in self.ALGORITHMS:
            with self.subTest(alg=alg_str):
                algo = Algorithm.parse_moves(alg_str)
                mem = compute_memory(algo)
                self.assertIn(mem.memory_rating, valid_ratings)

    def test_sub_scores_in_range(self) -> None:
        """All sub-scores should be in [0, 100]."""
        for alg_str in self.ALGORITHMS:
            with self.subTest(alg=alg_str):
                algo = Algorithm.parse_moves(alg_str)
                mem = compute_memory(algo)
                for field in (
                    'length_score', 'chunk_score', 'structure_score',
                    'repetition_score', 'face_diversity_score',
                    'flow_score', 'move_familiarity_score',
                ):
                    value = getattr(mem, field)
                    self.assertGreaterEqual(
                        value, 0.0, msg=f'{field}={value} < 0',
                    )
                    self.assertLessEqual(
                        value, 100.0, msg=f'{field}={value} > 100',
                    )
