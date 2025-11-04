"""Tests for ergonomics analysis."""

import unittest
from unittest.mock import patch

from cubing_algs.algorithm import Algorithm
from cubing_algs.ergonomics import ErgonomicsData
from cubing_algs.ergonomics import compute_comfort_score
from cubing_algs.ergonomics import compute_ergonomics
from cubing_algs.ergonomics import compute_estimated_execution_time
from cubing_algs.ergonomics import compute_finger_distribution
from cubing_algs.ergonomics import compute_fingertrick_difficulty
from cubing_algs.ergonomics import compute_flow_breaks
from cubing_algs.ergonomics import compute_hand_balance
from cubing_algs.ergonomics import compute_regrip_count
from cubing_algs.ergonomics import get_ergonomic_rating
from cubing_algs.ergonomics import get_move_key
from cubing_algs.move import Move


class TestGetMoveKey(unittest.TestCase):
    """Test the get_move_key function for move standardization."""

    def test_basic_moves(self) -> None:
        """Test basic move key extraction."""
        self.assertEqual(get_move_key(Move('R')), 'R')
        self.assertEqual(get_move_key(Move("R'")), "R'")
        self.assertEqual(get_move_key(Move('R2')), 'R2')

    def test_wide_moves(self) -> None:
        """Test wide move key extraction."""
        self.assertEqual(get_move_key(Move('Rw')), 'Rw')
        self.assertEqual(get_move_key(Move("Rw'")), "Rw'")
        self.assertEqual(get_move_key(Move('Rw2')), 'Rw2')

    def test_slice_moves(self) -> None:
        """Test slice move key extraction."""
        self.assertEqual(get_move_key(Move('M')), 'M')
        self.assertEqual(get_move_key(Move("M'")), "M'")
        self.assertEqual(get_move_key(Move('M2')), 'M2')

    def test_rotation_moves(self) -> None:
        """Test rotation move key extraction."""
        self.assertEqual(get_move_key(Move('x')), 'x')
        self.assertEqual(get_move_key(Move("y'")), "y'")
        self.assertEqual(get_move_key(Move('z2')), 'z2')

    def test_pause_moves(self) -> None:
        """Test pause move key extraction."""
        self.assertEqual(get_move_key(Move('.')), '.')

    def test_sign_moves(self) -> None:
        """Test SiGN notation move key extraction."""
        # SiGN moves should be converted to standard notation
        sign_move = Move('r')  # lowercase r is SiGN notation for Rw
        key = get_move_key(sign_move)
        # Should convert to standard notation
        self.assertEqual(key, 'Rw')

    def test_layered_moves(self) -> None:
        """Test layered move key extraction returns unlayered version."""
        layered_move = Move('2-4Rw')
        key = get_move_key(layered_move)
        self.assertEqual(key, 'Rw')


class TestComputeHandBalance(unittest.TestCase):
    """Test hand balance computation."""

    def test_empty_algorithm(self) -> None:
        """Test hand balance for empty algorithm."""
        alg = Algorithm.parse_moves('')
        right, left, both, ratio = compute_hand_balance(alg)
        self.assertEqual(right, 0)
        self.assertEqual(left, 0)
        self.assertEqual(both, 0)
        self.assertEqual(ratio, 0.5)  # Perfect balance for empty algorithm

    def test_right_hand_dominant(self) -> None:
        """Test algorithm with right-hand dominant moves."""
        alg = Algorithm.parse_moves("R U R' U'")
        right, left, both, ratio = compute_hand_balance(alg)
        self.assertEqual(right, 2)  # R and R'
        self.assertEqual(left, 0)
        self.assertEqual(both, 2)  # U and U'
        self.assertEqual(ratio, 0.0)  # All handed moves are right

    def test_left_hand_dominant(self) -> None:
        """Test algorithm with left-hand dominant moves."""
        alg = Algorithm.parse_moves("L' U' L U")
        right, left, both, ratio = compute_hand_balance(alg)
        self.assertEqual(right, 0)
        self.assertEqual(left, 2)  # L' and L
        self.assertEqual(both, 2)  # U' and U
        self.assertEqual(ratio, 0.0)  # All handed moves are left

    def test_balanced_algorithm(self) -> None:
        """Test perfectly balanced algorithm."""
        alg = Algorithm.parse_moves("R U R' U' L' U' L U")
        right, left, both, ratio = compute_hand_balance(alg)
        self.assertEqual(right, 2)  # R and R'
        self.assertEqual(left, 2)  # L' and L
        self.assertEqual(both, 4)  # All U moves
        self.assertEqual(ratio, 0.5)  # Perfect balance

    def test_only_both_hand_moves(self) -> None:
        """Test algorithm with only both-hand moves."""
        alg = Algorithm.parse_moves("U D U' D'")
        right, left, both, ratio = compute_hand_balance(alg)
        self.assertEqual(right, 0)
        self.assertEqual(left, 0)
        self.assertEqual(both, 4)
        self.assertEqual(ratio, 0.5)  # Perfect balance when no handed moves

    def test_with_pauses(self) -> None:
        """Test hand balance calculation ignores pauses."""
        alg = Algorithm.parse_moves("R . U . R'")
        right, left, both, ratio = compute_hand_balance(alg)
        self.assertEqual(right, 2)  # R and R'
        self.assertEqual(left, 0)
        self.assertEqual(both, 1)  # U
        self.assertEqual(ratio, 0.0)  # All handed moves are right


class TestComputeFingerDistribution(unittest.TestCase):
    """Test finger distribution computation."""

    def test_empty_algorithm(self) -> None:
        """Test finger distribution for empty algorithm."""
        alg = Algorithm.parse_moves('')
        thumb, index, middle, ring = compute_finger_distribution(alg)
        self.assertEqual(thumb, 0)
        self.assertEqual(index, 0)
        self.assertEqual(middle, 0)
        self.assertEqual(ring, 0)

    def test_thumb_moves(self) -> None:
        """Test algorithm with thumb moves."""
        alg = Algorithm.parse_moves("R L R' L'")
        thumb, index, middle, ring = compute_finger_distribution(alg)
        self.assertEqual(thumb, 4)  # All R and L moves use thumb
        self.assertEqual(index, 0)
        self.assertEqual(middle, 0)
        self.assertEqual(ring, 0)

    def test_index_finger_moves(self) -> None:
        """Test algorithm with index finger moves."""
        alg = Algorithm.parse_moves("U D U' D'")
        thumb, index, middle, ring = compute_finger_distribution(alg)
        self.assertEqual(thumb, 0)
        self.assertEqual(index, 4)  # All U and D moves use index finger
        self.assertEqual(middle, 0)
        self.assertEqual(ring, 0)

    def test_middle_finger_moves(self) -> None:
        """Test algorithm with middle finger moves."""
        alg = Algorithm.parse_moves("F B F' B'")
        thumb, index, middle, ring = compute_finger_distribution(alg)
        self.assertEqual(thumb, 0)
        self.assertEqual(index, 0)
        self.assertEqual(middle, 4)  # All F and B moves use middle finger
        self.assertEqual(ring, 0)

    def test_ring_finger_moves(self) -> None:
        """Test algorithm with ring finger moves (slice moves)."""
        alg = Algorithm.parse_moves("M E S M'")
        thumb, index, middle, ring = compute_finger_distribution(alg)
        self.assertEqual(thumb, 0)
        self.assertEqual(index, 0)
        self.assertEqual(middle, 0)
        self.assertEqual(ring, 4)  # All slice moves use ring finger

    def test_mixed_finger_usage(self) -> None:
        """Test algorithm with mixed finger usage."""
        alg = Algorithm.parse_moves('R U F M')
        thumb, index, middle, ring = compute_finger_distribution(alg)
        self.assertEqual(thumb, 1)  # R
        self.assertEqual(index, 1)  # U
        self.assertEqual(middle, 1)  # F
        self.assertEqual(ring, 1)  # M

    def test_with_pauses(self) -> None:
        """Test finger distribution calculation ignores pauses."""
        alg = Algorithm.parse_moves('R . U . F')
        thumb, index, middle, ring = compute_finger_distribution(alg)
        self.assertEqual(thumb, 1)  # R
        self.assertEqual(index, 1)  # U
        self.assertEqual(middle, 1)  # F
        self.assertEqual(ring, 0)

    def test_ring_finger_moves_as_last_move(self) -> None:
        """Test algorithm ending with ring finger move for branch coverage."""
        alg = Algorithm.parse_moves('R U M')
        thumb, index, middle, ring = compute_finger_distribution(alg)
        self.assertEqual(thumb, 1)  # R
        self.assertEqual(index, 1)  # U
        self.assertEqual(middle, 0)
        self.assertEqual(ring, 1)  # M

    def test_single_ring_finger_move(self) -> None:
        """Test algorithm with only ring finger move for branch coverage."""
        alg = Algorithm.parse_moves('S')
        thumb, index, middle, ring = compute_finger_distribution(alg)
        self.assertEqual(thumb, 0)
        self.assertEqual(index, 0)
        self.assertEqual(middle, 0)
        self.assertEqual(ring, 1)  # S

    def test_algorithm_ending_with_ring_finger(self) -> None:
        """Test for complete branch coverage with ring finger move at end."""
        # Test different ring finger moves to ensure full branch coverage
        for move_str in ['M', 'E', 'S', "M'", "E'", "S'", 'M2', 'E2', 'S2']:
            alg = Algorithm.parse_moves(move_str)
            thumb, index, middle, ring = compute_finger_distribution(alg)
            self.assertEqual(ring, 1, f'Ring finger count wrong for {move_str}')
            self.assertEqual(thumb + index + middle, 0,
                           f'Other fingers should be 0 for {move_str}')

    def test_multiple_ring_finger_moves(self) -> None:
        """Test multiple consecutive ring finger moves for branch coverage."""
        alg = Algorithm.parse_moves('M E S')
        thumb, index, middle, ring = compute_finger_distribution(alg)
        self.assertEqual(thumb, 0)
        self.assertEqual(index, 0)
        self.assertEqual(middle, 0)
        self.assertEqual(ring, 3)

    def test_empty_finger_distribution_for_coverage(self) -> None:
        """Test edge case to ensure complete branch coverage."""
        # This test targets potential edge cases in branch coverage

        # Create algorithm with specific sequence that might hit missing branch
        moves = [Move('M')]  # Single ring finger move as Move object
        alg = Algorithm(moves)
        thumb, index, middle, ring = compute_finger_distribution(alg)
        self.assertEqual(ring, 1)

        # Also test with empty algorithm
        empty_alg = Algorithm([])
        thumb, index, middle, ring = compute_finger_distribution(empty_alg)
        self.assertEqual(thumb, 0)
        self.assertEqual(index, 0)
        self.assertEqual(middle, 0)
        self.assertEqual(ring, 0)

    def test_rotation_moves_default_to_index(self) -> None:
        """Test that rotation moves default to index finger."""
        # Rotation moves are not in FINGER_ASSIGNMENTS, should default to index
        alg = Algorithm.parse_moves('x y z')
        thumb, index, middle, ring = compute_finger_distribution(alg)
        self.assertEqual(thumb, 0)
        self.assertEqual(index, 3)  # All rotations default to index
        self.assertEqual(middle, 0)
        self.assertEqual(ring, 0)

    def test_wide_moves_default_to_index(self) -> None:
        """Test that wide moves default to index finger."""
        # Wide moves are not in FINGER_ASSIGNMENTS, should default to index
        alg = Algorithm.parse_moves('Rw Uw Fw')
        thumb, index, middle, ring = compute_finger_distribution(alg)
        self.assertEqual(thumb, 0)
        self.assertEqual(index, 3)  # All wide moves default to index
        self.assertEqual(middle, 0)
        self.assertEqual(ring, 0)

    def test_ring_finger_not_last_move(self) -> None:
        """Test ring move followed by another for branch coverage."""
        # This test ensures the branch from ring finger check back to loop
        alg = Algorithm.parse_moves('M R')  # ring finger then thumb
        thumb, index, middle, ring = compute_finger_distribution(alg)
        self.assertEqual(thumb, 1)
        self.assertEqual(index, 0)
        self.assertEqual(middle, 0)
        self.assertEqual(ring, 1)

    def test_unknown_finger_type_not_counted(self) -> None:
        """Test that unknown finger types don't increment any counter."""
        # Mock FINGER_ASSIGNMENTS to return an unknown finger type
        with patch('cubing_algs.ergonomics.FINGER_ASSIGNMENTS', {'R': 'pinky'}):
            alg = Algorithm.parse_moves('R')
            thumb, index, middle, ring = compute_finger_distribution(alg)
            # Unknown finger type should not increment any counter
            self.assertEqual(thumb, 0)
            self.assertEqual(index, 0)
            self.assertEqual(middle, 0)
            self.assertEqual(ring, 0)


class TestComputeRegripCount(unittest.TestCase):
    """Test regrip count computation."""

    def test_empty_algorithm(self) -> None:
        """Test regrip count for empty algorithm."""
        alg = Algorithm.parse_moves('')
        regrips = compute_regrip_count(alg)
        self.assertEqual(regrips, 0)

    def test_no_regrip_moves(self) -> None:
        """Test algorithm with no regrip moves."""
        alg = Algorithm.parse_moves("R U R' U'")
        regrips = compute_regrip_count(alg)
        self.assertEqual(regrips, 0)  # R and U moves don't require regrips

    def test_b_moves_require_regrips(self) -> None:
        """Test that B moves require regrips."""
        alg = Algorithm.parse_moves("B B' B2")
        regrips = compute_regrip_count(alg)
        self.assertEqual(regrips, 3)  # All B moves require regrips

    def test_d_moves_require_regrips(self) -> None:
        """Test that D moves require regrips."""
        alg = Algorithm.parse_moves("D D' D2")
        regrips = compute_regrip_count(alg)
        self.assertEqual(regrips, 3)  # All D moves require regrips

    def test_slice_moves_require_regrips(self) -> None:
        """Test that slice moves require regrips."""
        alg = Algorithm.parse_moves("E E' S S2")
        regrips = compute_regrip_count(alg)
        self.assertEqual(regrips, 4)  # E and S moves require regrips

    def test_mixed_algorithm(self) -> None:
        """Test algorithm with mixed regrip and non-regrip moves."""
        alg = Algorithm.parse_moves('R U B D F')
        regrips = compute_regrip_count(alg)
        self.assertEqual(regrips, 2)  # B and D require regrips

    def test_with_pauses(self) -> None:
        """Test regrip count calculation ignores pauses."""
        alg = Algorithm.parse_moves('B . D . R')
        regrips = compute_regrip_count(alg)
        self.assertEqual(regrips, 2)  # B and D require regrips


class TestComputeFlowBreaks(unittest.TestCase):
    """Test flow breaks computation."""

    def test_empty_algorithm(self) -> None:
        """Test flow breaks for empty algorithm."""
        alg = Algorithm.parse_moves('')
        breaks = compute_flow_breaks(alg)
        self.assertEqual(breaks, 0)

    def test_single_move(self) -> None:
        """Test flow breaks for single move."""
        alg = Algorithm.parse_moves('R')
        breaks = compute_flow_breaks(alg)
        self.assertEqual(breaks, 0)

    def test_no_flow_breaks(self) -> None:
        """Test algorithm with no flow breaks."""
        alg = Algorithm.parse_moves("R U R' U'")
        breaks = compute_flow_breaks(alg)
        self.assertEqual(breaks, 0)  # No awkward transitions

    def test_r_to_l_flow_break(self) -> None:
        """Test R to L transition creates flow break."""
        alg = Algorithm.parse_moves('R L')
        breaks = compute_flow_breaks(alg)
        self.assertEqual(breaks, 1)  # R to L is awkward

    def test_l_to_r_flow_break(self) -> None:
        """Test L to R transition creates flow break."""
        alg = Algorithm.parse_moves('L R')
        breaks = compute_flow_breaks(alg)
        self.assertEqual(breaks, 1)  # L to R is awkward

    def test_f_to_b_flow_break(self) -> None:
        """Test F to B transition creates flow break."""
        alg = Algorithm.parse_moves('F B')
        breaks = compute_flow_breaks(alg)
        self.assertEqual(breaks, 1)  # F to B is awkward

    def test_m_to_r_flow_break(self) -> None:
        """Test M to R transition creates flow break."""
        alg = Algorithm.parse_moves('M R')
        breaks = compute_flow_breaks(alg)
        self.assertEqual(breaks, 1)  # M to R is awkward

    def test_multiple_flow_breaks(self) -> None:
        """Test algorithm with multiple flow breaks."""
        alg = Algorithm.parse_moves('R L F B')
        breaks = compute_flow_breaks(alg)
        self.assertEqual(breaks, 2)  # R->L and F->B are both awkward

    def test_modifiers_ignored_in_flow_breaks(self) -> None:
        """Test that move modifiers are ignored when checking flow breaks."""
        alg = Algorithm.parse_moves("R' L2")
        breaks = compute_flow_breaks(alg)
        self.assertEqual(breaks, 1)  # R' to L2 is still R to L transition

    def test_with_pauses(self) -> None:
        """Test flow breaks calculation ignores pauses."""
        alg = Algorithm.parse_moves('R . L')
        breaks = compute_flow_breaks(alg)
        self.assertEqual(breaks, 1)  # R to L transition still detected


class TestComputeFingertrickDifficulty(unittest.TestCase):
    """Test fingertrick difficulty computation."""

    def test_empty_algorithm(self) -> None:
        """Test fingertrick difficulty for empty algorithm."""
        alg = Algorithm.parse_moves('')
        difficulty = compute_fingertrick_difficulty(alg)
        self.assertEqual(difficulty, 0.0)

    def test_easy_moves(self) -> None:
        """Test algorithm with easy moves."""
        alg = Algorithm.parse_moves('R U')
        difficulty = compute_fingertrick_difficulty(alg)
        expected = (1.0 + 1.0) / 2  # R=1.0, U=1.0
        self.assertEqual(difficulty, expected)

    def test_difficult_moves(self) -> None:
        """Test algorithm with difficult moves."""
        alg = Algorithm.parse_moves('S2 E2')
        difficulty = compute_fingertrick_difficulty(alg)
        expected = (2.0 + 1.9) / 2  # S2=2.0, E2=1.9
        self.assertEqual(difficulty, expected)

    def test_mixed_difficulty(self) -> None:
        """Test algorithm with mixed difficulty moves."""
        alg = Algorithm.parse_moves('R M')
        difficulty = compute_fingertrick_difficulty(alg)
        expected = (1.0 + 1.5) / 2  # R=1.0, M=1.5
        self.assertEqual(difficulty, expected)

    def test_unknown_move_defaults_to_one(self) -> None:
        """Test that unknown moves default to difficulty 1.0."""
        # Create algorithm with move not in MOVE_DIFFICULTY
        alg = Algorithm([Move('x')])  # x rotation has difficulty 1.0
        difficulty = compute_fingertrick_difficulty(alg)
        self.assertEqual(difficulty, 1.0)

    def test_with_pauses(self) -> None:
        """Test fingertrick difficulty calculation ignores pauses."""
        alg = Algorithm.parse_moves('R . U')
        difficulty = compute_fingertrick_difficulty(alg)
        expected = (1.0 + 1.0) / 2  # R=1.0, U=1.0
        self.assertEqual(difficulty, expected)


class TestComputeEstimatedExecutionTime(unittest.TestCase):
    """Test estimated execution time computation."""

    def test_empty_algorithm(self) -> None:
        """Test execution time for empty algorithm."""
        alg = Algorithm.parse_moves('')
        time = compute_estimated_execution_time(alg, 0)
        self.assertEqual(time, 0.0)

    def test_base_move_time(self) -> None:
        """Test execution time calculation with base move time."""
        alg = Algorithm.parse_moves('R U')
        time = compute_estimated_execution_time(alg, 0)
        expected = 2 * 0.15  # 2 moves * 0.15 seconds per move
        self.assertEqual(time, expected)

    def test_with_regrips(self) -> None:
        """Test execution time includes regrip penalties."""
        alg = Algorithm.parse_moves('R U')
        time = compute_estimated_execution_time(alg, 2)
        expected = (2 * 0.15) + (2 * 0.07)  # 2 moves + 2 regrips
        self.assertEqual(time, expected)

    def test_with_pauses(self) -> None:
        """Test execution time calculation ignores pauses."""
        alg = Algorithm.parse_moves('R . U')
        time = compute_estimated_execution_time(alg, 0)
        expected = 2 * 0.15  # Only count non-pause moves
        self.assertEqual(time, expected)


class TestComputeComfortScore(unittest.TestCase):
    """Test comfort score computation."""

    def test_empty_algorithm_perfect_score(self) -> None:
        """Test that empty algorithm gets perfect score."""
        score = compute_comfort_score(0.5, 1.0, 0, 0, 0)
        self.assertEqual(score, 100.0)

    def test_perfect_balance_maximum_points(self) -> None:
        """Test that perfect hand balance gives maximum balance points."""
        score = compute_comfort_score(0.5, 1.0, 0, 0, 4)
        # hand_balance(0.5) * 25 = 12.5 points
        # difficulty: 25 - (1.0/2.0 * 25) = 12.5 points
        # regrip: 25 - (0/4 * 25) = 25 points
        # flow: 25 - (0/3 * 25) = 25 points
        expected = 12.5 + 12.5 + 25 + 25
        self.assertEqual(score, expected)

    def test_imbalanced_hands_lower_score(self) -> None:
        """Test that imbalanced hands lower the score."""
        score = compute_comfort_score(0.0, 1.0, 0, 0, 4)
        # hand_balance(0.0) * 25 = 0 points
        expected = 0 + 12.5 + 25 + 25
        self.assertEqual(score, expected)

    def test_high_difficulty_lowers_score(self) -> None:
        """Test that high difficulty lowers the score."""
        score = compute_comfort_score(0.5, 2.0, 0, 0, 4)
        # difficulty: 25 - (2.0/2.0 * 25) = 0 points
        expected = 12.5 + 0 + 25 + 25
        self.assertEqual(score, expected)

    def test_many_regrips_lower_score(self) -> None:
        """Test that many regrips lower the score."""
        score = compute_comfort_score(0.5, 1.0, 4, 0, 4)
        # regrip: 25 - (4/4 * 25) = 0 points
        expected = 12.5 + 12.5 + 0 + 25
        self.assertEqual(score, expected)

    def test_many_flow_breaks_lower_score(self) -> None:
        """Test that many flow breaks lower the score."""
        score = compute_comfort_score(0.5, 1.0, 0, 3, 4)
        # flow: 25 - (3/3 * 25) = 0 points
        expected = 12.5 + 12.5 + 25 + 0
        self.assertEqual(score, expected)


class TestGetErgonomicRating(unittest.TestCase):
    """Test ergonomic rating conversion."""

    def test_excellent_rating(self) -> None:
        """Test excellent rating threshold."""
        self.assertEqual(get_ergonomic_rating(100.0), 'Excellent')
        self.assertEqual(get_ergonomic_rating(80.0), 'Excellent')

    def test_good_rating(self) -> None:
        """Test good rating threshold."""
        self.assertEqual(get_ergonomic_rating(79.9), 'Good')
        self.assertEqual(get_ergonomic_rating(65.0), 'Good')

    def test_fair_rating(self) -> None:
        """Test fair rating threshold."""
        self.assertEqual(get_ergonomic_rating(64.9), 'Fair')
        self.assertEqual(get_ergonomic_rating(50.0), 'Fair')

    def test_poor_rating(self) -> None:
        """Test poor rating threshold."""
        self.assertEqual(get_ergonomic_rating(49.9), 'Poor')
        self.assertEqual(get_ergonomic_rating(35.0), 'Poor')

    def test_very_poor_rating(self) -> None:
        """Test very poor rating threshold."""
        self.assertEqual(get_ergonomic_rating(34.9), 'Very Poor')
        self.assertEqual(get_ergonomic_rating(0.0), 'Very Poor')


class TestComputeErgonomics(unittest.TestCase):
    """Test the main compute_ergonomics function with scenarios."""

    def test_empty_algorithm(self) -> None:
        """Test ergonomics computation for empty algorithm."""
        alg = Algorithm.parse_moves('')
        result = compute_ergonomics(alg)

        # Verify all fields are set correctly for empty algorithm
        self.assertEqual(result.total_moves, 0)
        self.assertEqual(result.right_hand_moves, 0)
        self.assertEqual(result.left_hand_moves, 0)
        self.assertEqual(result.both_hand_moves, 0)
        self.assertEqual(result.hand_balance_ratio, 0.5)
        self.assertEqual(result.regrip_count, 0)
        self.assertEqual(result.awkward_moves, 0)
        self.assertEqual(result.flow_breaks, 0)
        self.assertEqual(result.estimated_execution_time, 0.0)
        self.assertEqual(result.fingertrick_difficulty, 0.0)
        self.assertEqual(result.thumb_moves, 0)
        self.assertEqual(result.index_finger_moves, 0)
        self.assertEqual(result.middle_finger_moves, 0)
        self.assertEqual(result.ring_finger_moves, 0)
        self.assertEqual(result.comfort_score, 100.0)
        self.assertEqual(result.ergonomic_rating, 'Excellent')

    def test_sexy_move_right_hand_heavy(self) -> None:
        """Test ergonomics for sexy move (R U R' U') - right-hand heavy."""
        alg = Algorithm.parse_moves("R U R' U'")
        result = compute_ergonomics(alg)

        self.assertEqual(result.total_moves, 4)
        self.assertEqual(result.right_hand_moves, 2)  # R, R'
        self.assertEqual(result.left_hand_moves, 0)
        self.assertEqual(result.both_hand_moves, 2)  # U, U'
        # All handed moves are right
        self.assertEqual(result.hand_balance_ratio, 0.0)
        self.assertEqual(result.regrip_count, 0)  # No regrip moves
        self.assertEqual(result.flow_breaks, 0)  # No awkward transitions
        self.assertEqual(result.thumb_moves, 2)  # R, R'
        self.assertEqual(result.index_finger_moves, 2)  # U, U'
        self.assertEqual(result.middle_finger_moves, 0)
        self.assertEqual(result.ring_finger_moves, 0)
        # No awkward moves (all below threshold)
        self.assertEqual(result.awkward_moves, 0)

    def test_left_hand_equivalent(self) -> None:
        """Test ergonomics for left-hand sexy move (L' U' L U)."""
        alg = Algorithm.parse_moves("L' U' L U")
        result = compute_ergonomics(alg)

        self.assertEqual(result.total_moves, 4)
        self.assertEqual(result.right_hand_moves, 0)
        self.assertEqual(result.left_hand_moves, 2)  # L', L
        self.assertEqual(result.both_hand_moves, 2)  # U', U
        # All handed moves are left
        self.assertEqual(result.hand_balance_ratio, 0.0)
        self.assertEqual(result.regrip_count, 0)
        self.assertEqual(result.flow_breaks, 0)
        self.assertEqual(result.thumb_moves, 2)  # L', L
        self.assertEqual(result.index_finger_moves, 2)  # U', U
        self.assertEqual(result.awkward_moves, 0)

    def test_perfectly_balanced_algorithm(self) -> None:
        """Test ergonomics for perfectly balanced algorithm."""
        alg = Algorithm.parse_moves("R U R' U' L' U' L U")
        result = compute_ergonomics(alg)

        self.assertEqual(result.total_moves, 8)
        self.assertEqual(result.right_hand_moves, 2)  # R, R'
        self.assertEqual(result.left_hand_moves, 2)  # L', L
        self.assertEqual(result.both_hand_moves, 4)  # All U moves
        self.assertEqual(result.hand_balance_ratio, 0.5)  # Perfect balance
        self.assertEqual(result.regrip_count, 0)
        self.assertEqual(result.flow_breaks, 0)
        self.assertEqual(result.thumb_moves, 4)  # R, R', L', L
        self.assertEqual(result.index_finger_moves, 4)  # All U moves
        self.assertEqual(result.awkward_moves, 0)

    def test_slice_heavy_algorithm(self) -> None:
        """Test ergonomics for slice-heavy algorithm (M2 E2 S2)."""
        alg = Algorithm.parse_moves('M2 E2 S2')
        result = compute_ergonomics(alg)

        self.assertEqual(result.total_moves, 3)
        self.assertEqual(result.right_hand_moves, 0)
        self.assertEqual(result.left_hand_moves, 0)
        self.assertEqual(result.both_hand_moves, 3)  # All slice moves
        self.assertEqual(result.hand_balance_ratio, 0.5)  # No handed moves
        # E2 and S2 require regrips, M2 doesn't
        self.assertEqual(result.regrip_count, 2)
        self.assertEqual(result.flow_breaks, 0)  # No awkward transitions
        self.assertEqual(result.thumb_moves, 0)
        self.assertEqual(result.index_finger_moves, 0)
        self.assertEqual(result.middle_finger_moves, 0)
        self.assertEqual(result.ring_finger_moves, 3)  # All slice moves
        # All slice moves are above awkward threshold
        # M2=1.8, E2=1.9, S2=2.0 > 1.4
        self.assertEqual(result.awkward_moves, 3)

    def test_single_move_algorithm(self) -> None:
        """Test ergonomics for single move algorithm."""
        alg = Algorithm.parse_moves('R')
        result = compute_ergonomics(alg)

        self.assertEqual(result.total_moves, 1)
        self.assertEqual(result.right_hand_moves, 1)
        self.assertEqual(result.left_hand_moves, 0)
        self.assertEqual(result.both_hand_moves, 0)
        # All handed moves are right
        self.assertEqual(result.hand_balance_ratio, 0.0)
        self.assertEqual(result.regrip_count, 0)
        # Can't have flow breaks with one move
        self.assertEqual(result.flow_breaks, 0)
        self.assertEqual(result.thumb_moves, 1)
        self.assertEqual(result.index_finger_moves, 0)
        self.assertEqual(result.awkward_moves, 0)  # R difficulty = 1.0 < 1.4

    def test_t_perm_complex_algorithm(self) -> None:
        """Test ergonomics for T-perm (complex PLL algorithm)."""
        alg = Algorithm.parse_moves("R U R' F' R U R' U' R' F R2 U' R'")
        result = compute_ergonomics(alg)

        self.assertEqual(result.total_moves, 13)
        # Count expected hand distribution
        # R moves: R, R', R, R', R', R2, R' = 7
        # F moves: F', F = 2
        # Total right moves = 9
        # U moves: U, U, U', U' = 4 (both hand)
        # Left moves = 0

        # R moves (7) + F moves (2) = 9
        self.assertEqual(result.right_hand_moves, 9)
        self.assertEqual(result.left_hand_moves, 0)
        self.assertEqual(result.both_hand_moves, 4)  # U moves only
        # All handed moves are right
        self.assertEqual(result.hand_balance_ratio, 0.0)
        self.assertEqual(result.regrip_count, 0)  # No B, D, or slice moves

        # Check for specific expected values
        self.assertGreater(result.estimated_execution_time, 0)
        self.assertGreater(result.fingertrick_difficulty, 0)
        self.assertIsInstance(result.comfort_score, float)
        expected_ratings = ['Excellent', 'Good', 'Fair', 'Poor', 'Very Poor']
        self.assertIn(result.ergonomic_rating, expected_ratings)

    def test_algorithm_with_flow_breaks(self) -> None:
        """Test ergonomics for algorithm with awkward transitions."""
        alg = Algorithm.parse_moves('R L F B')
        result = compute_ergonomics(alg)

        self.assertEqual(result.total_moves, 4)
        self.assertEqual(result.flow_breaks, 2)  # R->L and F->B transitions
        self.assertEqual(result.right_hand_moves, 2)  # R, F
        self.assertEqual(result.left_hand_moves, 2)  # L, B
        self.assertEqual(result.hand_balance_ratio, 0.5)  # Perfect balance
        self.assertEqual(result.regrip_count, 1)  # B requires regrip

    def test_algorithm_with_pauses(self) -> None:
        """Test ergonomics calculation ignores pauses correctly."""
        alg = Algorithm.parse_moves("R . U . R'")
        result = compute_ergonomics(alg)

        self.assertEqual(result.total_moves, 3)  # Pauses not counted
        self.assertEqual(result.right_hand_moves, 2)  # R, R'
        self.assertEqual(result.both_hand_moves, 1)  # U
        self.assertEqual(result.regrip_count, 0)
        self.assertEqual(result.flow_breaks, 0)

    def test_ergonomics_data_is_namedtuple(self) -> None:
        """Test that ErgonomicsData behaves as a namedtuple."""
        alg = Algorithm.parse_moves('R U')
        result = compute_ergonomics(alg)

        # Test namedtuple properties
        self.assertIsInstance(result, ErgonomicsData)
        self.assertTrue(hasattr(result, 'total_moves'))
        self.assertTrue(hasattr(result, 'comfort_score'))
        self.assertTrue(hasattr(result, 'ergonomic_rating'))

        # Test immutability (namedtuple characteristic)
        with self.assertRaises(AttributeError):
            result.total_moves = 999  # type: ignore[misc]

    def test_all_fields_present_and_correct_types(self) -> None:
        """Test that all expected fields are present with correct types."""
        alg = Algorithm.parse_moves("R U R' U'")
        result = compute_ergonomics(alg)

        # Test integer fields
        self.assertIsInstance(result.total_moves, int)
        self.assertIsInstance(result.right_hand_moves, int)
        self.assertIsInstance(result.left_hand_moves, int)
        self.assertIsInstance(result.both_hand_moves, int)
        self.assertIsInstance(result.regrip_count, int)
        self.assertIsInstance(result.awkward_moves, int)
        self.assertIsInstance(result.flow_breaks, int)
        self.assertIsInstance(result.thumb_moves, int)
        self.assertIsInstance(result.index_finger_moves, int)
        self.assertIsInstance(result.middle_finger_moves, int)
        self.assertIsInstance(result.ring_finger_moves, int)

        # Test float fields
        self.assertIsInstance(result.hand_balance_ratio, float)
        self.assertIsInstance(result.estimated_execution_time, float)
        self.assertIsInstance(result.fingertrick_difficulty, float)
        self.assertIsInstance(result.comfort_score, float)

        # Test string field
        self.assertIsInstance(result.ergonomic_rating, str)

    def test_awkward_moves_counting(self) -> None:
        """Test that awkward moves are correctly identified and counted."""
        # Test moves above awkward threshold (1.4)
        # S=1.7, E=1.6, M2=1.8 (all > 1.4)
        alg = Algorithm.parse_moves('S E M2')
        result = compute_ergonomics(alg)
        self.assertEqual(result.awkward_moves, 3)

        # Test moves below threshold
        alg = Algorithm.parse_moves('R U F')  # R=1.0, U=1.0, F=1.2 (all < 1.4)
        result = compute_ergonomics(alg)
        self.assertEqual(result.awkward_moves, 0)

        # Test mixed
        # R=1.0 (not awkward), S=1.7 (awkward)
        alg = Algorithm.parse_moves('R S')
        result = compute_ergonomics(alg)
        self.assertEqual(result.awkward_moves, 1)
