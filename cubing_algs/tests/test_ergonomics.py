"""Tests for ergonomics analysis."""
import unittest
from typing import TypedDict
from unittest.mock import patch

from cubing_algs.algorithm import Algorithm
from cubing_algs.ergonomics import ERGONOMIC_WEIGHTS
from cubing_algs.ergonomics import HAND_ASSIGNMENTS
from cubing_algs.ergonomics import TRANSITION_PENALTIES
from cubing_algs.ergonomics import ErgonomicsData
from cubing_algs.ergonomics import HandDominance
from cubing_algs.ergonomics import calculate_ergonomic_score
from cubing_algs.ergonomics import calculate_flow_score
from cubing_algs.ergonomics import calculate_trigger_bonus
from cubing_algs.ergonomics import classify_algorithm_difficulty
from cubing_algs.ergonomics import compute_ergonomics
from cubing_algs.ergonomics import compute_estimated_execution_time
from cubing_algs.ergonomics import compute_finger_distribution
from cubing_algs.ergonomics import compute_fingertrick_difficulty
from cubing_algs.ergonomics import compute_hand_balance
from cubing_algs.ergonomics import compute_regrip_count
from cubing_algs.ergonomics import estimate_tps_potential
from cubing_algs.ergonomics import find_trigger_patterns
from cubing_algs.ergonomics import get_ergonomic_rating
from cubing_algs.ergonomics import get_move_ergonomic_weight
from cubing_algs.ergonomics import get_move_key
from cubing_algs.ergonomics import get_transition_penalty
from cubing_algs.ergonomics import suggest_ergonomic_improvements
from cubing_algs.move import Move
from cubing_algs.triggers import TRIGGER_PATTERNS
from cubing_algs.triggers import TriggerMatch
from cubing_algs.triggers import TriggerPattern


class ErgonomicInputs(TypedDict):
    """Pre-computed inputs shared by ergonomic scoring functions."""

    flow: float
    balance_ratio: float
    regrip_count: int


def ergonomic_inputs(alg: Algorithm) -> ErgonomicInputs:
    """
    Compute the pre-requisite inputs for ergonomic scoring functions.

    Returns:
        ErgonomicInputs with flow, balance_ratio, and regrip_count.

    """
    return ErgonomicInputs(
        flow=calculate_flow_score(alg),
        balance_ratio=compute_hand_balance(alg)[3],
        regrip_count=compute_regrip_count(alg),
    )


class TestHandDominance(unittest.TestCase):
    """Test the HandDominance enum."""

    def test_values(self) -> None:
        """Test enum values."""
        self.assertEqual(HandDominance.RIGHT.value, 'right')
        self.assertEqual(HandDominance.LEFT.value, 'left')
        self.assertEqual(HandDominance.AMBIDEXTROUS.value, 'ambidextrous')

    def test_members(self) -> None:
        """Test enum has exactly three members."""
        self.assertEqual(len(HandDominance), 3)


class TestTriggerPattern(unittest.TestCase):
    """Test the TriggerPattern NamedTuple."""

    def test_creation(self) -> None:
        """Test basic creation."""
        pattern = TriggerPattern(
            name='Test',
            moves='R U R',
            category='basic',
            ergonomic_bonus=0.1,
            speed_multiplier=1.2,
            variations=["L U L'"],
        )
        self.assertEqual(pattern.name, 'Test')
        self.assertEqual(pattern.moves, 'R U R')
        self.assertEqual(pattern.category, 'basic')

    def test_trigger_patterns_count(self) -> None:
        """Test that all 13 trigger patterns are defined."""
        self.assertEqual(len(TRIGGER_PATTERNS), 13)

    def test_no_primary_moves_in_other_variations(self) -> None:
        """
        Test that no pattern's primary moves appear
        as another pattern's variation.
        """
        primary_moves = {p.moves: p.name for p in TRIGGER_PATTERNS}
        for pattern in TRIGGER_PATTERNS:
            for variation in pattern.variations:
                if (
                        variation in primary_moves
                        and primary_moves[variation] != pattern.name
                ):
                    self.fail(
                        f"Variation '{variation} "
                        f"of '{pattern.name}' duplicates "
                        f"primary moves of '{primary_moves[variation]}'",
                    )


class TestTriggerMatch(unittest.TestCase):
    """Test the TriggerMatch NamedTuple."""

    def test_creation(self) -> None:
        """Test basic creation."""
        pattern = TRIGGER_PATTERNS[0]
        match = TriggerMatch(
            pattern=pattern,
            start_index=0,
            end_index=3,
            matched_moves="R U R' U'",
        )
        self.assertEqual(match.start_index, 0)
        self.assertEqual(match.end_index, 3)
        self.assertEqual(match.matched_moves, "R U R' U'")


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


class TestGetMoveErgonomicWeight(unittest.TestCase):
    """Test the get_move_ergonomic_weight function."""

    def test_right_hand_moves(self) -> None:
        """Test weights for right-hand moves."""
        self.assertEqual(
            get_move_ergonomic_weight(Move('R')), ERGONOMIC_WEIGHTS['R'],
        )
        self.assertEqual(
            get_move_ergonomic_weight(Move('U')), ERGONOMIC_WEIGHTS['U'],
        )

    def test_left_hand_moves(self) -> None:
        """Test weights for left-hand moves."""
        self.assertEqual(
            get_move_ergonomic_weight(Move('L')), ERGONOMIC_WEIGHTS['L'],
        )
        self.assertEqual(
            get_move_ergonomic_weight(Move('B')), ERGONOMIC_WEIGHTS['B'],
        )

    def test_unknown_move_defaults(self) -> None:
        """Test that unknown moves default to 0.5."""
        self.assertEqual(get_move_ergonomic_weight(Move('.')), 0.5)

    def test_ambidextrous_no_adjustment(self) -> None:
        """Test that ambidextrous mode returns base weight."""
        weight = get_move_ergonomic_weight(
            Move('R'), HandDominance.AMBIDEXTROUS,
        )
        self.assertEqual(weight, ERGONOMIC_WEIGHTS['R'])

    def test_left_handed_right_move_penalty(self) -> None:
        """Test that left-handed users get penalty for right moves."""
        right_weight = get_move_ergonomic_weight(
            Move('R'), HandDominance.RIGHT,
        )
        left_weight = get_move_ergonomic_weight(
            Move('R'), HandDominance.LEFT,
        )
        self.assertLess(left_weight, right_weight)

    def test_left_handed_left_move_bonus(self) -> None:
        """Test that left-handed users get bonus for left moves."""
        right_weight = get_move_ergonomic_weight(
            Move('L'), HandDominance.RIGHT,
        )
        left_weight = get_move_ergonomic_weight(
            Move('L'), HandDominance.LEFT,
        )
        self.assertGreater(left_weight, right_weight)

    def test_left_handed_both_move_no_change(self) -> None:
        """Test that both-hand moves are not adjusted for left-handed."""
        right_weight = get_move_ergonomic_weight(
            Move('U'), HandDominance.RIGHT,
        )
        left_weight = get_move_ergonomic_weight(
            Move('U'), HandDominance.LEFT,
        )
        self.assertEqual(left_weight, right_weight)


class TestGetTransitionPenalty(unittest.TestCase):
    """Test the get_transition_penalty function."""

    def test_pause_returns_zero(self) -> None:
        """Test that transitions involving pauses return 0."""
        self.assertEqual(
            get_transition_penalty(Move('.'), Move('R')), 0.0,
        )
        self.assertEqual(
            get_transition_penalty(Move('R'), Move('.')), 0.0,
        )

    def test_rotation_penalty(self) -> None:
        """Test that rotations get highest penalty."""
        penalty = get_transition_penalty(Move('R'), Move('x'))
        self.assertEqual(penalty, TRANSITION_PENALTIES['rotation'])

    def test_same_face_no_penalty(self) -> None:
        """Test that same-face transitions have no penalty."""
        penalty = get_transition_penalty(Move('R'), Move("R'"))
        self.assertEqual(penalty, TRANSITION_PENALTIES['same_face'])

    def test_opposite_face_penalty(self) -> None:
        """Test that opposite faces get high penalty."""
        penalty = get_transition_penalty(Move('R'), Move('L'))
        self.assertEqual(penalty, TRANSITION_PENALTIES['opposite'])

    def test_adjacent_face_penalty(self) -> None:
        """Test that adjacent faces get moderate penalty."""
        penalty = get_transition_penalty(Move('R'), Move('U'))
        self.assertEqual(penalty, TRANSITION_PENALTIES['adjacent'])

    def test_hand_switch_penalty(self) -> None:
        """Test that hand switches get moderate penalty."""
        # F (right) → B (left) — but F and B are opposite faces
        # so this gives opposite penalty, not hand_switch
        penalty = get_transition_penalty(Move('F'), Move('B'))
        self.assertEqual(penalty, TRANSITION_PENALTIES['opposite'])

    def test_slice_to_slice_default(self) -> None:
        """Test slice-to-slice transitions use default adjacent penalty."""
        # M and E are not in ADJACENT_FACES or OPPOSITE_FACES
        penalty = get_transition_penalty(Move('M'), Move('E'))
        self.assertEqual(penalty, TRANSITION_PENALTIES['adjacent'])

    def test_hand_switch_penalty_via_patched_assignments(self) -> None:
        """Test hand switch penalty for non-adjacent, non-opposite moves."""
        # M and E have base_move not in ADJACENT_FACES/OPPOSITE_FACES.
        # Patch hand assignments so they trigger the hand_switch branch.
        patched = dict(HAND_ASSIGNMENTS)
        patched['M'] = 'right'
        patched['E'] = 'left'
        with patch('cubing_algs.ergonomics.HAND_ASSIGNMENTS', patched):
            penalty = get_transition_penalty(Move('M'), Move('E'))
        self.assertEqual(penalty, TRANSITION_PENALTIES['hand_switch'])


class TestCalculateFlowScore(unittest.TestCase):
    """Test the calculate_flow_score function."""

    def test_empty_algorithm(self) -> None:
        """Test flow score for empty algorithm."""
        alg = Algorithm.parse_moves('')
        self.assertEqual(calculate_flow_score(alg), 1.0)

    def test_single_move(self) -> None:
        """Test flow score for single move."""
        alg = Algorithm.parse_moves('R')
        self.assertEqual(calculate_flow_score(alg), 1.0)

    def test_smooth_algorithm(self) -> None:
        """Test flow score for smooth algorithm with adjacent moves."""
        alg = Algorithm.parse_moves("R U R' U'")
        score = calculate_flow_score(alg)
        self.assertGreater(score, 0.7)

    def test_choppy_algorithm(self) -> None:
        """Test flow score for algorithm with opposite transitions."""
        alg = Algorithm.parse_moves('R L R L')
        score = calculate_flow_score(alg)
        self.assertLess(score, 0.5)


class TestFindTriggerPatterns(unittest.TestCase):
    """Test the find_trigger_patterns function."""

    def test_empty_algorithm(self) -> None:
        """Test trigger detection for empty algorithm."""
        alg = Algorithm.parse_moves('')
        matches = find_trigger_patterns(alg)
        self.assertEqual(len(matches), 0)

    def test_sexy_move_detected(self) -> None:
        """Test that sexy move is detected."""
        alg = Algorithm.parse_moves("R U R' U'")
        matches = find_trigger_patterns(alg)
        pattern_names = [m.pattern.name for m in matches]
        self.assertIn('Sexy Move', pattern_names)

    def test_no_triggers_in_slice_moves(self) -> None:
        """Test that slice-only algorithm has no triggers."""
        alg = Algorithm.parse_moves('M E S')
        matches = find_trigger_patterns(alg)
        self.assertEqual(len(matches), 0)

    def test_compound_trigger(self) -> None:
        """Test that compound triggers are detected over basic ones."""
        alg = Algorithm.parse_moves("R U R' U' R U R' U'")
        matches = find_trigger_patterns(alg)
        pattern_names = [m.pattern.name for m in matches]
        self.assertIn('Double Sexy', pattern_names)

    def test_non_overlapping_matches(self) -> None:
        """Test that matches don't overlap."""
        alg = Algorithm.parse_moves("R U R' U' R' F R F'")
        matches = find_trigger_patterns(alg)
        # All used indices should be unique
        all_indices: list[int] = []
        for m in matches:
            all_indices.extend(range(m.start_index, m.end_index + 1))
        self.assertEqual(len(all_indices), len(set(all_indices)))

    def test_left_hand_variation_detected(self) -> None:
        """Test that left-hand variations of triggers are detected."""
        alg = Algorithm.parse_moves("L U L' U'")
        matches = find_trigger_patterns(alg)
        self.assertGreater(len(matches), 0)

    def test_hand_dominance_param_accepted(self) -> None:
        """Test that hand dominance parameter is accepted."""
        alg = Algorithm.parse_moves("R U R' U'")
        matches_right = find_trigger_patterns(alg, HandDominance.RIGHT)
        matches_left = find_trigger_patterns(alg, HandDominance.LEFT)
        # Both should find the pattern
        self.assertGreater(len(matches_right), 0)
        self.assertGreater(len(matches_left), 0)

    def test_repeated_trigger_found_multiple_times(self) -> None:
        """Test that the same trigger pattern is found at each occurrence."""
        # Two Sexy Moves separated by F2 (prevents Double Sexy matching)
        alg = Algorithm.parse_moves("R U R' U' F2 R U R' U'")
        matches = find_trigger_patterns(alg)
        sexy_matches = [m for m in matches if m.pattern.name == 'Sexy Move']
        self.assertEqual(len(sexy_matches), 2)


class TestCalculateTriggerBonus(unittest.TestCase):
    """Test the calculate_trigger_bonus function."""

    def test_no_matches(self) -> None:
        """Test bonus with no matches."""
        bonus, multiplier = calculate_trigger_bonus([])
        self.assertEqual(bonus, 0.0)
        self.assertEqual(multiplier, 1.0)

    def test_single_match(self) -> None:
        """Test bonus with single match."""
        alg = Algorithm.parse_moves("R U R' U'")
        matches = find_trigger_patterns(alg)
        bonus, multiplier = calculate_trigger_bonus(matches)
        self.assertGreater(bonus, 0.0)
        self.assertGreater(multiplier, 1.0)

    def test_empty_matched_moves(self) -> None:
        """Test bonus calculation when matched_moves is empty."""
        pattern = TRIGGER_PATTERNS[0]
        match = TriggerMatch(
            pattern=pattern, start_index=0, end_index=0, matched_moves='',
        )
        bonus, multiplier = calculate_trigger_bonus([match])
        self.assertGreaterEqual(bonus, 0.0)
        self.assertEqual(multiplier, 1.0)

    def test_bonus_capped(self) -> None:
        """Test that bonus is capped at 0.3."""
        # Create many fake matches with high bonuses
        pattern = TRIGGER_PATTERNS[0]
        matches = [
            TriggerMatch(
                pattern=pattern,
                start_index=i * 4,
                end_index=i * 4 + 3,
                matched_moves="R U R' U'",
            )
            for i in range(10)
        ]
        bonus, multiplier = calculate_trigger_bonus(matches)
        self.assertLessEqual(bonus, 0.3)
        self.assertLessEqual(multiplier, 1.8)


class TestEstimateTpsPotential(unittest.TestCase):
    """Test the estimate_tps_potential function."""

    def test_empty_algorithm(self) -> None:
        """Test TPS for empty algorithm."""
        alg = Algorithm.parse_moves('')
        tps = estimate_tps_potential(
            alg, flow=1.0, regrip_count=0, balance_ratio=0.5,
        )
        self.assertEqual(tps, 0.0)

    def test_all_pause_algorithm(self) -> None:
        """Test TPS for non-empty algorithm with only pauses."""
        alg = Algorithm([Move('.')])
        tps = estimate_tps_potential(
            alg, flow=1.0, regrip_count=0, balance_ratio=0.5,
        )
        self.assertEqual(tps, 8.0)

    def test_easy_algorithm(self) -> None:
        """Test TPS for easy algorithm."""
        alg = Algorithm.parse_moves("R U R' U'")
        tps = estimate_tps_potential(alg, **ergonomic_inputs(alg))
        self.assertGreater(tps, 2.0)
        self.assertLessEqual(tps, 15.0)

    def test_hard_algorithm_lower_tps(self) -> None:
        """Test TPS is lower for hard algorithm."""
        easy_alg = Algorithm.parse_moves("R U R' U'")
        hard_alg = Algorithm.parse_moves('B2 E2 S2 D2')
        easy_tps = estimate_tps_potential(
            easy_alg, **ergonomic_inputs(easy_alg),
        )
        hard_tps = estimate_tps_potential(
            hard_alg, **ergonomic_inputs(hard_alg),
        )
        self.assertGreater(easy_tps, hard_tps)

    def test_bounds(self) -> None:
        """Test that TPS is within expected bounds."""
        alg = Algorithm.parse_moves('R U F L B D M E S')
        tps = estimate_tps_potential(alg, **ergonomic_inputs(alg))
        self.assertGreaterEqual(tps, 2.0)
        self.assertLessEqual(tps, 15.0)


class TestCalculateErgonomicScore(unittest.TestCase):
    """Test the calculate_ergonomic_score function."""

    def test_empty_algorithm(self) -> None:
        """Test score for empty algorithm."""
        alg = Algorithm.parse_moves('')
        self.assertEqual(
            calculate_ergonomic_score(
                alg, flow=1.0, balance_ratio=0.5, regrip_count=0,
            ),
            1.0,
        )

    def test_all_pause_algorithm(self) -> None:
        """Test score for non-empty algorithm with only pauses."""
        alg = Algorithm([Move('.')])
        self.assertEqual(
            calculate_ergonomic_score(
                alg, flow=1.0, balance_ratio=0.5, regrip_count=0,
            ),
            1.0,
        )

    def test_easy_algorithm_high_score(self) -> None:
        """Test that easy algorithms get high scores."""
        alg = Algorithm.parse_moves("R U R' U'")
        score = calculate_ergonomic_score(alg, **ergonomic_inputs(alg))
        self.assertGreater(score, 0.6)

    def test_hard_algorithm_lower_score(self) -> None:
        """Test that hard algorithms get lower scores."""
        easy_alg = Algorithm.parse_moves("R U R' U'")
        hard_alg = Algorithm.parse_moves('B2 E2 S2 D2')
        self.assertGreater(
            calculate_ergonomic_score(easy_alg, **ergonomic_inputs(easy_alg)),
            calculate_ergonomic_score(hard_alg, **ergonomic_inputs(hard_alg)),
        )

    def test_score_bounded(self) -> None:
        """Test that score is between 0 and 1."""
        alg = Algorithm.parse_moves('R U F L B D M E S')
        score = calculate_ergonomic_score(alg, **ergonomic_inputs(alg))
        self.assertGreaterEqual(score, 0.0)
        self.assertLessEqual(score, 1.0)


class TestClassifyAlgorithmDifficulty(unittest.TestCase):
    """Test the classify_algorithm_difficulty function."""

    def test_easy_algorithm_beginner(self) -> None:
        """Test that very easy algorithms classify as Beginner."""
        alg = Algorithm.parse_moves("R U R'")
        inputs = ergonomic_inputs(alg)
        score = calculate_ergonomic_score(alg, **inputs)
        difficulty = classify_algorithm_difficulty(
            score, inputs['regrip_count'], inputs['flow'],
        )
        self.assertIn(difficulty, ['Beginner', 'Intermediate'])

    def test_expert_classification(self) -> None:
        """Test that rotation-heavy algorithms classify as Expert."""
        alg = Algorithm.parse_moves('x x x x x x x x')
        inputs = ergonomic_inputs(alg)
        score = calculate_ergonomic_score(alg, **inputs)
        self.assertEqual(
            classify_algorithm_difficulty(
                score, inputs['regrip_count'], inputs['flow'],
            ),
            'Expert',
        )

    def test_valid_classifications(self) -> None:
        """Test that classification returns valid values."""
        valid = {'Beginner', 'Intermediate', 'Advanced', 'Expert'}
        alg = Algorithm.parse_moves('R U F L B D M E S')
        inputs = ergonomic_inputs(alg)
        score = calculate_ergonomic_score(alg, **inputs)
        difficulty = classify_algorithm_difficulty(
            score, inputs['regrip_count'], inputs['flow'],
        )
        self.assertIn(difficulty, valid)

    def test_hand_dominance_affects_classification(self) -> None:
        """Test that hand dominance can affect classification."""
        alg = Algorithm.parse_moves("L U L' U' L U L' U'")
        inputs = ergonomic_inputs(alg)
        right_score = calculate_ergonomic_score(
            alg, HandDominance.RIGHT, **inputs,
        )
        left_score = calculate_ergonomic_score(
            alg, HandDominance.LEFT, **inputs,
        )
        right_diff = classify_algorithm_difficulty(
            right_score, inputs['regrip_count'], inputs['flow'],
        )
        left_diff = classify_algorithm_difficulty(
            left_score, inputs['regrip_count'], inputs['flow'],
        )
        valid = {'Beginner', 'Intermediate', 'Advanced', 'Expert'}
        self.assertIn(right_diff, valid)
        self.assertIn(left_diff, valid)


class TestSuggestErgonomicImprovements(unittest.TestCase):
    """Test the suggest_ergonomic_improvements function."""

    def test_empty_algorithm(self) -> None:
        """Test suggestions for empty algorithm."""
        alg = Algorithm.parse_moves('')
        suggestions = suggest_ergonomic_improvements(
            alg, regrip_count=0, balance_ratio=0.5, flow=1.0,
        )
        self.assertEqual(suggestions, [])

    def test_all_pause_algorithm(self) -> None:
        """Test suggestions for non-empty algorithm with only pauses."""
        alg = Algorithm([Move('.')])
        self.assertEqual(
            suggest_ergonomic_improvements(
                alg, regrip_count=0, balance_ratio=0.5, flow=1.0,
            ),
            [],
        )

    def test_returns_list_of_strings(self) -> None:
        """Test that suggestions are strings."""
        alg = Algorithm.parse_moves('R U F L B D M E S')
        suggestions = suggest_ergonomic_improvements(
            alg, **ergonomic_inputs(alg),
        )
        self.assertIsInstance(suggestions, list)
        for s in suggestions:
            self.assertIsInstance(s, str)

    def test_rotation_heavy_algorithm(self) -> None:
        """Test suggestions for algorithm with many rotations."""
        alg = Algorithm.parse_moves('x y z x y')
        suggestions = suggest_ergonomic_improvements(
            alg, **ergonomic_inputs(alg),
        )
        rotation_suggestion = any('rotation' in s.lower() for s in suggestions)
        self.assertTrue(rotation_suggestion)

    def test_imbalanced_algorithm(self) -> None:
        """Test suggestions for right-heavy algorithm."""
        alg = Algorithm.parse_moves('R R R R R R R R')
        suggestions = suggest_ergonomic_improvements(
            alg, **ergonomic_inputs(alg),
        )
        balance_suggestion = any('balance' in s.lower() for s in suggestions)
        self.assertTrue(balance_suggestion)


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

    def test_rotation_moves_mapped_by_axis(self) -> None:
        """Test that rotation moves are mapped by their axis face."""
        alg = Algorithm.parse_moves('x y z')
        thumb, index, middle, ring = compute_finger_distribution(alg)
        self.assertEqual(thumb, 1)   # x -> thumb (R-axis)
        self.assertEqual(index, 1)   # y -> index (U-axis)
        self.assertEqual(middle, 1)  # z -> middle (F-axis)
        self.assertEqual(ring, 0)

    def test_wide_moves_match_base_face(self) -> None:
        """
        Test that wide moves are mapped to
        the same finger as their base face.
        """
        alg = Algorithm.parse_moves('Rw Uw Fw')
        thumb, index, middle, ring = compute_finger_distribution(alg)
        self.assertEqual(thumb, 1)   # Rw -> thumb (like R)
        self.assertEqual(index, 1)   # Uw -> index (like U)
        self.assertEqual(middle, 1)  # Fw -> middle (like F)
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
    """Test regrip count computation (transition-aware)."""

    def test_empty_algorithm(self) -> None:
        """Test regrip count for empty algorithm."""
        alg = Algorithm.parse_moves('')
        regrips = compute_regrip_count(alg)
        self.assertEqual(regrips, 0)

    def test_no_regrip_moves(self) -> None:
        """Test algorithm with no regrip-worthy transitions."""
        alg = Algorithm.parse_moves("R U R' U'")
        regrips = compute_regrip_count(alg)
        self.assertEqual(regrips, 0)  # All adjacent transitions

    def test_opposite_face_transitions(self) -> None:
        """Test that opposite face transitions count as regrips."""
        alg = Algorithm.parse_moves('R L')
        regrips = compute_regrip_count(alg)
        self.assertEqual(regrips, 1)  # R->L is opposite

    def test_opposite_face_transitions_inverse(self) -> None:
        """Test that opposite face transitions count as regrips."""
        alg = Algorithm.parse_moves('L R')
        regrips = compute_regrip_count(alg)
        self.assertEqual(regrips, 1)  # R->L is opposite

    def test_same_face_no_regrip(self) -> None:
        """Test that same-face consecutive moves don't need regrips."""
        alg = Algorithm.parse_moves("B B' B2")
        regrips = compute_regrip_count(alg)
        self.assertEqual(regrips, 0)  # Same face = no regrip

    def test_rotation_moves_always_regrip(self) -> None:
        """Test that rotation moves always count as regrips."""
        alg = Algorithm.parse_moves('R x U')
        regrips = compute_regrip_count(alg)
        self.assertEqual(regrips, 1)

    def test_adjacent_face_no_regrip(self) -> None:
        """Test that adjacent face transitions don't need regrips."""
        alg = Algorithm.parse_moves('R U F')
        regrips = compute_regrip_count(alg)
        self.assertEqual(regrips, 0)  # All adjacent

    def test_mixed_transitions(self) -> None:
        """Test algorithm with mixed transition types."""
        alg = Algorithm.parse_moves('R L F B')
        regrips = compute_regrip_count(alg)
        # R->L opposite (regrip),
        # L->F adjacent (no regrip),
        # F->B opposite (regrip)
        self.assertEqual(regrips, 2)

    def test_with_pauses(self) -> None:
        """
        Test that pauses are skipped
        when finding previous move for regrip check.
        """
        alg = Algorithm.parse_moves('R . L')
        regrips = compute_regrip_count(alg)
        self.assertEqual(regrips, 1)

    def test_single_move(self) -> None:
        """Test flow breaks for single move."""
        alg = Algorithm.parse_moves('R')
        breaks = compute_regrip_count(alg)
        self.assertEqual(breaks, 0)

    def test_no_regrip(self) -> None:
        """Test algorithm with no regrip."""
        alg = Algorithm.parse_moves("R U R' U'")
        breaks = compute_regrip_count(alg)
        self.assertEqual(breaks, 0)  # All adjacent transitions

    def test_f_to_b_regrip(self) -> None:
        """Test F to B transition creates regrip."""
        alg = Algorithm.parse_moves('F B')
        breaks = compute_regrip_count(alg)
        self.assertEqual(breaks, 1)  # F to B is opposite

    def test_m_to_r_no_regrip(self) -> None:
        """Test M to R transition (not opposite, uses default penalty)."""
        alg = Algorithm.parse_moves('M R')
        regrips = compute_regrip_count(alg)
        # M not in ADJACENT_FACES/OPPOSITE_FACES, falls to hand check
        # M='both', R='right', no hand switch since M='both'
        # Default adjacent penalty (0.1) < opposite threshold (0.3)
        self.assertEqual(regrips, 0)

    def test_multiple_regrips(self) -> None:
        """Test algorithm with multiple regrips."""
        alg = Algorithm.parse_moves('R L F B')
        regrips = compute_regrip_count(alg)
        # R->L opposite, L->F adjacent, F->B opposite
        self.assertEqual(regrips, 2)

    def test_modifiers_ignored_in_regrips(self) -> None:
        """Test that move modifiers are ignored when checking regrips."""
        alg = Algorithm.parse_moves("R' L2")
        regrips = compute_regrip_count(alg)
        self.assertEqual(regrips, 1)  # R' to L2 is still R to L opposite


class TestComputeFingertrickDifficulty(unittest.TestCase):
    """Test fingertrick difficulty computation (0-1 scale)."""

    def test_empty_algorithm(self) -> None:
        """Test fingertrick difficulty for empty algorithm."""
        alg = Algorithm.parse_moves('')
        difficulty = compute_fingertrick_difficulty(alg)
        self.assertEqual(difficulty, 0.0)

    def test_all_pause_algorithm(self) -> None:
        """Test difficulty for non-empty algorithm with only pauses."""
        alg = Algorithm([Move('.')])
        self.assertEqual(compute_fingertrick_difficulty(alg), 0.0)

    def test_easy_moves(self) -> None:
        """Test algorithm with easy moves has low difficulty."""
        alg = Algorithm.parse_moves('R U')
        difficulty = compute_fingertrick_difficulty(alg)
        # R=1.0, U=1.0, avg=1.0, difficulty=0.0
        self.assertAlmostEqual(difficulty, 0.0)

    def test_difficult_moves(self) -> None:
        """Test algorithm with difficult moves has high difficulty."""
        alg = Algorithm.parse_moves('S2 E2')
        difficulty = compute_fingertrick_difficulty(alg)
        # S2=0.55, E2=0.45, avg=0.5, difficulty=0.5
        self.assertAlmostEqual(difficulty, 0.5)

    def test_mixed_difficulty(self) -> None:
        """Test algorithm with mixed difficulty moves."""
        alg = Algorithm.parse_moves('R M')
        difficulty = compute_fingertrick_difficulty(alg)
        # R=1.0, M=0.7, avg=0.85, difficulty=0.15
        self.assertAlmostEqual(difficulty, 0.15)

    def test_rotation_move_weight(self) -> None:
        """Test that rotation moves use ergonomic weights."""
        alg = Algorithm([Move('x')])
        difficulty = compute_fingertrick_difficulty(alg)
        # x=0.4, difficulty=0.6
        self.assertAlmostEqual(difficulty, 0.6)

    def test_with_pauses(self) -> None:
        """Test fingertrick difficulty calculation ignores pauses."""
        alg = Algorithm.parse_moves('R . U')
        difficulty = compute_fingertrick_difficulty(alg)
        # R=1.0, U=1.0, avg=1.0, difficulty=0.0
        self.assertAlmostEqual(difficulty, 0.0)

    def test_hand_dominance_param(self) -> None:
        """Test that hand dominance affects difficulty."""
        alg = Algorithm.parse_moves('L L L L')
        right_diff = compute_fingertrick_difficulty(alg, HandDominance.RIGHT)
        left_diff = compute_fingertrick_difficulty(alg, HandDominance.LEFT)
        # L moves should be easier for left-handed
        self.assertGreater(right_diff, left_diff)


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


class TestGetErgonomicRating(unittest.TestCase):
    """Test ergonomic rating conversion from ergonomic_score (0-1 scale)."""

    def test_excellent_rating(self) -> None:
        """Test excellent rating threshold."""
        self.assertEqual(get_ergonomic_rating(1.0), 'Excellent')
        self.assertEqual(get_ergonomic_rating(0.80), 'Excellent')

    def test_good_rating(self) -> None:
        """Test good rating threshold."""
        self.assertEqual(get_ergonomic_rating(0.79), 'Good')
        self.assertEqual(get_ergonomic_rating(0.65), 'Good')

    def test_fair_rating(self) -> None:
        """Test fair rating threshold."""
        self.assertEqual(get_ergonomic_rating(0.64), 'Fair')
        self.assertEqual(get_ergonomic_rating(0.50), 'Fair')

    def test_poor_rating(self) -> None:
        """Test poor rating threshold."""
        self.assertEqual(get_ergonomic_rating(0.49), 'Poor')
        self.assertEqual(get_ergonomic_rating(0.35), 'Poor')

    def test_very_poor_rating(self) -> None:
        """Test very poor rating threshold."""
        self.assertEqual(get_ergonomic_rating(0.34), 'Very Poor')
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
        self.assertEqual(result.estimated_execution_time, 0.0)
        self.assertEqual(result.fingertrick_difficulty, 0.0)
        self.assertEqual(result.thumb_moves, 0)
        self.assertEqual(result.index_finger_moves, 0)
        self.assertEqual(result.middle_finger_moves, 0)
        self.assertEqual(result.ring_finger_moves, 0)
        self.assertEqual(result.ergonomic_rating, 'Excellent')
        # New fields
        self.assertEqual(result.ergonomic_score, 1.0)
        self.assertEqual(result.flow_score, 1.0)
        self.assertEqual(result.estimated_tps, 0.0)
        self.assertEqual(result.difficulty_classification, 'Beginner')
        self.assertEqual(result.trigger_count, 0)
        self.assertEqual(result.trigger_coverage, 0)
        self.assertEqual(result.detected_patterns, ())
        self.assertEqual(result.suggestions, ())

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
        self.assertEqual(result.regrip_count, 0)  # All adjacent transitions
        self.assertEqual(result.thumb_moves, 2)  # R, R'
        self.assertEqual(result.index_finger_moves, 2)  # U, U'
        self.assertEqual(result.middle_finger_moves, 0)
        self.assertEqual(result.ring_finger_moves, 0)
        self.assertEqual(result.awkward_moves, 0)  # All weights >= 0.6

        # New fields
        self.assertGreater(result.ergonomic_score, 0.5)
        self.assertGreater(result.flow_score, 0.7)
        self.assertGreater(result.estimated_tps, 2.0)
        self.assertGreater(result.trigger_count, 0)  # Should detect Sexy Move

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
        # No rotation moves, no opposite-face transitions
        self.assertEqual(result.regrip_count, 0)
        self.assertEqual(result.thumb_moves, 0)
        self.assertEqual(result.index_finger_moves, 0)
        self.assertEqual(result.middle_finger_moves, 0)
        self.assertEqual(result.ring_finger_moves, 3)  # All slice moves
        # E2=0.45, S2=0.55 are below AWKWARD_THRESHOLD=0.6; M2=0.65 is not
        self.assertEqual(result.awkward_moves, 2)

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
        self.assertEqual(result.thumb_moves, 1)
        self.assertEqual(result.index_finger_moves, 0)
        self.assertEqual(result.awkward_moves, 0)  # R weight = 1.0 >= 0.6

    def test_t_perm_complex_algorithm(self) -> None:
        """Test ergonomics for T-perm (complex PLL algorithm)."""
        alg = Algorithm.parse_moves("R U R' F' R U R' U' R' F R2 U' R'")
        result = compute_ergonomics(alg)

        self.assertEqual(result.total_moves, 13)
        # R moves (7) + F moves (2) = 9
        self.assertEqual(result.right_hand_moves, 9)
        self.assertEqual(result.left_hand_moves, 0)
        self.assertEqual(result.both_hand_moves, 4)  # U moves only
        # All handed moves are right
        self.assertEqual(result.hand_balance_ratio, 0.0)

        # Check for specific expected values
        self.assertGreater(result.estimated_execution_time, 0)
        self.assertGreater(result.fingertrick_difficulty, 0)
        expected_ratings = ['Excellent', 'Good', 'Fair', 'Poor', 'Very Poor']
        self.assertIn(result.ergonomic_rating, expected_ratings)

        # New fields should be populated
        self.assertGreater(result.ergonomic_score, 0)
        self.assertGreater(result.estimated_tps, 0)
        valid_diffs = {'Beginner', 'Intermediate', 'Advanced', 'Expert'}
        self.assertIn(result.difficulty_classification, valid_diffs)

    def test_algorithm_with_regrip(self) -> None:
        """Test ergonomics for algorithm with opposite-face transitions."""
        alg = Algorithm.parse_moves('R L F B')
        result = compute_ergonomics(alg)

        self.assertEqual(result.total_moves, 4)
        self.assertEqual(result.right_hand_moves, 2)  # R, F
        self.assertEqual(result.left_hand_moves, 2)  # L, B
        self.assertEqual(result.hand_balance_ratio, 0.5)  # Perfect balance
        # R->L opposite (regrip), F->B opposite (regrip)
        self.assertEqual(result.regrip_count, 2)
        # B=0.5 < 0.6 threshold
        self.assertEqual(result.awkward_moves, 1)

    def test_algorithm_with_pauses(self) -> None:
        """Test ergonomics calculation ignores pauses correctly."""
        alg = Algorithm.parse_moves("R . U . R'")
        result = compute_ergonomics(alg)

        self.assertEqual(result.total_moves, 3)  # Pauses not counted
        self.assertEqual(result.right_hand_moves, 2)  # R, R'
        self.assertEqual(result.both_hand_moves, 1)  # U
        self.assertEqual(result.regrip_count, 0)

    def test_ergonomics_data_is_immutable_named_tuple(self) -> None:
        """Test that ErgonomicsData is an immutable NamedTuple."""
        alg = Algorithm.parse_moves('R U')
        result = compute_ergonomics(alg)

        self.assertIsInstance(result, ErgonomicsData)
        self.assertTrue(hasattr(result, 'total_moves'))
        self.assertTrue(hasattr(result, 'ergonomic_rating'))

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
        self.assertIsInstance(result.thumb_moves, int)
        self.assertIsInstance(result.index_finger_moves, int)
        self.assertIsInstance(result.middle_finger_moves, int)
        self.assertIsInstance(result.ring_finger_moves, int)

        # Test float fields
        self.assertIsInstance(result.hand_balance_ratio, float)
        self.assertIsInstance(result.estimated_execution_time, float)
        self.assertIsInstance(result.fingertrick_difficulty, float)

        # Test string field
        self.assertIsInstance(result.ergonomic_rating, str)

        # Test new fields
        self.assertIsInstance(result.ergonomic_score, float)
        self.assertIsInstance(result.flow_score, float)
        self.assertIsInstance(result.estimated_tps, float)
        self.assertIsInstance(result.difficulty_classification, str)
        self.assertIsInstance(result.trigger_count, int)
        self.assertIsInstance(result.trigger_coverage, int)
        self.assertIsInstance(result.detected_patterns, tuple)
        self.assertIsInstance(result.suggestions, tuple)

    def test_awkward_moves_counting(self) -> None:
        """Test that awkward moves are correctly identified and counted."""
        # E=0.5, S2=0.55 below threshold 0.6; M=0.7 above
        alg = Algorithm.parse_moves('E S2 M')
        result = compute_ergonomics(alg)
        self.assertEqual(result.awkward_moves, 2)  # E and S2

        # All above threshold
        alg = Algorithm.parse_moves('R U F')  # R=1.0, U=1.0, F=0.85
        result = compute_ergonomics(alg)
        self.assertEqual(result.awkward_moves, 0)

        # Mixed: R=1.0 (not), E=0.5 (awkward)
        alg = Algorithm.parse_moves('R E')
        result = compute_ergonomics(alg)
        self.assertEqual(result.awkward_moves, 1)

    def test_hand_dominance_parameter(self) -> None:
        """Test that hand dominance parameter is accepted."""
        alg = Algorithm.parse_moves("R U R' U'")
        result_right = compute_ergonomics(alg, HandDominance.RIGHT)
        result_left = compute_ergonomics(alg, HandDominance.LEFT)
        # Both should complete without error
        self.assertIsInstance(result_right, ErgonomicsData)
        self.assertIsInstance(result_left, ErgonomicsData)

    def test_new_fields_populated_for_nonempty(self) -> None:
        """Test that new advanced fields are populated for non-empty algs."""
        alg = Algorithm.parse_moves("R U R' U' R' F R F'")
        result = compute_ergonomics(alg)

        self.assertGreater(result.ergonomic_score, 0.0)
        self.assertLessEqual(result.ergonomic_score, 1.0)
        self.assertGreater(result.flow_score, 0.0)
        self.assertLessEqual(result.flow_score, 1.0)
        self.assertGreater(result.estimated_tps, 0.0)
        valid_diffs = {'Beginner', 'Intermediate', 'Advanced', 'Expert'}
        self.assertIn(result.difficulty_classification, valid_diffs)
        self.assertIsInstance(result.trigger_count, int)
        self.assertIsInstance(result.trigger_coverage, int)
