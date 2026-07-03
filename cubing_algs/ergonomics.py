"""
Ergonomics analysis tools for Rubik's cube algorithms.

This module provides functions to analyze the ergonomic properties
of algorithms, including hand balance, fingertrick comfort,
regrip requirements, trigger pattern detection, and overall
execution comfort.
"""
from collections.abc import Sequence
from enum import Enum
from functools import cache
from typing import TYPE_CHECKING
from typing import NamedTuple

from cubing_algs.constants import OPPOSITE_FACES
from cubing_algs.constants import SYMMETRY_M
from cubing_algs.move import Move
from cubing_algs.triggers import TRIGGER_PATTERNS
from cubing_algs.triggers import TriggerMatch
from cubing_algs.triggers import TriggerPattern
from cubing_algs.triggers import TriggerVariation
from cubing_algs.triggers import VariationKind

if TYPE_CHECKING:
    from cubing_algs.algorithm import Algorithm  # pragma: no cover


class HandDominance(Enum):
    """Enumeration for hand dominance preferences."""

    RIGHT = 'right'
    LEFT = 'left'
    AMBIDEXTROUS = 'ambidextrous'


class FingerAssignment(Enum):
    """Enumeration for finger assignments in move execution."""

    MIXED = 'mixed'
    THUMB = 'thumb'
    INDEX = 'index'
    MIDDLE = 'middle'
    RING = 'ring'
    PINKY = 'pinky'


class ErgonomicsData(NamedTuple):
    """
    Container for ergonomics computation results.

    All normalized metrics share the same scale: 0.0 to 1.0,
    higher is better.

    Attributes:
        total_moves: Number of non-pause moves.
        right_hand_moves: Moves executed by the right hand.
        left_hand_moves: Moves executed by the left hand.
        both_hand_moves: Moves executable by either hand; excluded
            from hand_balance_ratio.
        hand_balance_ratio: 2 * min(right, left) / (right + left),
            0.0 (one-handed) to 1.0 (perfectly balanced).
        regrip_count: Estimated number of regrips (count, lower is
            better).
        awkward_moves: Moves with an ergonomic weight below
            AWKWARD_THRESHOLD (count, lower is better).
        estimated_execution_time: Estimated execution time in seconds,
            including regrip and pause time.
        fingertrick_comfort: Average ergonomic move weight, 0.0
            (awkward) to 1.0 (comfortable).
        thumb_moves: Moves assigned to the thumb.
        index_finger_moves: Moves assigned to the index finger.
        middle_finger_moves: Moves assigned to the middle finger.
        ring_finger_moves: Moves assigned to the ring finger.
        pinky_finger_moves: Moves assigned to the pinky finger.
        mixed_finger_moves: Moves without a single-finger assignment.
        ergonomic_rating: Qualitative rating derived from
            ergonomic_score (Excellent to Very Poor).
        ergonomic_score: Overall weighted score, 0.0 to 1.0.
        flow_score: Transition smoothness, 0.0 to 1.0.
        estimated_tps: Derived turns per second
            (total_moves / estimated_execution_time).
        difficulty_classification: Beginner, Intermediate, Advanced
            or Expert, derived from the final score.
        trigger_count: Number of detected trigger patterns.
        trigger_coverage: Number of moves covered by triggers.
        detected_patterns: Names of the detected trigger patterns.
        suggestions: Improvement suggestions.

    """

    total_moves: int

    # Hand balance metrics
    right_hand_moves: int
    left_hand_moves: int
    both_hand_moves: int
    hand_balance_ratio: float

    # Difficulty metrics
    regrip_count: int
    awkward_moves: int

    # Execution metrics
    estimated_execution_time: float
    fingertrick_comfort: float

    # Move type distribution
    thumb_moves: int
    index_finger_moves: int
    middle_finger_moves: int
    ring_finger_moves: int
    pinky_finger_moves: int
    mixed_finger_moves: int

    # Comfort metrics
    ergonomic_rating: str

    # Advanced metrics
    ergonomic_score: float
    flow_score: float
    estimated_tps: float
    difficulty_classification: str
    trigger_count: int
    trigger_coverage: int
    detected_patterns: tuple[str, ...]
    suggestions: tuple[str, ...]


class MoveProperties(NamedTuple):
    """Ergonomic properties for a single move."""

    hand: HandDominance
    finger: FingerAssignment
    weight: float


HD = HandDominance
FA = FingerAssignment

MOVE_DATA: dict[str, MoveProperties] = {
    # Outer Face Moves
    'R': MoveProperties(HD.RIGHT, FA.THUMB, 0.95),
    "R'": MoveProperties(HD.RIGHT, FA.THUMB, 0.97),
    'R2': MoveProperties(HD.RIGHT, FA.THUMB, 0.88),
    'L': MoveProperties(HD.LEFT, FA.THUMB, 0.78),
    "L'": MoveProperties(HD.LEFT, FA.THUMB, 0.80),
    'L2': MoveProperties(HD.LEFT, FA.THUMB, 0.72),
    'U': MoveProperties(HD.RIGHT, FA.INDEX, 0.98),
    "U'": MoveProperties(HD.LEFT, FA.INDEX, 1.0),
    'U2': MoveProperties(HD.AMBIDEXTROUS, FA.INDEX, 0.90),
    'D': MoveProperties(HD.LEFT, FA.RING, 0.55),
    "D'": MoveProperties(HD.RIGHT, FA.RING, 0.58),
    'D2': MoveProperties(HD.AMBIDEXTROUS, FA.RING, 0.52),
    'F': MoveProperties(HD.RIGHT, FA.INDEX, 0.85),
    "F'": MoveProperties(HD.LEFT, FA.INDEX, 0.88),
    'F2': MoveProperties(HD.AMBIDEXTROUS, FA.INDEX, 0.80),
    'B': MoveProperties(HD.LEFT, FA.MIDDLE, 0.52),
    "B'": MoveProperties(HD.RIGHT, FA.MIDDLE, 0.55),
    'B2': MoveProperties(HD.AMBIDEXTROUS, FA.MIDDLE, 0.50),
    # Wide Moves — 2 layers
    'Rw': MoveProperties(HD.RIGHT, FA.THUMB, 0.85),
    "Rw'": MoveProperties(HD.RIGHT, FA.THUMB, 0.87),
    'Rw2': MoveProperties(HD.RIGHT, FA.THUMB, 0.78),
    'Lw': MoveProperties(HD.LEFT, FA.THUMB, 0.68),
    "Lw'": MoveProperties(HD.LEFT, FA.THUMB, 0.70),
    'Lw2': MoveProperties(HD.LEFT, FA.THUMB, 0.62),
    'Uw': MoveProperties(HD.RIGHT, FA.INDEX, 0.88),
    "Uw'": MoveProperties(HD.LEFT, FA.INDEX, 0.90),
    'Uw2': MoveProperties(HD.AMBIDEXTROUS, FA.INDEX, 0.80),
    'Dw': MoveProperties(HD.LEFT, FA.MIDDLE, 0.45),
    "Dw'": MoveProperties(HD.RIGHT, FA.MIDDLE, 0.48),
    'Dw2': MoveProperties(HD.AMBIDEXTROUS, FA.MIDDLE, 0.42),
    'Fw': MoveProperties(HD.RIGHT, FA.INDEX, 0.75),
    "Fw'": MoveProperties(HD.LEFT, FA.INDEX, 0.78),
    'Fw2': MoveProperties(HD.AMBIDEXTROUS, FA.INDEX, 0.70),
    'Bw': MoveProperties(HD.LEFT, FA.MIDDLE, 0.42),
    "Bw'": MoveProperties(HD.RIGHT, FA.MIDDLE, 0.45),
    'Bw2': MoveProperties(HD.AMBIDEXTROUS, FA.MIDDLE, 0.40),
    # Slice Moves
    'M': MoveProperties(HD.RIGHT, FA.THUMB, 0.42),
    "M'": MoveProperties(HD.LEFT, FA.RING, 0.48),
    'M2': MoveProperties(HD.LEFT, FA.RING, 0.45),
    'E': MoveProperties(HD.LEFT, FA.MIDDLE, 0.32),
    "E'": MoveProperties(HD.RIGHT, FA.INDEX, 0.35),
    'E2': MoveProperties(HD.RIGHT, FA.INDEX, 0.30),
    'S': MoveProperties(HD.RIGHT, FA.INDEX, 0.38),
    "S'": MoveProperties(HD.LEFT, FA.INDEX, 0.32),
    'S2': MoveProperties(HD.RIGHT, FA.INDEX, 0.35),
    # Cube Rotations
    'x': MoveProperties(HD.AMBIDEXTROUS, FA.MIXED, 0.28),
    "x'": MoveProperties(HD.AMBIDEXTROUS, FA.MIXED, 0.28),
    'x2': MoveProperties(HD.AMBIDEXTROUS, FA.MIXED, 0.25),
    'y': MoveProperties(HD.AMBIDEXTROUS, FA.MIXED, 0.30),
    "y'": MoveProperties(HD.AMBIDEXTROUS, FA.MIXED, 0.30),
    'y2': MoveProperties(HD.AMBIDEXTROUS, FA.MIXED, 0.22),
    'z': MoveProperties(HD.AMBIDEXTROUS, FA.MIXED, 0.25),
    "z'": MoveProperties(HD.AMBIDEXTROUS, FA.MIXED, 0.25),
    'z2': MoveProperties(HD.AMBIDEXTROUS, FA.MIXED, 0.20),
}

DEFAULT_MOVE_PROPERTIES = MoveProperties(
    HD.AMBIDEXTROUS, FA.INDEX, 0.5,
)

# Threshold for considering a move awkward (weight below this is awkward)
AWKWARD_THRESHOLD = 0.6

# Difficulty classification thresholds
BEGINNER_SCORE = 0.8
BEGINNER_FLOW = 0.8
BEGINNER_REGRIPS = 1
INTERMEDIATE_SCORE = 0.65
INTERMEDIATE_FLOW = 0.6
INTERMEDIATE_REGRIPS = 3
ADVANCED_SCORE = 0.45
ADVANCED_REGRIPS = 6

# Ergonomic rating thresholds
EXCELLENT_SCORE = 0.80
GOOD_SCORE = 0.65
FAIR_SCORE = 0.50
POOR_SCORE = 0.35

# Suggestion thresholds
REGRIP_RATIO_THRESHOLD = 0.2
BALANCE_THRESHOLD = 0.6
FLOW_THRESHOLD = 0.6
WEIGHT_THRESHOLD = 0.6
ROTATION_RATIO_THRESHOLD = 0.15

# Ergonomic factors applied to trigger qualities and speed multipliers
# depending on the matched variation kind (canonical form gets 1.0).
VARIATION_FACTORS: dict[VariationKind, float] = {
    VariationKind.LEFTY: 0.95,
    VariationKind.INVERSE: 0.95,
    VariationKind.BACK: 0.85,
}

# Best in-catalogue trigger bonus, used to normalize trigger quality to 0-1.
MAX_TRIGGER_BONUS = max(p.ergonomic_bonus for p in TRIGGER_PATTERNS)

# Weighted-average composition of the ergonomic score (weights sum to 1.0).
# Calibrated so the acceptance algorithms of the 2.4 refactor discriminate:
# hand balance is kept low so one-handed OLLs are not unduly penalized.
SCORE_WEIGHT_MOVES = 0.40
SCORE_WEIGHT_FLOW = 0.25
SCORE_WEIGHT_TRIGGERS = 0.15
SCORE_WEIGHT_BALANCE = 0.05
SCORE_WEIGHT_REGRIPS = 0.15

TRANSITION_PENALTIES: dict[str, float] = {
    'same_face': 0.0,
    'adjacent': 0.1,
    'hand_switch': 0.15,
    'opposite': 0.3,
    'rotation': 0.5,
}

# Cube rotations are hand-neutral: the left-handed mirror keeps them as-is.
MIRROR_IGNORE_MOVES = {'x', 'y', 'z'}

# Temporal model calibration (decision D2): seconds for a weight-1.0 move,
# chosen so a clean R/U algorithm like Sune lands around 4.5 effective TPS.
BASE_MOVE_TIME = 0.28

# Additional seconds per regrip.
REGRIP_TIME_PENALTY = 0.07

# Seconds per pause: one comfortable move worth of hesitation.
PAUSE_TIME = BASE_MOVE_TIME


def get_move_key(move: Move) -> str:
    """
    Get the standardized key for move lookup.

    Handles SiGN notation and layered moves by converting them
    to their base equivalents.

    Args:
        move: Move object to get key for.

    Returns:
        Standardized string key for move lookup.

    """
    if move.is_pause or move.is_rotation_move:
        return str(move)

    # Convert SiGN notation to standard
    if move.is_sign_move:
        move = move.to_standard

    # Get unlayered version for lookup
    base_move = move.unlayered

    return str(base_move)


@cache
def mirror_move_key(move_key: str) -> str:
    """
    Mirror a move key across the M slice.

    R and L layers are swapped and the turn direction is inverted
    (R becomes L', M becomes M'), while cube rotations and pauses
    are left unchanged.

    Args:
        move_key: Move key to mirror, as returned by get_move_key.

    Returns:
        The mirrored move key.

    """
    from cubing_algs.parsing import parse_moves  # noqa: PLC0415
    from cubing_algs.transform.symmetry import symmetry_moves  # noqa: PLC0415

    return str(
        symmetry_moves(
            parse_moves(move_key),
            MIRROR_IGNORE_MOVES,
            SYMMETRY_M,
        ),
    )


def get_move_ergonomic_weight(
    move: Move,
    hand_dominance: HandDominance = HandDominance.RIGHT,
) -> float:
    """
    Get the ergonomic weight for a single move.

    Returns a value between 0 and 1, where 1 is the most ergonomic.

    MOVE_DATA holds right-handed weights; for left-handed users the
    weight of the mirrored move is used instead, making both hands
    perfectly symmetric.

    Args:
        move: The move to analyze.
        hand_dominance: The hand dominance preference.

    Returns:
        Ergonomic weight from 0.0 to 1.0.

    """
    move_key = get_move_key(move)

    if hand_dominance == HandDominance.LEFT:
        move_key = mirror_move_key(move_key)

    return MOVE_DATA.get(move_key, DEFAULT_MOVE_PROPERTIES).weight


def get_transition_penalty(move1: Move, move2: Move) -> float:
    """
    Calculate the ergonomic penalty for transitioning between two moves.

    Args:
        move1: The first move.
        move2: The second move.

    Returns:
        Penalty value (0.0 = no penalty, higher = more difficult).

    """
    if move1.is_pause or move2.is_pause:
        return 0.0

    # Rotation moves always incur significant penalty
    if move1.is_rotation_move or move2.is_rotation_move:
        return TRANSITION_PENALTIES['rotation']

    face1 = move1.base_move
    face2 = move2.base_move

    # Same face is easiest
    if face1 == face2:
        return TRANSITION_PENALTIES['same_face']

    # Opposite faces may require regripping
    if OPPOSITE_FACES.get(face1) == face2:
        return TRANSITION_PENALTIES['opposite']

    # Hand switches cost more than staying on the same hand.
    # Checked before adjacency: distinct non-opposite faces are
    # always adjacent, so adjacency alone cannot discriminate.
    key1 = get_move_key(move1)
    key2 = get_move_key(move2)
    hand1 = MOVE_DATA.get(key1, DEFAULT_MOVE_PROPERTIES).hand
    hand2 = MOVE_DATA.get(key2, DEFAULT_MOVE_PROPERTIES).hand
    if (
        hand1 not in {hand2, HandDominance.AMBIDEXTROUS}
        and hand2 != HandDominance.AMBIDEXTROUS
    ):
        return TRANSITION_PENALTIES['hand_switch']

    # Same-hand transitions between different faces are moderate
    return TRANSITION_PENALTIES['adjacent']


def calculate_flow_score(algorithm: 'Algorithm') -> float:
    """
    Calculate the overall flow score of an algorithm.

    Higher scores indicate better flow with fewer awkward transitions.
    Pauses are transparent: transitions are evaluated between the
    moves surrounding them, so inserting pauses cannot improve flow.
    Their time cost is handled by the temporal model instead.

    Args:
        algorithm: The algorithm to analyze.

    Returns:
        Flow score from 0.0 to 1.0.

    """
    from cubing_algs.transform.pause import unpause_moves  # noqa: PLC0415

    moves = algorithm.transform(unpause_moves)

    if len(moves) <= 1:
        return 1.0

    total_penalty = sum(
        get_transition_penalty(moves[i - 1], moves[i])
        for i in range(1, len(moves))
    )

    avg_penalty = total_penalty / (len(moves) - 1)

    # Normalize on the effective penalty range of regular transitions
    # (up to opposite-face) so values spread; rotation-heavy algorithms
    # exceed the ceiling and bottom out at 0.
    max_effective_penalty = TRANSITION_PENALTIES['opposite']

    return max(0.0, 1.0 - (avg_penalty / max_effective_penalty))


def normalize_algorithm_string(algorithm: 'Algorithm') -> str:
    """
    Convert algorithm to normalized string for pattern matching.

    Pauses are removed and moves are converted to standard notation.

    Returns:
        Space-separated string of non-pause moves in standard notation.

    """
    from cubing_algs.transform.pause import unpause_moves  # noqa: PLC0415
    from cubing_algs.transform.sign import unsign_moves  # noqa: PLC0415

    return str(algorithm.transform(unpause_moves, unsign_moves))


@cache
def normalize_moves_string(moves: str) -> str:
    """
    Normalize a space-separated move string to standard notation.

    Cached string-level wrapper around normalize_algorithm_string,
    used to normalize the static trigger pattern strings once.

    Args:
        moves: Space-separated move string.

    Returns:
        Space-separated move string in standard notation.

    """
    from cubing_algs.parsing import parse_moves  # noqa: PLC0415

    return normalize_algorithm_string(parse_moves(moves))


def find_trigger_patterns(
    algorithm: 'Algorithm',
    hand_dominance: HandDominance = HandDominance.RIGHT,
) -> list[TriggerMatch]:
    """
    Detect common speedcubing triggers and patterns in an algorithm.

    Args:
        algorithm: The algorithm to analyze.
        hand_dominance: Hand dominance preference for pattern prioritization.

    Returns:
        List of TriggerMatch objects for detected patterns.

    """
    if len(algorithm) == 0:
        return []

    algorithm_str = normalize_algorithm_string(algorithm)
    algorithm_moves = algorithm_str.split()

    matches: list[TriggerMatch] = []
    used_indices: set[int] = set()

    # Sort patterns: longer first, then by ergonomic bonus
    # Left-handed users get a slight bonus for patterns with a lefty form
    left_bonus = 0.01 if hand_dominance == HandDominance.LEFT else 0.0

    def has_lefty_variation(pattern: TriggerPattern) -> bool:
        return any(
            variation.kind == VariationKind.LEFTY
            for variation in pattern.variations
        )

    sorted_patterns = sorted(
        TRIGGER_PATTERNS,
        key=lambda p: (
            len(p.moves.split()),
            p.ergonomic_bonus + (left_bonus if has_lefty_variation(p) else 0.0),
        ),
        reverse=True,
    )

    for pattern in sorted_patterns:
        # Check main pattern first, then variations.
        candidates: list[tuple[str, TriggerVariation | None]] = [
            (pattern.moves, None),
            *((variation.moves, variation) for variation in pattern.variations),
        ]

        for pattern_moves, variation in candidates:
            pattern_list = normalize_moves_string(pattern_moves).split()
            pattern_length = len(pattern_list)

            # Sliding window search
            for i in range(len(algorithm_moves) - pattern_length + 1):
                if any(
                    idx in used_indices for idx in range(i, i + pattern_length)
                ):
                    continue

                window = algorithm_moves[i : i + pattern_length]
                if window == pattern_list:
                    match = TriggerMatch(
                        pattern=pattern,
                        start_index=i,
                        end_index=i + pattern_length - 1,
                        matched_moves=' '.join(window),
                        variation=variation,
                    )
                    matches.append(match)

                    used_indices.update(range(i, i + pattern_length))

    return matches


def variation_factor(match: TriggerMatch) -> float:
    """
    Get the ergonomic factor of a matched trigger variation.

    Canonical values were calibrated from right-hand executions.
    Lefty and inverse variations execute close to canonical,
    back-face variations are noticeably slower.

    Args:
        match: Trigger match to evaluate.

    Returns:
        Factor from 0.0 to 1.0, 1.0 for the canonical form.

    """
    if match.variation is None:
        return 1.0
    return VARIATION_FACTORS[match.variation.kind]


def trigger_speed_factor(match: TriggerMatch) -> float:
    """
    Get the effective speed multiplier of a matched trigger.

    Degraded variations are never faster than the canonical form:
    the speed benefit of fast triggers shrinks with the variation
    factor (Sexy Move 1.95 canonical → 1.90 lefty → 1.81 back) while
    the slowness of slow triggers grows (Hedgeslammer 0.85 canonical
    → 0.82 back).

    Args:
        match: Trigger match to evaluate.

    Returns:
        Speed multiplier applied to the moves covered by the trigger.

    """
    deviation = match.pattern.speed_multiplier - 1.0
    factor = variation_factor(match)

    if deviation >= 0:
        return 1.0 + deviation * factor
    return 1.0 + deviation / factor


def trigger_quality(match: TriggerMatch) -> float:
    """
    Get the ergonomic quality of a matched trigger, from 0.0 to 1.0.

    The pattern's ergonomic bonus is normalized against the best
    in-catalogue bonus, then scaled by the variation factor: a canonical
    Sexy Move rates 1.0, awkward patterns rate near 0.0.

    Args:
        match: Trigger match to evaluate.

    Returns:
        Quality factor from 0.0 to 1.0.

    """
    return (
        match.pattern.ergonomic_bonus / MAX_TRIGGER_BONUS
    ) * variation_factor(match)


def calculate_trigger_score(
    matches: Sequence[TriggerMatch],
    total_moves: int,
) -> float:
    """
    Calculate the trigger component of the ergonomic score.

    Quality-weighted trigger coverage: each matched move contributes its
    trigger's quality, normalized by the algorithm length. An algorithm
    fully covered by top-quality triggers scores 1.0, one without any
    trigger scores 0.0.

    Args:
        matches: Detected trigger matches.
        total_moves: Number of non-pause moves in the algorithm.

    Returns:
        Trigger score from 0.0 to 1.0.

    """
    if total_moves == 0 or not matches:
        return 0.0

    weighted_coverage = sum(
        match.length * trigger_quality(match)
        for match in matches
    )

    return min(1.0, weighted_coverage / total_moves)


class ErgonomicScoreInputs(NamedTuple):
    """Pre-computed metrics feeding the ergonomic score."""

    total_moves: int
    fingertrick_comfort: float
    flow: float
    balance_ratio: float
    regrip_count: int
    trigger_score: float


def calculate_ergonomic_score(inputs: ErgonomicScoreInputs) -> float:
    """
    Calculate an overall ergonomic score from pre-computed metrics.

    Weighted average of move comfort, flow, trigger coverage,
    hand balance and regrip components, all on a 0-1 scale.

    Args:
        inputs: Pre-computed comfort, flow, balance, regrip and
            trigger metrics.

    Returns:
        Ergonomic score from 0.0 to 1.0.

    """
    if inputs.total_moves == 0:
        return 1.0

    regrip_score = max(
        0.0, 1.0 - (inputs.regrip_count / inputs.total_moves),
    )

    return max(
        0.0,
        min(
            1.0,
            inputs.fingertrick_comfort * SCORE_WEIGHT_MOVES
            + inputs.flow * SCORE_WEIGHT_FLOW
            + inputs.trigger_score * SCORE_WEIGHT_TRIGGERS
            + inputs.balance_ratio * SCORE_WEIGHT_BALANCE
            + regrip_score * SCORE_WEIGHT_REGRIPS,
        ),
    )


def classify_algorithm_difficulty(
    ergonomic_score: float,
    regrip_count: int,
    flow: float,
) -> str:
    """
    Classify an algorithm into difficulty categories based on ergonomics.

    Args:
        ergonomic_score: Pre-computed ergonomic score.
        regrip_count: Pre-computed regrip count.
        flow: Pre-computed flow score.

    Returns:
        One of: 'Beginner', 'Intermediate', 'Advanced', 'Expert'.

    """
    if (
        ergonomic_score >= BEGINNER_SCORE
        and regrip_count <= BEGINNER_REGRIPS
        and flow >= BEGINNER_FLOW
    ):
        return 'Beginner'
    if (
        ergonomic_score >= INTERMEDIATE_SCORE
        and regrip_count <= INTERMEDIATE_REGRIPS
        and flow >= INTERMEDIATE_FLOW
    ):
        return 'Intermediate'
    if ergonomic_score >= ADVANCED_SCORE and regrip_count <= ADVANCED_REGRIPS:
        return 'Advanced'
    return 'Expert'


def suggest_ergonomic_improvements(
    algorithm: 'Algorithm',
    *,
    regrip_count: int,
    balance_ratio: float,
    flow: float,
    fingertrick_comfort: float,
) -> list[str]:
    """
    Suggest specific improvements to make the algorithm more ergonomic.

    Args:
        algorithm: The algorithm to analyze.
        regrip_count: Pre-computed regrip count.
        balance_ratio: Pre-computed hand balance ratio.
        flow: Pre-computed flow score.
        fingertrick_comfort: Pre-computed fingertrick comfort, on the
            analyzed hand.

    Returns:
        List of improvement suggestions.

    """
    if len(algorithm) == 0:
        return []

    suggestions: list[str] = []

    non_pause_count = sum(1 for m in algorithm if not m.is_pause)

    if non_pause_count == 0:
        return []

    if regrip_count > non_pause_count * REGRIP_RATIO_THRESHOLD:
        suggestions.append(
            'Consider reducing rotations and opposite-face transitions'
            ' to minimize regrips',
        )

    if balance_ratio < BALANCE_THRESHOLD:
        suggestions.append('Try to balance moves between both hands')

    if flow < FLOW_THRESHOLD:
        suggestions.append(
            'Look for alternatives to reduce awkward move transitions',
        )

    if fingertrick_comfort < WEIGHT_THRESHOLD:
        suggestions.append(
            'Consider alternatives to D, B, and slice moves where possible',
        )

    rotation_count = sum(1 for move in algorithm if move.is_rotation_move)
    if rotation_count > non_pause_count * ROTATION_RATIO_THRESHOLD:
        suggestions.append('Try to find rotation-free alternatives')

    return suggestions


def compute_hand_balance(moves: 'Algorithm') -> tuple[int, int, int, float]:
    """
    Calculate hand balance metrics for the algorithm.

    Args:
        moves: 'Algorithm' to analyze.

    Returns:
        Tuple of (right_count, left_count, both_count, balance_ratio).

    """
    right_count = 0
    left_count = 0
    both_count = 0

    for move in moves:
        if move.is_pause:
            continue

        move_key = get_move_key(move)
        hand = MOVE_DATA.get(move_key, DEFAULT_MOVE_PROPERTIES).hand

        if hand == HandDominance.RIGHT:
            right_count += 1
        elif hand == HandDominance.LEFT:
            left_count += 1
        else:
            both_count += 1

    # Balance ratio: 0.0 (one-handed) to 1.0 (perfectly balanced).
    # Ambidextrous moves are excluded: only clearly handed moves are
    # compared (decision D3); the three counters stay exposed.
    total_handed = right_count + left_count
    if total_handed == 0:
        balance_ratio = 1.0
    else:
        balance_ratio = 2 * min(right_count, left_count) / total_handed

    return right_count, left_count, both_count, balance_ratio


def compute_finger_distribution(
    moves: 'Algorithm',
) -> tuple[int, int, int, int, int, int]:
    """
    Calculate finger usage distribution for the algorithm.

    Args:
        moves: 'Algorithm' to analyze.

    Returns:
        Tuple of (thumb_count, index_count, middle_count,
        ring_count, pinky_count, none_count).

    """
    thumb_count = 0
    index_count = 0
    middle_count = 0
    ring_count = 0
    pinky_count = 0
    none_count = 0

    for move in moves:
        if move.is_pause:
            continue

        move_key = get_move_key(move)
        finger = MOVE_DATA.get(move_key, DEFAULT_MOVE_PROPERTIES).finger

        if finger == FingerAssignment.THUMB:
            thumb_count += 1
        elif finger == FingerAssignment.INDEX:
            index_count += 1
        elif finger == FingerAssignment.MIDDLE:
            middle_count += 1
        elif finger == FingerAssignment.RING:
            ring_count += 1
        elif finger == FingerAssignment.PINKY:
            pinky_count += 1
        elif finger == FingerAssignment.MIXED:
            none_count += 1

    return (
        thumb_count,
        index_count,
        middle_count,
        ring_count,
        pinky_count,
        none_count,
    )


def compute_regrip_count(moves: 'Algorithm') -> int:
    """
    Estimate the number of regrips required for the algorithm.

    Uses transition-aware approach: counts rotation moves and
    transitions with penalty >= opposite-face penalty.

    Args:
        moves: 'Algorithm' to analyze.

    Returns:
        Number of estimated regrips required.

    """
    from cubing_algs.transform.pause import unpause_moves  # noqa: PLC0415

    moves = moves.transform(unpause_moves)
    regrip_count = 0
    prev_move: Move | None = None
    opposite = TRANSITION_PENALTIES['opposite']

    for move in moves:
        if move.is_rotation_move:
            regrip_count += 1
            # The rotation regrip resets the hands: transitions
            # across it are not evaluated.
            prev_move = None
            continue

        if (
            prev_move is not None
            and get_transition_penalty(prev_move, move) >= opposite
        ):
            regrip_count += 1

        prev_move = move

    return regrip_count


def compute_fingertrick_comfort(
    moves: 'Algorithm',
    hand_dominance: HandDominance = HandDominance.RIGHT,
) -> float:
    """
    Calculate overall fingertrick comfort score.

    Average of the ergonomic move weights: higher means more
    comfortable execution.

    Args:
        moves: 'Algorithm' to analyze.
        hand_dominance: The hand dominance preference.

    Returns:
        Comfort score from 0.0 (most awkward) to 1.0 (most comfortable).

    """
    if not moves:
        return 1.0

    total_weight = 0.0
    move_count = 0

    for move in moves:
        if move.is_pause:
            continue

        weight = get_move_ergonomic_weight(move, hand_dominance)
        total_weight += weight
        move_count += 1

    if move_count == 0:
        return 1.0

    return total_weight / move_count


def compute_move_execution_time(
    move: Move,
    hand_dominance: HandDominance = HandDominance.RIGHT,
) -> float:
    """
    Estimate the execution time of a single move in seconds.

    Derived from the ergonomic weight: a weight-1.0 move takes
    BASE_MOVE_TIME, the least ergonomic moves take up to twice that.

    Args:
        move: The move to analyze.
        hand_dominance: The hand dominance preference.

    Returns:
        Estimated move time in seconds.

    """
    weight = get_move_ergonomic_weight(move, hand_dominance)
    return 2 * BASE_MOVE_TIME / (1 + weight)


def compute_estimated_execution_time(
    moves: 'Algorithm',
    regrip_count: int,
    trigger_matches: Sequence[TriggerMatch] = (),
    hand_dominance: HandDominance = HandDominance.RIGHT,
) -> float:
    """
    Estimate algorithm execution time in seconds.

    Sums per-move execution times, speeds up trigger-covered moves by
    the trigger's speed factor, and adds regrip and pause penalties.

    Args:
        moves: 'Algorithm' to analyze.
        regrip_count: Number of regrips in the algorithm.
        trigger_matches: Detected triggers; their indices refer to the
            non-pause move sequence.
        hand_dominance: The hand dominance preference.

    Returns:
        Estimated execution time in seconds.

    """
    non_pause_moves = [move for move in moves if not move.is_pause]

    if not non_pause_moves:
        return 0.0

    pause_count = len(moves) - len(non_pause_moves)

    speed_factors = [1.0] * len(non_pause_moves)
    for match in trigger_matches:
        factor = trigger_speed_factor(match)
        for index in range(match.start_index, match.end_index + 1):
            speed_factors[index] = factor

    move_times = sum(
        compute_move_execution_time(move, hand_dominance) / factor
        for move, factor in zip(non_pause_moves, speed_factors, strict=True)
    )

    return (
        move_times
        + (regrip_count * REGRIP_TIME_PENALTY)
        + (pause_count * PAUSE_TIME)
    )


def get_ergonomic_rating(ergonomic_score: float) -> str:
    """
    Convert ergonomic score to ergonomic rating.

    Args:
        ergonomic_score: Ergonomic score from 0.0 to 1.0.

    Returns:
        Human-readable rating string (Excellent, Good, Fair, Poor, Very Poor).

    """
    if ergonomic_score >= EXCELLENT_SCORE:
        return 'Excellent'
    if ergonomic_score >= GOOD_SCORE:
        return 'Good'
    if ergonomic_score >= FAIR_SCORE:
        return 'Fair'
    if ergonomic_score >= POOR_SCORE:
        return 'Poor'
    return 'Very Poor'


def compute_ergonomics(  # noqa: PLR0914
    algorithm: 'Algorithm',
    hand_dominance: HandDominance = HandDominance.RIGHT,
) -> ErgonomicsData:
    """
    Compute comprehensive ergonomics metrics for an algorithm.

    This function analyzes various aspects of algorithm ergonomics including:
    - Hand balance and coordination requirements
    - Fingertrick difficulty and execution comfort
    - Regrip requirements and flow interruptions
    - Trigger pattern detection
    - Estimated execution time and overall comfort rating

    Args:
        algorithm: The algorithm to analyze.
        hand_dominance: The hand dominance preference.

    Returns:
        ErgonomicsData containing all calculated ergonomic metrics.

    """
    # Filter out pauses for most calculations
    non_pause_moves = [move for move in algorithm if not move.is_pause]
    total_moves = len(non_pause_moves)

    if total_moves == 0:
        return ErgonomicsData(
            total_moves=0,
            right_hand_moves=0,
            left_hand_moves=0,
            both_hand_moves=0,
            hand_balance_ratio=1.0,
            regrip_count=0,
            awkward_moves=0,
            estimated_execution_time=0.0,
            fingertrick_comfort=1.0,
            thumb_moves=0,
            index_finger_moves=0,
            middle_finger_moves=0,
            ring_finger_moves=0,
            pinky_finger_moves=0,
            mixed_finger_moves=0,
            ergonomic_rating='Excellent',
            ergonomic_score=1.0,
            flow_score=1.0,
            estimated_tps=0.0,
            difficulty_classification='Beginner',
            trigger_count=0,
            trigger_coverage=0,
            detected_patterns=(),
            suggestions=(),
        )

    # Calculate hand balance
    right_hand, left_hand, both_hand, balance_ratio = compute_hand_balance(
        algorithm,
    )

    # Calculate finger distribution
    thumb, index, middle, ring, pinky, mixed_moves = (
        compute_finger_distribution(algorithm)
    )

    # Calculate difficulty metrics
    regrip_count = compute_regrip_count(algorithm)

    # Move weights are computed once: they feed the comfort average,
    # the awkward count and the ergonomic score
    move_weights = [
        get_move_ergonomic_weight(move, hand_dominance)
        for move in non_pause_moves
    ]
    fingertrick_comfort = sum(move_weights) / total_moves
    awkward_moves = sum(
        1 for weight in move_weights if weight < AWKWARD_THRESHOLD
    )

    # Detect triggers first: they speed up the moves they cover
    trigger_matches = find_trigger_patterns(algorithm, hand_dominance)

    # Calculate execution time; TPS is derived from it
    execution_time = compute_estimated_execution_time(
        algorithm,
        regrip_count,
        trigger_matches,
        hand_dominance,
    )
    estimated_tps = total_moves / execution_time

    # Advanced metrics
    flow_score_val = calculate_flow_score(algorithm)
    trigger_score = calculate_trigger_score(trigger_matches, total_moves)
    ergonomic_score = calculate_ergonomic_score(
        ErgonomicScoreInputs(
            total_moves=total_moves,
            fingertrick_comfort=fingertrick_comfort,
            flow=flow_score_val,
            balance_ratio=balance_ratio,
            regrip_count=regrip_count,
            trigger_score=trigger_score,
        ),
    )

    # Get qualitative rating from the primary ergonomic score
    ergonomic_rating = get_ergonomic_rating(ergonomic_score)

    difficulty_classification = classify_algorithm_difficulty(
        ergonomic_score,
        regrip_count,
        flow_score_val,
    )
    suggestions_list = suggest_ergonomic_improvements(
        algorithm,
        regrip_count=regrip_count,
        balance_ratio=balance_ratio,
        flow=flow_score_val,
        fingertrick_comfort=fingertrick_comfort,
    )

    trigger_count = len(trigger_matches)
    trigger_coverage = sum(m.length for m in trigger_matches)
    detected_patterns = tuple(m.pattern.name for m in trigger_matches)

    return ErgonomicsData(
        total_moves=total_moves,
        right_hand_moves=right_hand,
        left_hand_moves=left_hand,
        both_hand_moves=both_hand,
        hand_balance_ratio=balance_ratio,
        regrip_count=regrip_count,
        awkward_moves=awkward_moves,
        estimated_execution_time=execution_time,
        fingertrick_comfort=fingertrick_comfort,
        thumb_moves=thumb,
        index_finger_moves=index,
        middle_finger_moves=middle,
        ring_finger_moves=ring,
        pinky_finger_moves=pinky,
        mixed_finger_moves=mixed_moves,
        ergonomic_rating=ergonomic_rating,
        ergonomic_score=ergonomic_score,
        flow_score=flow_score_val,
        estimated_tps=estimated_tps,
        difficulty_classification=difficulty_classification,
        trigger_count=trigger_count,
        trigger_coverage=trigger_coverage,
        detected_patterns=detected_patterns,
        suggestions=tuple(suggestions_list),
    )
