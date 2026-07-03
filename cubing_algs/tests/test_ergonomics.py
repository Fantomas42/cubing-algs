"""Tests for ergonomics analysis."""
import unittest
from typing import TypedDict
from unittest.mock import patch

from cubing_algs.algorithm import Algorithm
from cubing_algs.ergonomics import AWKWARD_THRESHOLD
from cubing_algs.ergonomics import BASE_MOVE_TIME
from cubing_algs.ergonomics import MOVE_DATA
from cubing_algs.ergonomics import PAUSE_TIME
from cubing_algs.ergonomics import REGRIP_TIME_PENALTY
from cubing_algs.ergonomics import TRANSITION_PENALTIES
from cubing_algs.ergonomics import VARIATION_FACTORS
from cubing_algs.ergonomics import WEIGHT_THRESHOLD
from cubing_algs.ergonomics import ErgonomicScoreInputs
from cubing_algs.ergonomics import ErgonomicsData
from cubing_algs.ergonomics import FingerAssignment
from cubing_algs.ergonomics import HandDominance
from cubing_algs.ergonomics import MoveProperties
from cubing_algs.ergonomics import calculate_ergonomic_score
from cubing_algs.ergonomics import calculate_flow_score
from cubing_algs.ergonomics import calculate_trigger_score
from cubing_algs.ergonomics import classify_algorithm_difficulty
from cubing_algs.ergonomics import compute_ergonomics
from cubing_algs.ergonomics import compute_estimated_execution_time
from cubing_algs.ergonomics import compute_finger_distribution
from cubing_algs.ergonomics import compute_fingertrick_comfort
from cubing_algs.ergonomics import compute_hand_balance
from cubing_algs.ergonomics import compute_move_execution_time
from cubing_algs.ergonomics import compute_regrip_count
from cubing_algs.ergonomics import find_trigger_patterns
from cubing_algs.ergonomics import get_ergonomic_rating
from cubing_algs.ergonomics import get_move_ergonomic_weight
from cubing_algs.ergonomics import get_move_key
from cubing_algs.ergonomics import get_transition_penalty
from cubing_algs.ergonomics import mirror_move_key
from cubing_algs.ergonomics import normalize_algorithm_string
from cubing_algs.ergonomics import suggest_ergonomic_improvements
from cubing_algs.ergonomics import trigger_speed_factor
from cubing_algs.move import Move
from cubing_algs.triggers import TRIGGER_PATTERNS
from cubing_algs.triggers import TriggerMatch
from cubing_algs.triggers import VariationKind


class SuggestionInputs(TypedDict):
    """Pre-computed inputs for suggest_ergonomic_improvements."""

    flow: float
    balance_ratio: float
    regrip_count: int
    fingertrick_comfort: float


def suggestion_inputs(
    alg: Algorithm,
    hand_dominance: HandDominance = HandDominance.RIGHT,
) -> SuggestionInputs:
    """
    Compute the pre-requisite inputs for improvement suggestions.

    Returns:
        SuggestionInputs with flow, balance_ratio, regrip_count
        and fingertrick_comfort.

    """
    return SuggestionInputs(
        flow=calculate_flow_score(alg),
        balance_ratio=compute_hand_balance(alg)[3],
        regrip_count=compute_regrip_count(alg),
        fingertrick_comfort=compute_fingertrick_comfort(alg, hand_dominance),
    )


def score_inputs(
    alg: Algorithm,
    hand_dominance: HandDominance = HandDominance.RIGHT,
) -> ErgonomicScoreInputs:
    """
    Compute the pre-requisite inputs for calculate_ergonomic_score.

    Returns:
        ErgonomicScoreInputs with comfort, flow, balance, regrip
        and trigger metrics.

    """
    total_moves = sum(1 for move in alg if not move.is_pause)
    return ErgonomicScoreInputs(
        total_moves=total_moves,
        trigger_score=calculate_trigger_score(
            find_trigger_patterns(alg, hand_dominance), total_moves,
        ),
        **suggestion_inputs(alg, hand_dominance),
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


class TestFingerAssignment(unittest.TestCase):
    """Test the FingerAssignment enum."""

    def test_values(self) -> None:
        """Test enum values."""
        self.assertEqual(FingerAssignment.MIXED.value, 'mixed')
        self.assertEqual(FingerAssignment.THUMB.value, 'thumb')
        self.assertEqual(FingerAssignment.INDEX.value, 'index')
        self.assertEqual(FingerAssignment.MIDDLE.value, 'middle')
        self.assertEqual(FingerAssignment.RING.value, 'ring')
        self.assertEqual(FingerAssignment.PINKY.value, 'pinky')

    def test_members(self) -> None:
        """Test enum has exactly six members."""
        self.assertEqual(len(FingerAssignment), 6)


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
            get_move_ergonomic_weight(Move('R')), MOVE_DATA['R'].weight,
        )
        self.assertEqual(
            get_move_ergonomic_weight(Move('U')), MOVE_DATA['U'].weight,
        )

    def test_left_hand_moves(self) -> None:
        """Test weights for left-hand moves."""
        self.assertEqual(
            get_move_ergonomic_weight(Move('L')), MOVE_DATA['L'].weight,
        )
        self.assertEqual(
            get_move_ergonomic_weight(Move('B')), MOVE_DATA['B'].weight,
        )

    def test_unknown_move_defaults(self) -> None:
        """Test that unknown moves default to 0.5."""
        self.assertEqual(get_move_ergonomic_weight(Move('.')), 0.5)

    def test_ambidextrous_no_adjustment(self) -> None:
        """Test that ambidextrous mode returns base weight."""
        weight = get_move_ergonomic_weight(
            Move('R'), HandDominance.AMBIDEXTROUS,
        )
        self.assertEqual(weight, MOVE_DATA['R'].weight)

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
            Move('B'), HandDominance.RIGHT,
        )
        left_weight = get_move_ergonomic_weight(
            Move('B'), HandDominance.LEFT,
        )
        self.assertGreater(left_weight, right_weight)

    def test_left_handed_both_move_no_change(self) -> None:
        """Test that both-hand moves are not adjusted for left-handed."""
        right_weight = get_move_ergonomic_weight(
            Move('U2'), HandDominance.RIGHT,
        )
        left_weight = get_move_ergonomic_weight(
            Move('U2'), HandDominance.LEFT,
        )
        self.assertEqual(left_weight, right_weight)

    def test_left_weight_is_mirrored_table_lookup(self) -> None:
        """Test that LEFT weights come from the mirrored move entry."""
        expectations = (
            ('R', "L'"),
            ("R'", 'L'),
            ('R2', 'L2'),
            ('L', "R'"),
            ('U', "U'"),
            ("U'", 'U'),
            ('Rw', "Lw'"),
            ('Lw2', 'Rw2'),
            ('M', "M'"),
            ('E2', 'E2'),
            ('S', "S'"),
            ('x', 'x'),
            ("y'", "y'"),
            ('z2', 'z2'),
        )
        for move_key, mirrored_key in expectations:
            with self.subTest(move=move_key, mirror=mirrored_key):
                self.assertEqual(
                    get_move_ergonomic_weight(
                        Move(move_key), HandDominance.LEFT,
                    ),
                    MOVE_DATA[mirrored_key].weight,
                )

    def test_left_weight_mirror_property(self) -> None:
        """Test weight(m, LEFT) == weight(mirror(m), RIGHT) for all moves."""
        for move_key in MOVE_DATA:
            with self.subTest(move=move_key):
                mirrored_key = mirror_move_key(move_key)
                self.assertEqual(
                    get_move_ergonomic_weight(
                        Move(move_key), HandDominance.LEFT,
                    ),
                    get_move_ergonomic_weight(
                        Move(mirrored_key), HandDominance.RIGHT,
                    ),
                )


class TestMirrorMoveKey(unittest.TestCase):
    """Test the mirror_move_key helper."""

    def test_mirror_is_an_involution(self) -> None:
        """Test that mirroring twice returns the original key."""
        for move_key in MOVE_DATA:
            with self.subTest(move=move_key):
                self.assertEqual(
                    mirror_move_key(mirror_move_key(move_key)), move_key,
                )

    def test_mirror_covers_move_data(self) -> None:
        """Test that every mirrored key is still a MOVE_DATA entry."""
        for move_key in MOVE_DATA:
            with self.subTest(move=move_key):
                self.assertIn(mirror_move_key(move_key), MOVE_DATA)

    def test_mirror_keeps_pauses_unchanged(self) -> None:
        """Test that pauses are left unchanged by the mirror."""
        self.assertEqual(mirror_move_key('.'), '.')


class TestMoveDataCalibration(unittest.TestCase):
    """Test the calibration of the MOVE_DATA weight table."""

    ISSUE_B_BASED = (
        "U' B R D' L' U L' U' U U L U F' U F U' B' U B U' U' U' L' U L "
        "L U L' U' U B' U' U' B U' B U U B' U U B U' B' U B' U B U' U' "
        "B' U B B L U L' U' B' F U R U' R' F' U U' U'"
    )
    ISSUE_R_BASED = (
        "U' R F D' B' U B' U' U U B U L' U L U' R' U R U' U' U' B' U B "
        "B U B' U' U R' U' U' R U' R U U R' U U R U' R' U R' U R U' U' "
        "R' U R R B U B' U' R' L U F U' F' L' U U' U'"
    )

    def test_back_face_below_right_face(self) -> None:
        """Test that B moves are rated below their R counterparts."""
        for b_key, r_key in (('B', 'R'), ("B'", "R'"), ('B2', 'R2')):
            with self.subTest(b_key=b_key, r_key=r_key):
                self.assertLess(
                    MOVE_DATA[b_key].weight, MOVE_DATA[r_key].weight,
                )

    def test_left_face_above_back_face(self) -> None:
        """Test that L moves are rated above their B counterparts."""
        for l_key, b_key in (('L', 'B'), ("L'", "B'"), ('L2', 'B2')):
            with self.subTest(l_key=l_key, b_key=b_key):
                self.assertGreater(
                    MOVE_DATA[l_key].weight, MOVE_DATA[b_key].weight,
                )

    def test_home_grip_faces_in_top_band(self) -> None:
        """Test that R/U/F quarter turns sit in the top band."""
        for key in ('R', "R'", 'U', "U'", 'F', "F'"):
            with self.subTest(key=key):
                self.assertGreaterEqual(MOVE_DATA[key].weight, 0.85)

    def test_b_d_faces_in_low_band(self) -> None:
        """Test that B/D moves sit clearly lower and count as awkward."""
        for face in ('B', 'D'):
            for suffix in ('', "'", '2'):
                key = face + suffix
                with self.subTest(key=key):
                    self.assertGreaterEqual(MOVE_DATA[key].weight, 0.4)
                    self.assertLess(
                        MOVE_DATA[key].weight, AWKWARD_THRESHOLD,
                    )

    def test_slices_and_rotations_below_b_d(self) -> None:
        """Test that slices and rotations sit below the B/D band."""
        b_d_floor = min(
            MOVE_DATA[face + suffix].weight
            for face in ('B', 'D')
            for suffix in ('', "'", '2')
        )
        slice_and_rotation_keys = [
            key for key in MOVE_DATA
            if key[0] in 'MESxyz'
        ]
        for key in slice_and_rotation_keys:
            with self.subTest(key=key):
                self.assertLess(MOVE_DATA[key].weight, b_d_floor)

    def test_awkward_moves_reflect_b_d_moves(self) -> None:
        """Test that B/D-heavy algorithms report their awkward moves."""
        b_based = compute_ergonomics(Algorithm.parse_moves(self.ISSUE_B_BASED))
        r_based = compute_ergonomics(Algorithm.parse_moves(self.ISSUE_R_BASED))

        self.assertEqual(b_based.awkward_moves, 16)
        self.assertEqual(r_based.awkward_moves, 10)

    def test_average_weight_r_based_above_b_based(self) -> None:
        """Test that the R-based algorithm has better move weights."""
        b_based = Algorithm.parse_moves(self.ISSUE_B_BASED)
        r_based = Algorithm.parse_moves(self.ISSUE_R_BASED)

        def average_weight(algorithm: Algorithm) -> float:
            weights = [
                get_move_ergonomic_weight(move)
                for move in algorithm
            ]
            return sum(weights) / len(weights)

        self.assertGreater(
            average_weight(r_based), average_weight(b_based),
        )


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

    def test_hand_switch_beats_adjacency(self) -> None:
        """Test that switching hands on adjacent faces costs hand_switch."""
        # R (right) → F' (left): adjacent faces but different hands
        penalty = get_transition_penalty(Move('R'), Move("F'"))
        self.assertEqual(penalty, TRANSITION_PENALTIES['hand_switch'])

    def test_same_hand_adjacent_faces(self) -> None:
        """Test that same-hand adjacent transitions cost adjacent."""
        # R (right) → F (right): adjacent faces, same hand
        penalty = get_transition_penalty(Move('R'), Move('F'))
        self.assertEqual(penalty, TRANSITION_PENALTIES['adjacent'])

    def test_ambidextrous_adjacent_no_hand_switch(self) -> None:
        """Test that ambidextrous moves never count as hand switches."""
        # R (right) → U2 (ambidextrous): adjacent faces
        penalty = get_transition_penalty(Move('R'), Move('U2'))
        self.assertEqual(penalty, TRANSITION_PENALTIES['adjacent'])

    def test_slice_to_slice_default(self) -> None:
        """Test slice-to-slice transitions use default adjacent penalty."""
        # M and S are not in ADJACENT_FACES or OPPOSITE_FACES, same hand
        penalty = get_transition_penalty(Move('M'), Move('S'))
        self.assertEqual(penalty, TRANSITION_PENALTIES['adjacent'])

    def test_hand_switch_penalty_via_patched_assignments(self) -> None:
        """Test hand switch penalty for non-adjacent, non-opposite moves."""
        # M and E have base_move not in ADJACENT_FACES/OPPOSITE_FACES.
        # Patch hand assignments so they trigger the hand_switch branch.
        patched = dict(MOVE_DATA)
        patched['M'] = MoveProperties(
            HandDominance.RIGHT, MOVE_DATA['M'].finger, MOVE_DATA['M'].weight)
        patched['E'] = MoveProperties(
            HandDominance.LEFT, MOVE_DATA['E'].finger, MOVE_DATA['E'].weight)
        with patch('cubing_algs.ergonomics.MOVE_DATA', patched):
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
        self.assertGreater(score, 0.55)

    def test_pauses_are_transparent_for_flow(self) -> None:
        """Test that inserting pauses does not change the flow score."""
        without_pauses = Algorithm.parse_moves('R B L D R B')
        with_pauses = Algorithm.parse_moves('R . B . L . D . R . B')
        self.assertLess(calculate_flow_score(without_pauses), 1.0)
        self.assertEqual(
            calculate_flow_score(with_pauses),
            calculate_flow_score(without_pauses),
        )

    def test_normalized_on_effective_penalty_range(self) -> None:
        """Test that flow is normalized by the opposite-face penalty."""
        # All transitions adjacent: avg penalty 0.1 out of a 0.3 ceiling
        alg = Algorithm.parse_moves('R U R U')
        expected = 1.0 - (
            TRANSITION_PENALTIES['adjacent']
            / TRANSITION_PENALTIES['opposite']
        )
        self.assertAlmostEqual(calculate_flow_score(alg), expected)

    def test_choppy_algorithm(self) -> None:
        """Test flow score for algorithm with opposite transitions."""
        alg = Algorithm.parse_moves('R L R L')
        score = calculate_flow_score(alg)
        self.assertLess(score, 0.5)

    def test_opposite_transitions_exhaust_flow(self) -> None:
        """Test that opposite-only transitions bottom out the flow."""
        alg = Algorithm.parse_moves('R L R L')
        self.assertAlmostEqual(calculate_flow_score(alg), 0.0)


class TestNormalizeAlgorithmString(unittest.TestCase):
    """Test the normalize_algorithm_string function."""

    def test_standard_notation_unchanged(self) -> None:
        """Test that standard notation is preserved."""
        alg = Algorithm.parse_moves("R U R' U'")
        self.assertEqual(normalize_algorithm_string(alg), "R U R' U'")

    def test_sign_notation_converted_to_standard(self) -> None:
        """Test that SiGN wide moves are converted to standard notation."""
        alg = Algorithm.parse_moves("r U r' U'")
        self.assertEqual(normalize_algorithm_string(alg), "Rw U Rw' U'")

    def test_pauses_removed(self) -> None:
        """Test that pauses are removed from the normalized string."""
        alg = Algorithm.parse_moves('R . U .')
        self.assertEqual(normalize_algorithm_string(alg), 'R U')


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

    def test_wide_trigger_detected_in_sign_notation(self) -> None:
        """Test that wide triggers are detected on SiGN-written algorithms."""
        alg = Algorithm.parse_moves("r U r' U'")
        pattern_names = [m.pattern.name for m in find_trigger_patterns(alg)]
        self.assertIn('Wide Sexy', pattern_names)

    def test_wide_trigger_detected_in_standard_notation(self) -> None:
        """Test that wide triggers are detected on standard-written algos."""
        alg = Algorithm.parse_moves("Rw U Rw' U'")
        pattern_names = [m.pattern.name for m in find_trigger_patterns(alg)]
        self.assertIn('Wide Sexy', pattern_names)

    def test_repeated_trigger_found_multiple_times(self) -> None:
        """Test that the same trigger pattern is found at each occurrence."""
        # Two Sexy Moves separated by F2 (prevents Double Sexy matching)
        alg = Algorithm.parse_moves("R U R' U' F2 R U R' U'")
        matches = find_trigger_patterns(alg)
        sexy_matches = [m for m in matches if m.pattern.name == 'Sexy Move']
        self.assertEqual(len(sexy_matches), 2)


class TestCalculateTriggerScore(unittest.TestCase):
    """Test the calculate_trigger_score function."""

    def test_no_matches(self) -> None:
        """Test score with no matches."""
        self.assertEqual(calculate_trigger_score([], 4), 0.0)

    def test_no_moves(self) -> None:
        """Test score with no moves."""
        self.assertEqual(calculate_trigger_score([], 0), 0.0)

    def test_full_coverage_best_trigger(self) -> None:
        """Test that full coverage by the best trigger scores 1.0."""
        alg = Algorithm.parse_moves("R U R' U'")
        matches = find_trigger_patterns(alg)
        self.assertAlmostEqual(calculate_trigger_score(matches, 4), 1.0)

    def test_partial_coverage_scores_lower(self) -> None:
        """Test that uncovered moves dilute the score."""
        alg = Algorithm.parse_moves("R U R' U'")
        matches = find_trigger_patterns(alg)
        full = calculate_trigger_score(matches, 4)
        diluted = calculate_trigger_score(matches, 8)
        self.assertAlmostEqual(diluted, full / 2)

    def test_quality_weighted_by_pattern_bonus(self) -> None:
        """Test that low-bonus triggers contribute less than high-bonus."""
        sexy_alg = Algorithm.parse_moves("R U R' U'")
        sledge_alg = Algorithm.parse_moves("R' F R F'")
        sexy_score = calculate_trigger_score(
            find_trigger_patterns(sexy_alg), 4,
        )
        sledge_score = calculate_trigger_score(
            find_trigger_patterns(sledge_alg), 4,
        )
        self.assertLess(sledge_score, sexy_score)

    def test_canonical_match_has_no_variation(self) -> None:
        """Test that a canonical match carries no variation."""
        alg = Algorithm.parse_moves("R U R' U'")
        matches = find_trigger_patterns(alg)
        sexy = next(m for m in matches if m.pattern.name == 'Sexy Move')
        self.assertIsNone(sexy.variation)

    def test_inverse_variation_gets_inverse_factor(self) -> None:
        """Test that right-hand inverse variations avoid the back penalty."""
        alg = Algorithm.parse_moves("R' U' R U")
        matches = find_trigger_patterns(alg)
        sexy = next(m for m in matches if m.pattern.name == 'Sexy Move')
        if sexy.variation is None:
            self.fail('Inverse Sexy Move match should carry a variation')
        self.assertEqual(sexy.variation.kind, VariationKind.INVERSE)
        canonical = calculate_trigger_score(
            find_trigger_patterns(Algorithm.parse_moves("R U R' U'")), 4,
        )
        self.assertAlmostEqual(
            calculate_trigger_score([sexy], 4),
            canonical * VARIATION_FACTORS[VariationKind.INVERSE],
        )

    def test_back_variation_gets_back_factor(self) -> None:
        """Test that back-face variations get the back penalty."""
        alg = Algorithm.parse_moves("R B' R' B")
        matches = find_trigger_patterns(alg)
        sledge = next(
            m for m in matches if m.pattern.name == 'Sledgehammer'
        )
        if sledge.variation is None:
            self.fail('Back Sledgehammer match should carry a variation')
        self.assertEqual(sledge.variation.kind, VariationKind.BACK)
        expected_factor = 1.0 + (
            (sledge.pattern.speed_multiplier - 1.0)
            / VARIATION_FACTORS[VariationKind.BACK]
        )
        self.assertAlmostEqual(trigger_speed_factor(sledge), expected_factor)

    def test_lefty_variation_gets_lefty_factor(self) -> None:
        """Test that lefty variations get the lefty factor."""
        alg = Algorithm.parse_moves("L' U' L U")
        matches = find_trigger_patterns(alg)
        sexy = next(m for m in matches if m.pattern.name == 'Sexy Move')
        if sexy.variation is None:
            self.fail('Lefty Sexy Move match should carry a variation')
        self.assertEqual(sexy.variation.kind, VariationKind.LEFTY)
        canonical = calculate_trigger_score(
            find_trigger_patterns(Algorithm.parse_moves("R U R' U'")), 4,
        )
        self.assertAlmostEqual(
            calculate_trigger_score([sexy], 4),
            canonical * VARIATION_FACTORS[VariationKind.LEFTY],
        )

    def test_score_bounded(self) -> None:
        """Test that score never exceeds 1.0."""
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
        self.assertLessEqual(calculate_trigger_score(matches, 4), 1.0)


class TestTriggerSpeedFactor(unittest.TestCase):
    """Test the trigger_speed_factor function."""

    def test_canonical_match_uses_pattern_multiplier(self) -> None:
        """Test that a canonical match keeps the pattern multiplier."""
        alg = Algorithm.parse_moves("R U R' U'")
        matches = find_trigger_patterns(alg)
        sexy = next(m for m in matches if m.pattern.name == 'Sexy Move')
        self.assertEqual(
            trigger_speed_factor(sexy), sexy.pattern.speed_multiplier,
        )

    def test_variation_pulls_multiplier_toward_one(self) -> None:
        """Test that variations reduce the distance to a neutral factor."""
        alg = Algorithm.parse_moves("L' U' L U")
        matches = find_trigger_patterns(alg)
        sexy = next(m for m in matches if m.pattern.name == 'Sexy Move')
        self.assertLess(
            trigger_speed_factor(sexy), sexy.pattern.speed_multiplier,
        )
        self.assertGreater(trigger_speed_factor(sexy), 1.0)

    def test_degraded_variation_never_faster_than_canonical(self) -> None:
        """Test that variations of slow triggers stay below canonical."""
        canonical = find_trigger_patterns(
            Algorithm.parse_moves("F R' F' R"),
        )
        back = find_trigger_patterns(
            Algorithm.parse_moves("B' R B R'"),
        )
        canonical_hedge = next(
            m for m in canonical if m.pattern.name == 'Hedgeslammer'
        )
        back_hedge = next(
            m for m in back if m.pattern.name == 'Hedgeslammer'
        )
        self.assertLess(back_hedge.pattern.speed_multiplier, 1.0)
        self.assertLess(
            trigger_speed_factor(back_hedge),
            trigger_speed_factor(canonical_hedge),
        )


class TestCalculateErgonomicScore(unittest.TestCase):
    """Test the calculate_ergonomic_score function."""

    def test_empty_algorithm(self) -> None:
        """Test score for empty algorithm."""
        alg = Algorithm.parse_moves('')
        self.assertEqual(
            calculate_ergonomic_score(score_inputs(alg)),
            1.0,
        )

    def test_all_pause_algorithm(self) -> None:
        """Test score for non-empty algorithm with only pauses."""
        alg = Algorithm([Move('.')])
        self.assertEqual(
            calculate_ergonomic_score(score_inputs(alg)),
            1.0,
        )

    def test_easy_algorithm_high_score(self) -> None:
        """Test that easy algorithms get high scores."""
        alg = Algorithm.parse_moves("R U R' U'")
        score = calculate_ergonomic_score(score_inputs(alg))
        self.assertGreater(score, 0.6)

    def test_hard_algorithm_lower_score(self) -> None:
        """Test that hard algorithms get lower scores."""
        easy_alg = Algorithm.parse_moves("R U R' U'")
        hard_alg = Algorithm.parse_moves('B2 E2 S2 D2')
        self.assertGreater(
            calculate_ergonomic_score(score_inputs(easy_alg)),
            calculate_ergonomic_score(score_inputs(hard_alg)),
        )

    def test_score_bounded(self) -> None:
        """Test that score is between 0 and 1."""
        alg = Algorithm.parse_moves('R U F L B D M E S')
        score = calculate_ergonomic_score(score_inputs(alg))
        self.assertGreaterEqual(score, 0.0)
        self.assertLessEqual(score, 1.0)


class TestErgonomicScoreDesaturation(unittest.TestCase):
    """
    Acceptance criteria for the desaturated ergonomic score (phase 2.4).

    Four F2L-style algorithms differing only by their base face must get
    four distinct, non-saturated scores ordered sensibly, while clean
    OLL algorithms stay high and B/D/E-based ones stay low.
    """

    F_BASED = (
        "U' F L D' R' U R' U' U U R U B' U B U' F' U F U' U' U' R' U R "
        "R U R' U' U F' U' U' F U' F U U F' U U F U' F' U F' U F U' U' "
        "F' U F F R U R' U' F' B U L U' L' B' U U' U'"
    )
    L_BASED = (
        "U' L B D' F' U F' U' U U F U R' U R U' L' U L U' U' U' F' U F "
        "F U F' U' U L' U' U' L U' L U U L' U U L U' L' U L' U L U' U' "
        "L' U L L F U F' U' L' R U B U' B' R' U U' U'"
    )
    B_BASED = (
        "U' B R D' L' U L' U' U U L U F' U F U' B' U B U' U' U' L' U L "
        "L U L' U' U B' U' U' B U' B U U B' U U B U' B' U B' U B U' U' "
        "B' U B B L U L' U' B' F U R U' R' F' U U' U'"
    )
    R_BASED = (
        "U' R F D' B' U B' U' U U B U L' U L U' R' U R U' U' U' B' U B "
        "B U B' U' U R' U' U' R U' R U U R' U U R U' R' U R' U R U' U' "
        "R' U R R B U B' U' R' L U F U' F' L' U U' U'"
    )

    def scores(self) -> dict[str, float]:
        """
        Compute the ergonomic scores of the four reference algorithms.

        Returns:
            Mapping of base-face label to ergonomic score.

        """
        return {
            name: compute_ergonomics(
                Algorithm.parse_moves(moves),
            ).ergonomic_score
            for name, moves in [
                ('F', self.F_BASED),
                ('L', self.L_BASED),
                ('B', self.B_BASED),
                ('R', self.R_BASED),
            ]
        }

    def test_four_distinct_scores(self) -> None:
        """Test that the four reference algorithms get distinct scores."""
        scores = self.scores()
        self.assertEqual(len(set(scores.values())), 4)

    def test_no_saturation(self) -> None:
        """Test that no reference algorithm saturates the scale."""
        for name, score in self.scores().items():
            with self.subTest(base=name):
                self.assertLess(score, 0.85)

    def test_r_based_beats_b_based(self) -> None:
        """Test that the R-based variant outscores the B-based one."""
        scores = self.scores()
        self.assertGreater(scores['R'], scores['B'])

    def test_clean_oll_stays_high(self) -> None:
        """Test that a clean R/U algorithm like Sune scores above 0.8."""
        sune = Algorithm.parse_moves("R U R' U R U2 R'")
        self.assertGreater(compute_ergonomics(sune).ergonomic_score, 0.8)

    def test_awkward_faces_score_low(self) -> None:
        """Test that a B/D/E-based algorithm scores below 0.5."""
        awkward = Algorithm.parse_moves('B2 E2 S2 D2')
        self.assertLess(compute_ergonomics(awkward).ergonomic_score, 0.5)


class TestClassifyAlgorithmDifficulty(unittest.TestCase):
    """Test the classify_algorithm_difficulty function."""

    def test_beginner_classification(self) -> None:
        """Test that a comfortable, flowing algorithm is Beginner."""
        alg = Algorithm.parse_moves("U U'")
        inputs = score_inputs(alg)
        score = calculate_ergonomic_score(inputs)
        self.assertEqual(
            classify_algorithm_difficulty(
                score, inputs.regrip_count, inputs.flow,
            ),
            'Beginner',
        )

    def test_easy_algorithm_beginner(self) -> None:
        """Test that very easy algorithms classify as Beginner."""
        alg = Algorithm.parse_moves("R U R'")
        inputs = score_inputs(alg)
        score = calculate_ergonomic_score(inputs)
        difficulty = classify_algorithm_difficulty(
            score, inputs.regrip_count, inputs.flow,
        )
        self.assertIn(difficulty, ['Beginner', 'Intermediate'])

    def test_expert_classification(self) -> None:
        """Test that rotation-heavy algorithms classify as Expert."""
        alg = Algorithm.parse_moves('x x x x x x x x')
        inputs = score_inputs(alg)
        score = calculate_ergonomic_score(inputs)
        self.assertEqual(
            classify_algorithm_difficulty(
                score, inputs.regrip_count, inputs.flow,
            ),
            'Expert',
        )

    def test_valid_classifications(self) -> None:
        """Test that classification returns valid values."""
        valid = {'Beginner', 'Intermediate', 'Advanced', 'Expert'}
        alg = Algorithm.parse_moves('R U F L B D M E S')
        inputs = score_inputs(alg)
        score = calculate_ergonomic_score(inputs)
        difficulty = classify_algorithm_difficulty(
            score, inputs.regrip_count, inputs.flow,
        )
        self.assertIn(difficulty, valid)

    def test_hand_dominance_affects_classification(self) -> None:
        """Test that hand dominance can affect classification."""
        alg = Algorithm.parse_moves("L U L' U' L U L' U'")
        right_inputs = score_inputs(alg, HandDominance.RIGHT)
        left_inputs = score_inputs(alg, HandDominance.LEFT)
        right_score = calculate_ergonomic_score(right_inputs)
        left_score = calculate_ergonomic_score(left_inputs)
        right_diff = classify_algorithm_difficulty(
            right_score, right_inputs.regrip_count, right_inputs.flow,
        )
        left_diff = classify_algorithm_difficulty(
            left_score, left_inputs.regrip_count, left_inputs.flow,
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
            fingertrick_comfort=1.0,
        )
        self.assertEqual(suggestions, [])

    def test_all_pause_algorithm(self) -> None:
        """Test suggestions for non-empty algorithm with only pauses."""
        alg = Algorithm([Move('.')])
        self.assertEqual(
            suggest_ergonomic_improvements(
                alg, regrip_count=0, balance_ratio=0.5, flow=1.0,
                fingertrick_comfort=1.0,
            ),
            [],
        )

    def test_returns_list_of_strings(self) -> None:
        """Test that suggestions are strings."""
        alg = Algorithm.parse_moves('R U F L B D M E S')
        suggestions = suggest_ergonomic_improvements(
            alg, **suggestion_inputs(alg),
        )
        self.assertIsInstance(suggestions, list)
        for s in suggestions:
            self.assertIsInstance(s, str)

    def test_rotation_heavy_algorithm(self) -> None:
        """Test suggestions for algorithm with many rotations."""
        alg = Algorithm.parse_moves('x y z x y')
        suggestions = suggest_ergonomic_improvements(
            alg, **suggestion_inputs(alg),
        )
        rotation_suggestion = any('rotation' in s.lower() for s in suggestions)
        self.assertTrue(rotation_suggestion)

    def test_imbalanced_algorithm(self) -> None:
        """Test suggestions for right-heavy algorithm."""
        alg = Algorithm.parse_moves('R R R R R R R R')
        suggestions = suggest_ergonomic_improvements(
            alg, **suggestion_inputs(alg),
        )
        balance_suggestion = any('balance' in s.lower() for s in suggestions)
        self.assertTrue(balance_suggestion)

    def test_regrip_suggestion_names_actual_causes(self) -> None:
        """Test that the regrip suggestion fits rotation-free regrips."""
        alg = Algorithm.parse_moves("R L' R L' R L'")
        result = compute_ergonomics(alg)
        self.assertGreater(result.regrip_count, 0)
        self.assertNotIn(
            'Consider reducing cube rotations to minimize regrips',
            result.suggestions,
        )
        self.assertIn(
            'Consider reducing rotations and opposite-face transitions'
            ' to minimize regrips',
            result.suggestions,
        )

    def test_awkward_moves_suggestion_follows_hand_dominance(self) -> None:
        """Test that the awkward-moves suggestion uses the analyzed hand."""
        alg = Algorithm.parse_moves("L E L' M")
        awkward_suggestion = (
            'Consider alternatives to D, B, and slice moves where possible'
        )
        right = alg.compute_ergonomics(HandDominance.RIGHT)
        left = alg.compute_ergonomics(HandDominance.LEFT)
        # Right-hand comfort is below the threshold, lefty comfort above
        self.assertLess(right.fingertrick_comfort, WEIGHT_THRESHOLD)
        self.assertGreaterEqual(left.fingertrick_comfort, WEIGHT_THRESHOLD)
        self.assertIn(awkward_suggestion, right.suggestions)
        self.assertNotIn(awkward_suggestion, left.suggestions)


class TestComputeHandBalance(unittest.TestCase):
    """Test hand balance computation (ratio 0-1, 1 = perfectly balanced)."""

    def test_empty_algorithm(self) -> None:
        """Test hand balance for empty algorithm."""
        alg = Algorithm.parse_moves('')
        right, left, both, ratio = compute_hand_balance(alg)
        self.assertEqual(right, 0)
        self.assertEqual(left, 0)
        self.assertEqual(both, 0)
        self.assertEqual(ratio, 1.0)  # Perfect balance for empty algorithm

    def test_right_hand_dominant(self) -> None:
        """Test algorithm with right-hand dominant moves."""
        alg = Algorithm.parse_moves("R U R' U'")
        right, left, both, ratio = compute_hand_balance(alg)
        self.assertEqual(right, 3)  # R, U, R'
        self.assertEqual(left, 1)   # U'
        self.assertEqual(both, 0)
        self.assertAlmostEqual(ratio, 0.5)  # 2*min(3,1)/(3+1)

    def test_left_hand_dominant(self) -> None:
        """Test algorithm with left-hand dominant moves."""
        alg = Algorithm.parse_moves("L' U' L U")
        right, left, both, ratio = compute_hand_balance(alg)
        self.assertEqual(right, 1)  # U
        self.assertEqual(left, 3)   # L', U', L
        self.assertEqual(both, 0)
        self.assertAlmostEqual(ratio, 0.5)  # 2*min(1,3)/(1+3)

    def test_balanced_algorithm(self) -> None:
        """Test perfectly balanced algorithm."""
        alg = Algorithm.parse_moves("R U R' U' L' U' L U")
        right, left, both, ratio = compute_hand_balance(alg)
        self.assertEqual(right, 4)  # R, U, R', U
        self.assertEqual(left, 4)   # U', L', U', L
        self.assertEqual(both, 0)
        self.assertEqual(ratio, 1.0)  # Perfect balance

    def test_only_both_hand_moves(self) -> None:
        """Test algorithm with only both-hand moves."""
        alg = Algorithm.parse_moves('U2 D2 F2 B2')
        right, left, both, ratio = compute_hand_balance(alg)
        self.assertEqual(right, 0)
        self.assertEqual(left, 0)
        self.assertEqual(both, 4)
        self.assertEqual(ratio, 1.0)  # Perfect balance when no handed moves

    def test_ambidextrous_moves_excluded_from_ratio(self) -> None:
        """Test that both-hand moves do not dilute the ratio (D3)."""
        alg = Algorithm.parse_moves('R L U2 D2')
        right, left, both, ratio = compute_hand_balance(alg)
        self.assertEqual(right, 1)
        self.assertEqual(left, 1)
        self.assertEqual(both, 2)
        self.assertEqual(ratio, 1.0)  # Only R and L are compared

    def test_with_pauses(self) -> None:
        """Test hand balance calculation ignores pauses."""
        alg = Algorithm.parse_moves("R . U . R'")
        right, left, both, ratio = compute_hand_balance(alg)
        self.assertEqual(right, 3)  # R, U, R'
        self.assertEqual(left, 0)
        self.assertEqual(both, 0)
        self.assertEqual(ratio, 0.0)  # All handed moves are right


class TestComputeFingerDistribution(unittest.TestCase):
    """Test finger distribution computation."""

    def test_empty_algorithm(self) -> None:
        """Test finger distribution for empty algorithm."""
        alg = Algorithm.parse_moves('')
        thumb, index, middle, ring, pinky, mixed_moves = (
            compute_finger_distribution(alg)
        )
        self.assertEqual(thumb, 0)
        self.assertEqual(index, 0)
        self.assertEqual(middle, 0)
        self.assertEqual(ring, 0)
        self.assertEqual(pinky, 0)
        self.assertEqual(mixed_moves, 0)

    def test_thumb_moves(self) -> None:
        """Test algorithm with thumb moves."""
        alg = Algorithm.parse_moves("R L R' L'")
        thumb, index, middle, ring, pinky, mixed_moves = (
            compute_finger_distribution(alg)
        )
        self.assertEqual(thumb, 4)  # All R and L moves use thumb
        self.assertEqual(index, 0)
        self.assertEqual(middle, 0)
        self.assertEqual(ring, 0)
        self.assertEqual(pinky, 0)
        self.assertEqual(mixed_moves, 0)

    def test_index_finger_moves(self) -> None:
        """Test algorithm with index finger moves."""
        alg = Algorithm.parse_moves("U F U' F'")
        thumb, index, middle, ring, pinky, mixed_moves = (
            compute_finger_distribution(alg)
        )
        self.assertEqual(thumb, 0)
        self.assertEqual(index, 4)  # All U and F moves use index finger
        self.assertEqual(middle, 0)
        self.assertEqual(ring, 0)
        self.assertEqual(pinky, 0)
        self.assertEqual(mixed_moves, 0)

    def test_middle_finger_moves(self) -> None:
        """Test algorithm with middle finger moves."""
        alg = Algorithm.parse_moves("B B' B2 E")
        thumb, index, middle, ring, pinky, mixed_moves = (
            compute_finger_distribution(alg)
        )
        self.assertEqual(thumb, 0)
        self.assertEqual(index, 0)
        self.assertEqual(middle, 4)  # All B and E moves use middle finger
        self.assertEqual(ring, 0)
        self.assertEqual(pinky, 0)
        self.assertEqual(mixed_moves, 0)

    def test_ring_finger_moves(self) -> None:
        """Test algorithm with ring finger moves (D and M' family)."""
        alg = Algorithm.parse_moves("D D' M' M2")
        thumb, index, middle, ring, pinky, mixed_moves = (
            compute_finger_distribution(alg)
        )
        self.assertEqual(thumb, 0)
        self.assertEqual(index, 0)
        self.assertEqual(middle, 0)
        self.assertEqual(ring, 4)  # D, D', M', M2 use ring finger
        self.assertEqual(pinky, 0)
        self.assertEqual(mixed_moves, 0)

    def test_mixed_finger_usage(self) -> None:
        """Test algorithm with mixed finger usage."""
        alg = Algorithm.parse_moves("R U E M'")
        thumb, index, middle, ring, pinky, mixed_moves = (
            compute_finger_distribution(alg)
        )
        self.assertEqual(thumb, 1)   # R
        self.assertEqual(index, 1)   # U
        self.assertEqual(middle, 1)  # E
        self.assertEqual(ring, 1)    # M'
        self.assertEqual(pinky, 0)
        self.assertEqual(mixed_moves, 0)

    def test_with_pauses(self) -> None:
        """Test finger distribution calculation ignores pauses."""
        alg = Algorithm.parse_moves('R . U . B')
        thumb, index, middle, ring, pinky, mixed_moves = (
            compute_finger_distribution(alg)
        )
        self.assertEqual(thumb, 1)  # R
        self.assertEqual(index, 1)  # U
        self.assertEqual(middle, 1)  # B
        self.assertEqual(ring, 0)
        self.assertEqual(pinky, 0)
        self.assertEqual(mixed_moves, 0)

    def test_ring_finger_moves_as_last_move(self) -> None:
        """Test algorithm ending with ring finger move for branch coverage."""
        alg = Algorithm.parse_moves("R U M'")
        thumb, index, middle, ring, pinky, mixed_moves = (
            compute_finger_distribution(alg)
        )
        self.assertEqual(thumb, 1)  # R
        self.assertEqual(index, 1)  # U
        self.assertEqual(middle, 0)
        self.assertEqual(ring, 1)   # M'
        self.assertEqual(pinky, 0)
        self.assertEqual(mixed_moves, 0)

    def test_single_ring_finger_move(self) -> None:
        """Test algorithm with only ring finger move for branch coverage."""
        alg = Algorithm.parse_moves('D')
        thumb, index, middle, ring, pinky, mixed_moves = (
            compute_finger_distribution(alg)
        )
        self.assertEqual(thumb, 0)
        self.assertEqual(index, 0)
        self.assertEqual(middle, 0)
        self.assertEqual(ring, 1)  # D
        self.assertEqual(pinky, 0)
        self.assertEqual(mixed_moves, 0)

    def test_algorithm_ending_with_ring_finger(self) -> None:
        """Test for complete branch coverage with ring finger move at end."""
        # Ring finger moves: D family and M', M2
        for move_str in ['D', "D'", 'D2', "M'", 'M2']:
            alg = Algorithm.parse_moves(move_str)
            thumb, index, middle, ring, pinky, mixed_moves = (
            compute_finger_distribution(alg)
        )
            self.assertEqual(ring, 1, f'Ring finger count wrong for {move_str}')
            self.assertEqual(thumb + index + middle + pinky + mixed_moves, 0,
                           f'Other fingers should be 0 for {move_str}')

    def test_multiple_ring_finger_moves(self) -> None:
        """Test multiple consecutive ring finger moves for branch coverage."""
        alg = Algorithm.parse_moves("M' D M2")
        thumb, index, middle, ring, pinky, mixed_moves = (
            compute_finger_distribution(alg)
        )
        self.assertEqual(thumb, 0)
        self.assertEqual(index, 0)
        self.assertEqual(middle, 0)
        self.assertEqual(ring, 3)
        self.assertEqual(pinky, 0)
        self.assertEqual(mixed_moves, 0)

    def test_empty_finger_distribution_for_coverage(self) -> None:
        """Test edge case to ensure complete branch coverage."""
        moves = [Move("M'")]  # Single ring finger move as Move object
        alg = Algorithm(moves)
        thumb, index, middle, ring, pinky, mixed_moves = (
            compute_finger_distribution(alg)
        )
        self.assertEqual(ring, 1)
        self.assertEqual(thumb + index + middle + pinky + mixed_moves, 0)

        empty_alg = Algorithm([])
        thumb, index, middle, ring, pinky, mixed_moves = (
            compute_finger_distribution(empty_alg)
        )
        self.assertEqual(thumb, 0)
        self.assertEqual(index, 0)
        self.assertEqual(middle, 0)
        self.assertEqual(ring, 0)
        self.assertEqual(pinky, 0)
        self.assertEqual(mixed_moves, 0)

    def test_rotation_moves_mapped_by_axis(self) -> None:
        """Test that rotation moves are mapped to thumb."""
        alg = Algorithm.parse_moves('x y z')
        thumb, index, middle, ring, pinky, mixed_moves = (
            compute_finger_distribution(alg)
        )
        self.assertEqual(thumb, 0)
        self.assertEqual(index, 0)
        self.assertEqual(middle, 0)
        self.assertEqual(ring, 0)
        self.assertEqual(pinky, 0)
        self.assertEqual(mixed_moves, 3)   # x, y, z all map to mixed

    def test_wide_moves_match_base_face(self) -> None:
        """
        Test that wide moves are mapped to
        the same finger as their base face.
        """
        alg = Algorithm.parse_moves('Rw Uw Bw')
        thumb, index, middle, ring, pinky, mixed_moves = (
            compute_finger_distribution(alg)
        )
        self.assertEqual(thumb, 1)   # Rw -> thumb (like R)
        self.assertEqual(index, 1)   # Uw -> index (like U)
        self.assertEqual(middle, 1)  # Bw -> middle (like B)
        self.assertEqual(ring, 0)
        self.assertEqual(pinky, 0)
        self.assertEqual(mixed_moves, 0)

    def test_ring_finger_not_last_move(self) -> None:
        """Test ring move followed by another for branch coverage."""
        alg = Algorithm.parse_moves("M' R")  # ring finger then thumb
        thumb, index, middle, ring, pinky, mixed_moves = (
            compute_finger_distribution(alg)
        )
        self.assertEqual(thumb, 1)
        self.assertEqual(index, 0)
        self.assertEqual(middle, 0)
        self.assertEqual(ring, 1)
        self.assertEqual(pinky, 0)
        self.assertEqual(mixed_moves, 0)

    def test_pinky_finger_moves(self) -> None:
        """Test that PINKY finger assignment is counted correctly."""
        patched = {
            **MOVE_DATA,
            'R': MoveProperties(
                MOVE_DATA['R'].hand,
                FingerAssignment.PINKY,
                MOVE_DATA['R'].weight),
            "R'": MoveProperties(
                MOVE_DATA["R'"].hand,
                FingerAssignment.PINKY,
                MOVE_DATA["R'"].weight),
        }
        with patch('cubing_algs.ergonomics.MOVE_DATA', patched):
            alg = Algorithm.parse_moves("R R'")
            thumb, index, middle, ring, pinky, mixed_moves = (
                compute_finger_distribution(alg)
            )
            self.assertEqual(thumb, 0)
            self.assertEqual(index, 0)
            self.assertEqual(middle, 0)
            self.assertEqual(ring, 0)
            self.assertEqual(pinky, 2)
            self.assertEqual(mixed_moves, 0)

    def test_mixed_finger_moves(self) -> None:
        """Test that NONE finger assignment is counted correctly."""
        patched = {
            **MOVE_DATA,
            'R': MoveProperties(
                MOVE_DATA['R'].hand,
                FingerAssignment.MIXED,
                MOVE_DATA['R'].weight),
        }
        with patch('cubing_algs.ergonomics.MOVE_DATA', patched):
            alg = Algorithm.parse_moves('R')
            thumb, index, middle, ring, pinky, mixed_moves = (
                compute_finger_distribution(alg)
            )
            self.assertEqual(thumb, 0)
            self.assertEqual(index, 0)
            self.assertEqual(middle, 0)
            self.assertEqual(ring, 0)
            self.assertEqual(pinky, 0)
            self.assertEqual(mixed_moves, 1)


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

    def test_no_transition_counted_across_rotation(self) -> None:
        """Test that transitions across a rotation are not evaluated."""
        # R and L are opposite, but the rotation regrip between them
        # already resets the hands: only the rotation counts.
        alg = Algorithm.parse_moves('R x L')
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


class TestComputeFingertrickComfort(unittest.TestCase):
    """Test fingertrick comfort computation (0-1 scale, higher = better)."""

    def test_empty_algorithm(self) -> None:
        """Test fingertrick comfort for empty algorithm."""
        alg = Algorithm.parse_moves('')
        comfort = compute_fingertrick_comfort(alg)
        self.assertEqual(comfort, 1.0)

    def test_all_pause_algorithm(self) -> None:
        """Test comfort for non-empty algorithm with only pauses."""
        alg = Algorithm([Move('.')])
        self.assertEqual(compute_fingertrick_comfort(alg), 1.0)

    def test_easy_moves(self) -> None:
        """Test algorithm with easy moves has high comfort."""
        alg = Algorithm.parse_moves('R U')
        comfort = compute_fingertrick_comfort(alg)
        # R=0.95, U=0.98, avg=0.965
        self.assertAlmostEqual(comfort, 0.965)

    def test_difficult_moves(self) -> None:
        """Test algorithm with difficult moves has low comfort."""
        alg = Algorithm.parse_moves('S2 E2')
        comfort = compute_fingertrick_comfort(alg)
        # S2=0.35, E2=0.30, avg=0.325
        self.assertAlmostEqual(comfort, 0.325)

    def test_mixed_comfort(self) -> None:
        """Test algorithm with mixed comfort moves."""
        alg = Algorithm.parse_moves('R M')
        comfort = compute_fingertrick_comfort(alg)
        # R=0.95, M=0.42, avg=0.685
        self.assertAlmostEqual(comfort, 0.685)

    def test_rotation_move_weight(self) -> None:
        """Test that rotation moves use ergonomic weights."""
        alg = Algorithm([Move('x')])
        comfort = compute_fingertrick_comfort(alg)
        # x weighs 0.28 in MOVE_DATA
        self.assertAlmostEqual(comfort, 0.28)

    def test_with_pauses(self) -> None:
        """Test fingertrick comfort calculation ignores pauses."""
        alg = Algorithm.parse_moves('R . U')
        comfort = compute_fingertrick_comfort(alg)
        # R=0.95, U=0.98, avg=0.965
        self.assertAlmostEqual(comfort, 0.965)

    def test_hand_dominance_param(self) -> None:
        """Test that hand dominance affects comfort."""
        alg = Algorithm.parse_moves('B B B B')
        right_comfort = compute_fingertrick_comfort(alg, HandDominance.RIGHT)
        left_comfort = compute_fingertrick_comfort(alg, HandDominance.LEFT)
        # B moves (left-hand) should be more comfortable for left-handed
        self.assertLess(right_comfort, left_comfort)


class TestComputeMoveExecutionTime(unittest.TestCase):
    """Test per-move execution time computation."""

    def test_perfect_weight_takes_base_time(self) -> None:
        """Test that a weight-1.0 move takes exactly the base time."""
        self.assertEqual(MOVE_DATA["U'"].weight, 1.0)
        self.assertAlmostEqual(
            compute_move_execution_time(Move("U'")), BASE_MOVE_TIME,
        )

    def test_low_weight_moves_take_longer(self) -> None:
        """Test that less ergonomic moves take more time."""
        self.assertGreater(
            compute_move_execution_time(Move('B')),
            compute_move_execution_time(Move('R')),
        )
        self.assertGreater(
            compute_move_execution_time(Move('y2')),
            compute_move_execution_time(Move('B')),
        )

    def test_left_dominance_mirrors_time(self) -> None:
        """Test that move times follow the left-handed mirror model."""
        self.assertEqual(
            compute_move_execution_time(Move('L'), HandDominance.LEFT),
            compute_move_execution_time(Move("R'"), HandDominance.RIGHT),
        )


class TestComputeEstimatedExecutionTime(unittest.TestCase):
    """Test estimated execution time computation."""

    def test_empty_algorithm(self) -> None:
        """Test execution time for empty algorithm."""
        alg = Algorithm.parse_moves('')
        time = compute_estimated_execution_time(alg, 0)
        self.assertEqual(time, 0.0)

    def test_time_is_sum_of_move_times(self) -> None:
        """Test that execution time sums per-move execution times."""
        alg = Algorithm.parse_moves('R U')
        time = compute_estimated_execution_time(alg, 0)
        expected = (
            compute_move_execution_time(Move('R'))
            + compute_move_execution_time(Move('U'))
        )
        self.assertAlmostEqual(time, expected)

    def test_with_regrips(self) -> None:
        """Test execution time includes regrip penalties."""
        alg = Algorithm.parse_moves('R U')
        time = compute_estimated_execution_time(alg, 2)
        expected = (
            compute_estimated_execution_time(alg, 0)
            + 2 * REGRIP_TIME_PENALTY
        )
        self.assertAlmostEqual(time, expected)

    def test_with_pauses(self) -> None:
        """Test that each pause adds PAUSE_TIME to the execution time."""
        with_pause = Algorithm.parse_moves('R . U')
        without_pause = Algorithm.parse_moves('R U')
        self.assertAlmostEqual(
            compute_estimated_execution_time(with_pause, 0),
            compute_estimated_execution_time(without_pause, 0) + PAUSE_TIME,
        )

    def test_only_pauses_cost_no_time(self) -> None:
        """Test that an algorithm without real moves takes no time."""
        alg = Algorithm.parse_moves('. . .')
        self.assertEqual(compute_estimated_execution_time(alg, 0), 0.0)

    def test_trigger_speeds_up_covered_moves(self) -> None:
        """Test that trigger-covered moves execute at the trigger speed."""
        alg = Algorithm.parse_moves("R U R' U'")
        matches = find_trigger_patterns(alg)
        sexy = next(m for m in matches if m.pattern.name == 'Sexy Move')
        raw_time = compute_estimated_execution_time(alg, 0)
        trigger_time = compute_estimated_execution_time(alg, 0, matches)
        self.assertLess(trigger_time, raw_time)
        self.assertAlmostEqual(
            trigger_time, raw_time / trigger_speed_factor(sexy),
        )

    def test_trigger_speed_applies_only_to_covered_moves(self) -> None:
        """Test that moves outside a trigger keep their raw time."""
        alg = Algorithm.parse_moves("R U R' U' B2")
        matches = find_trigger_patterns(alg)
        sexy = next(m for m in matches if m.pattern.name == 'Sexy Move')
        self.assertEqual((sexy.start_index, sexy.end_index), (0, 3))
        sexy_alg = Algorithm.parse_moves("R U R' U'")
        expected = (
            compute_estimated_execution_time(sexy_alg, 0, matches)
            + compute_move_execution_time(Move('B2'))
        )
        self.assertAlmostEqual(
            compute_estimated_execution_time(alg, 0, matches), expected,
        )

    def test_left_dominance_changes_time(self) -> None:
        """Test that hand dominance is reflected in execution time."""
        alg = Algorithm.parse_moves("L' U' L U'")
        left_time = compute_estimated_execution_time(
            alg, 0, (), HandDominance.LEFT,
        )
        right_time = compute_estimated_execution_time(
            alg, 0, (), HandDominance.RIGHT,
        )
        self.assertLess(left_time, right_time)


class TestTemporalModelCoherence(unittest.TestCase):
    """Test that TPS and execution time are coherent by construction."""

    SUNE = "R U R' U R U2 R'"

    ISSUE_ALGOS = (
        (
            "U' F L D' R' U R' U' U U R U B' U B U' F' U F U' U' U' R' U R "
            "R U R' U' U F' U' U' F U' F U U F' U U F U' F' U F' U F U' U' "
            "F' U F F R U R' U' F' B U L U' L' B' U U' U'"
        ),
        (
            "U' L B D' F' U F' U' U U F U R' U R U' L' U L U' U' U' F' U F "
            "F U F' U' U L' U' U' L U' L U U L' U U L U' L' U L' U L U' U' "
            "L' U L L F U F' U' L' R U B U' B' R' U U' U'"
        ),
        (
            "U' B R D' L' U L' U' U U L U F' U F U' B' U B U' U' U' L' U L "
            "L U L' U' U B' U' U' B U' B U U B' U U B U' B' U B' U B U' U' "
            "B' U B B L U L' U' B' F U R U' R' F' U U' U'"
        ),
        (
            "U' R F D' B' U B' U' U U B U L' U L U' R' U R U' U' U' B' U B "
            "B U B' U' U R' U' U' R U' R U U R' U U R U' R' U R' U R U' U' "
            "R' U R R B U B' U' R' L U F U' F' L' U U' U'"
        ),
    )

    def test_tps_derived_from_execution_time(self) -> None:
        """Test estimated_tps == total_moves / estimated_execution_time."""
        for moves in (self.SUNE, "R U R' U'", 'B2 E2 S2 D2', *self.ISSUE_ALGOS):
            with self.subTest(moves=moves[:30]):
                result = Algorithm.parse_moves(moves).ergonomics
                self.assertAlmostEqual(
                    result.estimated_tps,
                    result.total_moves / result.estimated_execution_time,
                )

    def test_d2_calibration_on_clean_right_hand_algorithm(self) -> None:
        """Test that a clean R/U algorithm lands around 4.5 TPS (D2)."""
        result = Algorithm.parse_moves(self.SUNE).ergonomics
        self.assertGreaterEqual(result.estimated_tps, 4.0)
        self.assertLessEqual(result.estimated_tps, 5.0)

    def test_awkward_algorithm_is_much_slower(self) -> None:
        """Test that a B/D/slice-heavy algorithm is clearly slower."""
        clean = Algorithm.parse_moves(self.SUNE).ergonomics
        awkward = Algorithm.parse_moves('B2 E2 S2 D2').ergonomics
        self.assertLess(awkward.estimated_tps, clean.estimated_tps - 1.0)

    def test_issue_algorithms_have_distinct_times(self) -> None:
        """Test that the four issue algorithms get four distinct times."""
        times = {
            round(Algorithm.parse_moves(moves)
                  .ergonomics.estimated_execution_time, 9)
            for moves in self.ISSUE_ALGOS
        }
        self.assertEqual(len(times), len(self.ISSUE_ALGOS))


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
        self.assertEqual(result.hand_balance_ratio, 1.0)
        self.assertEqual(result.regrip_count, 0)
        self.assertEqual(result.awkward_moves, 0)
        self.assertEqual(result.estimated_execution_time, 0.0)
        self.assertEqual(result.fingertrick_comfort, 1.0)
        self.assertEqual(result.thumb_moves, 0)
        self.assertEqual(result.index_finger_moves, 0)
        self.assertEqual(result.middle_finger_moves, 0)
        self.assertEqual(result.ring_finger_moves, 0)
        self.assertEqual(result.pinky_finger_moves, 0)
        self.assertEqual(result.mixed_finger_moves, 0)
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

    def test_classification_consistent_with_exposed_score(self) -> None:
        """Test that classification derives from the exposed score."""
        # Sune: the trigger bonus lifts the final score above the
        # Beginner threshold; classification must follow the same score
        # as ergonomic_rating.
        alg = Algorithm.parse_moves("R U R' U R U2 R'")
        result = compute_ergonomics(alg)
        expected = classify_algorithm_difficulty(
            result.ergonomic_score,
            result.regrip_count,
            result.flow_score,
        )
        self.assertEqual(result.difficulty_classification, expected)

    def test_sexy_move_right_hand_heavy(self) -> None:
        """Test ergonomics for sexy move (R U R' U') - right-hand heavy."""
        alg = Algorithm.parse_moves("R U R' U'")
        result = compute_ergonomics(alg)

        self.assertEqual(result.total_moves, 4)
        self.assertEqual(result.right_hand_moves, 3)  # R, U, R'
        self.assertEqual(result.left_hand_moves, 1)   # U'
        self.assertEqual(result.both_hand_moves, 0)
        self.assertAlmostEqual(result.hand_balance_ratio, 0.5)  # 2*min(3,1)/4
        self.assertEqual(result.regrip_count, 0)  # All adjacent transitions
        self.assertEqual(result.thumb_moves, 2)  # R, R'
        self.assertEqual(result.index_finger_moves, 2)  # U, U'
        self.assertEqual(result.middle_finger_moves, 0)
        self.assertEqual(result.ring_finger_moves, 0)
        self.assertEqual(result.awkward_moves, 0)  # All weights >= 0.6

        # New fields
        self.assertGreater(result.ergonomic_score, 0.5)
        self.assertGreater(result.flow_score, 0.55)
        self.assertGreater(result.estimated_tps, 2.0)
        self.assertGreater(result.trigger_count, 0)  # Should detect Sexy Move

    def test_left_hand_equivalent(self) -> None:
        """Test ergonomics for left-hand sexy move (L' U' L U)."""
        alg = Algorithm.parse_moves("L' U' L U")
        result = compute_ergonomics(alg)

        self.assertEqual(result.total_moves, 4)
        self.assertEqual(result.right_hand_moves, 1)  # U
        self.assertEqual(result.left_hand_moves, 3)   # L', U', L
        self.assertEqual(result.both_hand_moves, 0)
        self.assertAlmostEqual(result.hand_balance_ratio, 0.5)  # 2*min(1,3)/4
        self.assertEqual(result.regrip_count, 0)
        self.assertEqual(result.thumb_moves, 2)  # L', L
        self.assertEqual(result.index_finger_moves, 2)  # U', U
        self.assertEqual(result.awkward_moves, 0)

    def test_perfectly_balanced_algorithm(self) -> None:
        """Test ergonomics for perfectly balanced algorithm."""
        alg = Algorithm.parse_moves("R U R' U' L' U' L U")
        result = compute_ergonomics(alg)

        self.assertEqual(result.total_moves, 8)
        self.assertEqual(result.right_hand_moves, 4)  # R, U, R', U
        self.assertEqual(result.left_hand_moves, 4)   # U', L', U', L
        self.assertEqual(result.both_hand_moves, 0)
        self.assertEqual(result.hand_balance_ratio, 1.0)  # Perfect balance
        self.assertEqual(result.regrip_count, 0)
        self.assertEqual(result.thumb_moves, 4)  # R, R', L', L
        self.assertEqual(result.index_finger_moves, 4)  # All U moves
        self.assertEqual(result.awkward_moves, 0)

    def test_slice_heavy_algorithm(self) -> None:
        """Test ergonomics for slice-heavy algorithm (M2 E2 S2)."""
        alg = Algorithm.parse_moves('M2 E2 S2')
        result = compute_ergonomics(alg)

        self.assertEqual(result.total_moves, 3)
        self.assertEqual(result.right_hand_moves, 2)  # E2, S2
        self.assertEqual(result.left_hand_moves, 1)   # M2
        self.assertEqual(result.both_hand_moves, 0)
        # 1 left, 2 right → 2*min(1,2)/(1+2) = 2/3
        self.assertAlmostEqual(result.hand_balance_ratio, 2 / 3)
        # No rotation moves, no opposite-face transitions
        self.assertEqual(result.regrip_count, 0)
        self.assertEqual(result.thumb_moves, 0)
        self.assertEqual(result.index_finger_moves, 2)  # E2, S2
        self.assertEqual(result.middle_finger_moves, 0)
        self.assertEqual(result.ring_finger_moves, 1)   # M2
        # M2=0.45, E2=0.30, S2=0.35 are all below AWKWARD_THRESHOLD=0.6
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
        self.assertEqual(result.thumb_moves, 1)
        self.assertEqual(result.index_finger_moves, 0)
        self.assertEqual(result.awkward_moves, 0)  # R weight = 1.0 >= 0.6

    def test_t_perm_complex_algorithm(self) -> None:
        """Test ergonomics for T-perm (complex PLL algorithm)."""
        alg = Algorithm.parse_moves("R U R' F' R U R' U' R' F R2 U' R'")
        result = compute_ergonomics(alg)

        self.assertEqual(result.total_moves, 13)
        # R moves (7) + F + U + U = 10 right; F' + U' + U' = 3 left
        self.assertEqual(result.right_hand_moves, 10)
        self.assertEqual(result.left_hand_moves, 3)   # F', U', U'
        self.assertEqual(result.both_hand_moves, 0)
        # 10 right, 3 left → 2*min(10,3)/(10+3) = 6/13
        self.assertAlmostEqual(result.hand_balance_ratio, 6 / 13)

        # Check for specific expected values
        self.assertGreater(result.estimated_execution_time, 0)
        self.assertLess(result.fingertrick_comfort, 1.0)
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
        self.assertEqual(result.hand_balance_ratio, 1.0)  # Perfect balance
        # R->L opposite (regrip), F->B opposite (regrip)
        self.assertEqual(result.regrip_count, 2)
        # B=0.52 is below AWKWARD_THRESHOLD=0.6; R, L, F are not
        self.assertEqual(result.awkward_moves, 1)

    def test_algorithm_with_pauses(self) -> None:
        """Test ergonomics calculation ignores pauses correctly."""
        alg = Algorithm.parse_moves("R . U . R'")
        result = compute_ergonomics(alg)

        self.assertEqual(result.total_moves, 3)  # Pauses not counted
        self.assertEqual(result.right_hand_moves, 3)  # R, U, R'
        self.assertEqual(result.both_hand_moves, 0)
        self.assertEqual(result.regrip_count, 0)

    def test_pauses_cannot_improve_score(self) -> None:
        """Test that inserting pauses costs time and never helps the score."""
        without_pauses = Algorithm.parse_moves("R B L' D R B")
        with_pauses = Algorithm.parse_moves("R . B . L' . D . R . B")
        plain = compute_ergonomics(without_pauses)
        paused = compute_ergonomics(with_pauses)

        self.assertEqual(paused.ergonomic_score, plain.ergonomic_score)
        self.assertEqual(paused.flow_score, plain.flow_score)
        self.assertGreater(
            paused.estimated_execution_time,
            plain.estimated_execution_time,
        )
        self.assertLess(paused.estimated_tps, plain.estimated_tps)

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
        self.assertIsInstance(result.pinky_finger_moves, int)
        self.assertIsInstance(result.mixed_finger_moves, int)

        # Test float fields
        self.assertIsInstance(result.hand_balance_ratio, float)
        self.assertIsInstance(result.estimated_execution_time, float)
        self.assertIsInstance(result.fingertrick_comfort, float)

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
        # E=0.45, S2=0.35, M=0.55 — all below threshold 0.6
        alg = Algorithm.parse_moves('E S2 M')
        result = compute_ergonomics(alg)
        self.assertEqual(result.awkward_moves, 3)  # E, S2, and M

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
