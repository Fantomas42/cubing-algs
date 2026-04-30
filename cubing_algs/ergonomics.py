"""
Ergonomics analysis tools for Rubik's cube algorithms.

This module provides functions to analyze the ergonomic properties
of algorithms, including hand balance, fingertrick difficulty,
regrip requirements, trigger pattern detection, and overall
execution comfort.
"""
from enum import Enum
from typing import TYPE_CHECKING
from typing import NamedTuple

from cubing_algs.constants import ADJACENT_FACES
from cubing_algs.constants import OPPOSITE_FACES
from cubing_algs.move import Move
from cubing_algs.triggers import TRIGGER_PATTERNS
from cubing_algs.triggers import TriggerMatch

if TYPE_CHECKING:
    from cubing_algs.algorithm import Algorithm  # pragma: no cover


class HandDominance(Enum):
    """Enumeration for hand dominance preferences."""

    RIGHT = 'right'
    LEFT = 'left'
    AMBIDEXTROUS = 'ambidextrous'


class FingerAssignment(Enum):
    """Enumeration for finger assignments in move execution."""

    NONE = 'none'
    THUMB = 'thumb'
    INDEX = 'index'
    MIDDLE = 'middle'
    RING = 'ring'
    PINKY = 'pinky'


class ErgonomicsData(NamedTuple):
    """Container for ergonomics computation results."""

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
    fingertrick_difficulty: float

    # Move type distribution
    thumb_moves: int
    index_finger_moves: int
    middle_finger_moves: int
    ring_finger_moves: int
    pinky_finger_moves: int
    none_finger_moves: int

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
    'R': MoveProperties(HD.RIGHT, FA.THUMB, 1.0),
    "R'": MoveProperties(HD.RIGHT, FA.THUMB, 1.0),
    'R2': MoveProperties(HD.RIGHT, FA.THUMB, 0.95),
    'L': MoveProperties(HD.LEFT, FA.THUMB, 1.0),
    "L'": MoveProperties(HD.LEFT, FA.THUMB, 1.0),
    'L2': MoveProperties(HD.LEFT, FA.THUMB, 0.95),
    'U': MoveProperties(HD.AMBIDEXTROUS, FA.INDEX, 1.0),
    "U'": MoveProperties(HD.AMBIDEXTROUS, FA.INDEX, 1.0),
    'U2': MoveProperties(HD.AMBIDEXTROUS, FA.INDEX, 0.9),
    'D': MoveProperties(HD.LEFT, FA.RING, 0.85),
    "D'": MoveProperties(HD.RIGHT, FA.RING, 0.85),
    'D2': MoveProperties(HD.AMBIDEXTROUS, FA.RING, 0.8),
    'F': MoveProperties(HD.RIGHT, FA.INDEX, 0.8),
    "F'": MoveProperties(HD.LEFT, FA.INDEX, 0.8),
    'F2': MoveProperties(HD.AMBIDEXTROUS, FA.INDEX, 0.75),
    'B': MoveProperties(HD.LEFT, FA.MIDDLE, 0.6),
    "B'": MoveProperties(HD.RIGHT, FA.MIDDLE, 0.6),
    'B2': MoveProperties(HD.AMBIDEXTROUS, FA.MIDDLE, 0.55),
    # Wide Moves — 2 layers
    'Rw': MoveProperties(HD.RIGHT, FA.THUMB, 0.95),
    "Rw'": MoveProperties(HD.RIGHT, FA.THUMB, 0.95),
    'Rw2': MoveProperties(HD.RIGHT, FA.THUMB, 0.9),
    'Lw': MoveProperties(HD.LEFT, FA.THUMB, 0.95),
    "Lw'": MoveProperties(HD.LEFT, FA.THUMB, 0.95),
    'Lw2': MoveProperties(HD.LEFT, FA.THUMB, 0.9),
    'Uw': MoveProperties(HD.AMBIDEXTROUS, FA.INDEX, 0.95),
    "Uw'": MoveProperties(HD.AMBIDEXTROUS, FA.INDEX, 0.95),
    'Uw2': MoveProperties(HD.AMBIDEXTROUS, FA.INDEX, 0.9),
    'Dw': MoveProperties(HD.LEFT, FA.MIDDLE, 0.8),
    "Dw'": MoveProperties(HD.RIGHT, FA.MIDDLE, 0.8),
    'Dw2': MoveProperties(HD.AMBIDEXTROUS, FA.MIDDLE, 0.75),
    'Fw': MoveProperties(HD.RIGHT, FA.INDEX, 0.8),
    "Fw'": MoveProperties(HD.LEFT, FA.INDEX, 0.8),
    'Fw2': MoveProperties(HD.AMBIDEXTROUS, FA.INDEX, 0.75),
    'Bw': MoveProperties(HD.LEFT, FA.MIDDLE, 0.55),
    "Bw'": MoveProperties(HD.RIGHT, FA.MIDDLE, 0.55),
    'Bw2': MoveProperties(HD.AMBIDEXTROUS, FA.MIDDLE, 0.5),
    # Slice Moves
    'M': MoveProperties(HD.RIGHT, FA.THUMB, 0.55),
    "M'": MoveProperties(HD.LEFT, FA.RING, 0.85),
    'M2': MoveProperties(HD.LEFT, FA.RING, 0.8),
    'E': MoveProperties(HD.LEFT, FA.MIDDLE, 0.45),
    "E'": MoveProperties(HD.RIGHT, FA.INDEX, 0.5),
    'E2': MoveProperties(HD.RIGHT, FA.INDEX, 0.45),
    'S': MoveProperties(HD.RIGHT, FA.INDEX, 0.4),
    "S'": MoveProperties(HD.LEFT, FA.INDEX, 0.35),
    'S2': MoveProperties(HD.RIGHT, FA.INDEX, 0.35),
    # Cube Rotations
    'x': MoveProperties(HD.AMBIDEXTROUS, FA.THUMB, 0.4),
    "x'": MoveProperties(HD.AMBIDEXTROUS, FA.THUMB, 0.4),
    'x2': MoveProperties(HD.AMBIDEXTROUS, FA.THUMB, 0.4),
    'y': MoveProperties(HD.AMBIDEXTROUS, FA.THUMB, 0.5),
    "y'": MoveProperties(HD.AMBIDEXTROUS, FA.THUMB, 0.5),
    'y2': MoveProperties(HD.AMBIDEXTROUS, FA.THUMB, 0.35),
    'z': MoveProperties(HD.AMBIDEXTROUS, FA.THUMB, 0.4),
    "z'": MoveProperties(HD.AMBIDEXTROUS, FA.THUMB, 0.4),
    'z2': MoveProperties(HD.AMBIDEXTROUS, FA.THUMB, 0.4),
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

# Suggestion thresholds
REGRIP_RATIO_THRESHOLD = 0.2
BALANCE_THRESHOLD = 0.6
FLOW_THRESHOLD = 0.6
WEIGHT_THRESHOLD = 0.6
ROTATION_RATIO_THRESHOLD = 0.15

TRANSITION_PENALTIES: dict[str, float] = {
    'same_face': 0.0,
    'adjacent': 0.1,
    'hand_switch': 0.15,
    'opposite': 0.3,
    'rotation': 0.5,
}


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


def get_move_ergonomic_weight(
    move: Move,
    hand_dominance: HandDominance = HandDominance.RIGHT,
) -> float:
    """
    Get the ergonomic weight for a single move.

    Returns a value between 0 and 1, where 1 is the most ergonomic.

    Args:
        move: The move to analyze.
        hand_dominance: The hand dominance preference.

    Returns:
        Ergonomic weight from 0.0 to 1.0.

    """
    move_key = get_move_key(move)
    props = MOVE_DATA.get(move_key, DEFAULT_MOVE_PROPERTIES)
    base_weight = props.weight

    if hand_dominance == HandDominance.AMBIDEXTROUS:
        return base_weight

    # Adjust based on hand dominance
    hand = props.hand

    if hand_dominance == HandDominance.LEFT:
        if hand == HandDominance.RIGHT:
            return max(0.0, base_weight * 0.75)
        if hand == HandDominance.LEFT:
            return min(1.0, base_weight * 1.33)

    return base_weight


def get_transition_penalty(move1: Move, move2: Move) -> float:  # noqa: PLR0911
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

    # Adjacent faces are moderate
    if face2 in ADJACENT_FACES.get(face1, ()):
        return TRANSITION_PENALTIES['adjacent']

    # Check for hand switches
    key1 = get_move_key(move1)
    key2 = get_move_key(move2)
    hand1 = MOVE_DATA.get(key1, DEFAULT_MOVE_PROPERTIES).hand
    hand2 = MOVE_DATA.get(key2, DEFAULT_MOVE_PROPERTIES).hand
    if (
        hand1 not in {hand2, HandDominance.AMBIDEXTROUS}
        and hand2 != HandDominance.AMBIDEXTROUS
    ):
        return TRANSITION_PENALTIES['hand_switch']

    return TRANSITION_PENALTIES['adjacent']


def calculate_flow_score(algorithm: 'Algorithm') -> float:
    """
    Calculate the overall flow score of an algorithm.

    Higher scores indicate better flow with fewer awkward transitions.

    Args:
        algorithm: The algorithm to analyze.

    Returns:
        Flow score from 0.0 to 1.0.

    """
    if len(algorithm) <= 1:
        return 1.0

    total_penalty = 0.0
    transition_count = 0

    for i in range(1, len(algorithm)):
        prev_move = algorithm[i - 1]
        curr_move = algorithm[i]

        if not prev_move.is_pause and not curr_move.is_pause:
            total_penalty += get_transition_penalty(prev_move, curr_move)
            transition_count += 1

    if transition_count == 0:
        return 1.0

    avg_penalty = total_penalty / transition_count
    max_possible_penalty = TRANSITION_PENALTIES['rotation']

    return max(0.0, 1.0 - (avg_penalty / max_possible_penalty))


def normalize_algorithm_string(algorithm: 'Algorithm') -> str:
    """
    Convert algorithm to normalized string for pattern matching.

    Returns:
        Space-separated string of non-pause moves.

    """
    from cubing_algs.transform.pause import unpause_moves  # noqa: PLC0415

    return str(algorithm.transform(unpause_moves))


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
    # Left-handed users get a slight bonus for left-hand patterns
    left_bonus = 0.01 if hand_dominance == HandDominance.LEFT else 0.0
    sorted_patterns = sorted(
        TRIGGER_PATTERNS,
        key=lambda p: (
            len(p.moves.split()),
            p.ergonomic_bonus + (left_bonus if 'L' in p.moves else 0.0),
        ),
        reverse=True,
    )

    for pattern in sorted_patterns:
        # Check main pattern and all variations
        patterns_to_check = [pattern.moves, *pattern.variations]

        for pattern_moves in patterns_to_check:
            pattern_list = pattern_moves.split()
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
                    )
                    matches.append(match)

                    used_indices.update(range(i, i + pattern_length))

    return matches


def calculate_trigger_bonus(
    matches: list[TriggerMatch],
) -> tuple[float, float]:
    """
    Calculate ergonomic bonuses from detected trigger patterns.

    Args:
        matches: List of trigger matches to evaluate.

    Returns:
        Tuple of (ergonomic_bonus, speed_multiplier).

    """
    if not matches:
        return 0.0, 1.0

    ergonomic_bonus = sum(m.pattern.ergonomic_bonus for m in matches)

    # Weighted speed multiplier
    total_moves = sum(len(m.matched_moves.split()) for m in matches)
    if total_moves > 0:
        speed_multiplier = (
            sum(
                m.pattern.speed_multiplier * len(m.matched_moves.split())
                for m in matches
            )
            / total_moves
        )
    else:
        speed_multiplier = 1.0

    # Diminishing returns for multiple patterns
    if len(matches) > 1:
        ergonomic_bonus *= 0.9

    # Bonus for multiple triggers
    if len(matches) >= 2:
        ergonomic_bonus += 0.05

    return min(ergonomic_bonus, 0.3), min(speed_multiplier, 1.8)


def estimate_tps_potential(
    algorithm: 'Algorithm',
    hand_dominance: HandDominance = HandDominance.RIGHT,
    *,
    flow: float,
    regrip_count: int,
    balance_ratio: float,
) -> float:
    """
    Estimate the maximum theoretical turns per second for this algorithm.

    Args:
        algorithm: The algorithm to analyze.
        hand_dominance: The hand dominance preference.
        flow: Pre-computed flow score.
        regrip_count: Pre-computed regrip count.
        balance_ratio: Pre-computed hand balance ratio.

    Returns:
        Estimated TPS (typically 2.0-15.0).

    """
    if len(algorithm) == 0:
        return 0.0

    base_tps = 8.0

    move_weights = [
        get_move_ergonomic_weight(move, hand_dominance)
        for move in algorithm
        if not move.is_pause
    ]

    if not move_weights:
        return base_tps

    avg_weight = sum(move_weights) / len(move_weights)
    non_pause_count = len(move_weights)

    weight_multiplier = avg_weight
    flow_multiplier = 0.7 + (0.3 * flow)
    regrip_penalty = max(0.8, 1.0 - (regrip_count / non_pause_count * 2))
    balance_bonus = 0.9 + (0.2 * balance_ratio)

    estimated_tps = (
        base_tps
        * weight_multiplier
        * flow_multiplier
        * regrip_penalty
        * balance_bonus
    )

    return max(2.0, min(15.0, estimated_tps))


def calculate_ergonomic_score(
    algorithm: 'Algorithm',
    hand_dominance: HandDominance = HandDominance.RIGHT,
    *,
    flow: float,
    balance_ratio: float,
    regrip_count: int,
) -> float:
    """
    Calculate an overall ergonomic score for the algorithm.

    Combines multiple ergonomic factors into a single score.

    Args:
        algorithm: The algorithm to analyze.
        hand_dominance: The hand dominance preference.
        flow: Pre-computed flow score.
        balance_ratio: Pre-computed hand balance ratio.
        regrip_count: Pre-computed regrip count.

    Returns:
        Ergonomic score from 0.0 to 1.0.

    """
    if len(algorithm) == 0:
        return 1.0

    move_weights = [
        get_move_ergonomic_weight(move, hand_dominance)
        for move in algorithm
        if not move.is_pause
    ]

    if not move_weights:
        return 1.0

    avg_move_score = sum(move_weights) / len(move_weights)
    hand_balance = balance_ratio * 2  # Convert 0-0.5 range to 0-1
    regrip_score = max(0.0, 1.0 - (regrip_count / len(move_weights)))

    return max(
        0.0,
        min(
            1.0,
            avg_move_score * 0.4
            + flow * 0.3
            + hand_balance * 0.15
            + regrip_score * 0.15,
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
) -> list[str]:
    """
    Suggest specific improvements to make the algorithm more ergonomic.

    Args:
        algorithm: The algorithm to analyze.
        regrip_count: Pre-computed regrip count.
        balance_ratio: Pre-computed hand balance ratio.
        flow: Pre-computed flow score.

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
            'Consider reducing cube rotations to minimize regrips',
        )

    if balance_ratio * 2 < BALANCE_THRESHOLD:
        suggestions.append('Try to balance moves between both hands')

    if flow < FLOW_THRESHOLD:
        suggestions.append(
            'Look for alternatives to reduce awkward move transitions',
        )

    move_weights = [
        get_move_ergonomic_weight(move)
        for move in algorithm
        if not move.is_pause
    ]
    avg_weight = sum(move_weights) / len(move_weights) if move_weights else 1.0
    if avg_weight < WEIGHT_THRESHOLD:
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

    # Calculate balance ratio
    # (0.5 is perfect balance, closer to 0 or 1 is imbalanced)
    total_handed = right_count + left_count
    if total_handed == 0:
        balance_ratio = 0.5
    else:
        balance_ratio = min(right_count, left_count) / total_handed

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
        elif finger == FingerAssignment.NONE:
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
    prev_move = None

    for move in moves:
        if move.is_rotation_move:
            regrip_count += 1
            continue

        opposite = TRANSITION_PENALTIES['opposite']
        high_penalty = (
            not move.is_rotation_move
            and prev_move is not None
            and get_transition_penalty(prev_move, move) >= opposite
        )

        if high_penalty:
            regrip_count += 1

        prev_move = move

    return regrip_count


def compute_fingertrick_difficulty(
    moves: 'Algorithm',
    hand_dominance: HandDominance = HandDominance.RIGHT,
) -> float:
    """
    Calculate overall fingertrick difficulty score.

    Based on ergonomic weights where higher difficulty means harder
    execution (inverted from weight scale).

    Args:
        moves: 'Algorithm' to analyze.
        hand_dominance: The hand dominance preference.

    Returns:
        Difficulty score from 0.0 (easiest) to 1.0 (hardest).

    """
    if not moves:
        return 0.0

    total_weight = 0.0
    move_count = 0

    for move in moves:
        if move.is_pause:
            continue

        weight = get_move_ergonomic_weight(move, hand_dominance)
        total_weight += weight
        move_count += 1

    if move_count == 0:
        return 0.0

    avg_weight = total_weight / move_count
    return 1.0 - avg_weight


def compute_estimated_execution_time(
    moves: 'Algorithm',
    regrip_count: int,
) -> float:
    """
    Estimate algorithm execution time in seconds.

    Based on average move times and regrip penalties.

    Args:
        moves: 'Algorithm' to analyze.
        regrip_count: Number of regrips in the algorithm.

    Returns:
        Estimated execution time in seconds.

    """
    if not moves:
        return 0.0

    # Base execution times (in seconds)
    base_move_time = 0.15  # Average time per move for experienced speedcuber
    regrip_penalty = 0.07  # Additional time per regrip

    non_pause_moves = sum(1 for move in moves if not move.is_pause)

    return (non_pause_moves * base_move_time) + (regrip_count * regrip_penalty)


def get_ergonomic_rating(ergonomic_score: float) -> str:
    """
    Convert ergonomic score to ergonomic rating.

    Args:
        ergonomic_score: Ergonomic score from 0.0 to 1.0.

    Returns:
        Human-readable rating string (Excellent, Good, Fair, Poor, Very Poor).

    """
    if ergonomic_score >= 0.80:  # noqa: PLR2004
        return 'Excellent'
    if ergonomic_score >= 0.65:  # noqa: PLR2004
        return 'Good'
    if ergonomic_score >= 0.50:  # noqa: PLR2004
        return 'Fair'
    if ergonomic_score >= 0.35:  # noqa: PLR2004
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
            hand_balance_ratio=0.5,
            regrip_count=0,
            awkward_moves=0,
            estimated_execution_time=0.0,
            fingertrick_difficulty=0.0,
            thumb_moves=0,
            index_finger_moves=0,
            middle_finger_moves=0,
            ring_finger_moves=0,
            pinky_finger_moves=0,
            none_finger_moves=0,
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
    thumb, index, middle, ring, pinky, none_moves = compute_finger_distribution(
        algorithm,
    )

    # Calculate difficulty metrics
    regrip_count = compute_regrip_count(algorithm)
    fingertrick_difficulty = compute_fingertrick_difficulty(
        algorithm,
        hand_dominance,
    )

    # Count awkward moves (those with low ergonomic weight)
    awkward_moves = sum(
        1
        for move in algorithm
        if not move.is_pause
        and get_move_ergonomic_weight(move, hand_dominance) < AWKWARD_THRESHOLD
    )

    # Calculate execution time
    execution_time = compute_estimated_execution_time(algorithm, regrip_count)

    # Advanced metrics
    flow_score_val = calculate_flow_score(algorithm)
    base_ergonomic_score = calculate_ergonomic_score(
        algorithm,
        hand_dominance,
        flow=flow_score_val,
        balance_ratio=balance_ratio,
        regrip_count=regrip_count,
    )

    trigger_matches = find_trigger_patterns(algorithm, hand_dominance)
    trigger_bonus, speed_mult = calculate_trigger_bonus(trigger_matches)
    ergonomic_score = min(1.0, base_ergonomic_score + trigger_bonus)

    # Get qualitative rating from the primary ergonomic score
    ergonomic_rating = get_ergonomic_rating(ergonomic_score)

    estimated_tps = estimate_tps_potential(
        algorithm,
        hand_dominance,
        flow=flow_score_val,
        regrip_count=regrip_count,
        balance_ratio=balance_ratio,
    )
    estimated_tps = max(2.0, min(15.0, estimated_tps * speed_mult))

    difficulty_classification = classify_algorithm_difficulty(
        base_ergonomic_score,
        regrip_count,
        flow_score_val,
    )
    suggestions_list = suggest_ergonomic_improvements(
        algorithm,
        regrip_count=regrip_count,
        balance_ratio=balance_ratio,
        flow=flow_score_val,
    )

    trigger_count = len(trigger_matches)
    trigger_coverage = sum(
        len(m.matched_moves.split()) for m in trigger_matches
    )
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
        fingertrick_difficulty=fingertrick_difficulty,
        thumb_moves=thumb,
        index_finger_moves=index,
        middle_finger_moves=middle,
        ring_finger_moves=ring,
        pinky_finger_moves=pinky,
        none_finger_moves=none_moves,
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
