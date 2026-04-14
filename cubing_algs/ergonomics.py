"""
Ergonomics analysis tools for Rubik's cube algorithms.

This module provides functions to analyze the ergonomic properties
of algorithms, including hand balance, fingertrick difficulty,
regrip requirements, trigger pattern detection, and overall
execution comfort.
"""
from dataclasses import dataclass
from enum import Enum
from typing import TYPE_CHECKING
from typing import NamedTuple

from cubing_algs.constants import ADJACENT_FACES
from cubing_algs.constants import OPPOSITE_FACES
from cubing_algs.move import Move

if TYPE_CHECKING:
    from cubing_algs.algorithm import Algorithm  # pragma: no cover


class HandDominance(Enum):
    """Enumeration for hand dominance preferences."""

    RIGHT = 'right'
    LEFT = 'left'
    AMBIDEXTROUS = 'ambidextrous'


@dataclass
class TriggerPattern:
    """
    Represents a common speedcubing trigger or pattern.

    Triggers are familiar move sequences that speedcubers can execute
    efficiently due to muscle memory and ergonomic flow.
    """

    name: str
    moves: str
    category: str
    ergonomic_bonus: float
    speed_multiplier: float
    variations: list[str]

    def __post_init__(self) -> None:
        """Normalize the moves string and variations."""
        self.moves = ' '.join(self.moves.split())
        self.variations = [' '.join(var.split()) for var in self.variations]


class TriggerMatch(NamedTuple):
    """Represents a detected trigger pattern in an algorithm."""

    pattern: 'TriggerPattern'
    start_index: int
    end_index: int
    matched_moves: str


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
    flow_breaks: int

    # Execution metrics
    estimated_execution_time: float
    fingertrick_difficulty: float

    # Move type distribution
    thumb_moves: int
    index_finger_moves: int
    middle_finger_moves: int
    ring_finger_moves: int

    # Comfort metrics
    comfort_score: float
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


# Common speedcubing triggers and patterns
TRIGGER_PATTERNS = [
    # Basic triggers (highest priority)
    TriggerPattern(
        name='Sexy Move',
        moves="R U R' U'",
        category='basic',
        ergonomic_bonus=0.15,
        speed_multiplier=1.3,
        variations=["L U L' U'", "R U' R' U", "L U' L' U"],
    ),
    TriggerPattern(
        name='Sledgehammer',
        moves="R' F R F'",
        category='basic',
        ergonomic_bonus=0.12,
        speed_multiplier=1.25,
        variations=["L' F L F'", "R' D R D'", "L' D L D'"],
    ),
    TriggerPattern(
        name='Sune Trigger',
        moves="R U R' U",
        category='basic',
        ergonomic_bonus=0.10,
        speed_multiplier=1.2,
        variations=["L U L' U", "R U' R' U'", "L U' L' U'"],
    ),
    TriggerPattern(
        name='Anti-Sune Trigger',
        moves="R U' R' U'",
        category='basic',
        ergonomic_bonus=0.10,
        speed_multiplier=1.2,
        variations=["L U' L' U'", "R U R' U", "L U L' U"],
    ),

    # Compound triggers
    TriggerPattern(
        name='Sexy + Sledge',
        moves="R U R' U' R' F R F'",
        category='compound',
        ergonomic_bonus=0.18,
        speed_multiplier=1.4,
        variations=["L U L' U' L' F L F'"],
    ),
    TriggerPattern(
        name='Double Sexy',
        moves="R U R' U' R U R' U'",
        category='compound',
        ergonomic_bonus=0.20,
        speed_multiplier=1.45,
        variations=["L U L' U' L U L' U'"],
    ),
    TriggerPattern(
        name='Sune',
        moves="R U R' U R U2 R'",
        category='OLL',
        ergonomic_bonus=0.14,
        speed_multiplier=1.3,
        variations=["L U L' U L U2 L'"],
    ),
    TriggerPattern(
        name='Anti-Sune',
        moves="R U2 R' U' R U' R'",
        category='OLL',
        ergonomic_bonus=0.14,
        speed_multiplier=1.3,
        variations=["L U2 L' U' L U' L'"],
    ),
    TriggerPattern(
        name='T-Perm Trigger',
        moves="R U R' F'",
        category='basic',
        ergonomic_bonus=0.08,
        speed_multiplier=1.15,
        variations=["L U L' F"],
    ),
    TriggerPattern(
        name='Niklas',
        moves="R U' L' U R' U' L U",
        category='advanced',
        ergonomic_bonus=0.16,
        speed_multiplier=1.35,
        variations=["L U' R' U L' U' R U"],
    ),

    # Setup patterns
    TriggerPattern(
        name='Right Insert',
        moves="R U R'",
        category='setup',
        ergonomic_bonus=0.06,
        speed_multiplier=1.1,
        variations=["L U L'", "R U' R'", "L U' L'"],
    ),
    TriggerPattern(
        name='Extended Insert',
        moves="R U2 R'",
        category='setup',
        ergonomic_bonus=0.05,
        speed_multiplier=1.05,
        variations=["L U2 L'"],
    ),

    # Wide move patterns
    TriggerPattern(
        name='Wide Sexy',
        moves="r U r' U'",
        category='wide',
        ergonomic_bonus=0.12,
        speed_multiplier=1.2,
        variations=["l U l' U'", "r U' r' U"],
    ),
]


# Hand assignment for different move types based on speedcubing conventions
HAND_ASSIGNMENTS: dict[str, str] = {
    # Right hand dominant moves
    'R': 'right', "R'": 'right', 'R2': 'right',
    'Rw': 'right', "Rw'": 'right', 'Rw2': 'right',
    'r': 'right', "r'": 'right', 'r2': 'right',
    'F': 'right', "F'": 'right', 'F2': 'right',
    'Fw': 'right', "Fw'": 'right', 'Fw2': 'right',
    'f': 'right', "f'": 'right', 'f2': 'right',

    # Left hand dominant moves
    'L': 'left', "L'": 'left', 'L2': 'left',
    'Lw': 'left', "Lw'": 'left', 'Lw2': 'left',
    'l': 'left', "l'": 'left', 'l2': 'left',
    'B': 'left', "B'": 'left', 'B2': 'left',
    'Bw': 'left', "Bw'": 'left', 'Bw2': 'left',
    'b': 'left', "b'": 'left', 'b2': 'left',

    # Both hands (U and D moves)
    'U': 'both', "U'": 'both', 'U2': 'both',
    'Uw': 'both', "Uw'": 'both', 'Uw2': 'both',
    'u': 'both', "u'": 'both', 'u2': 'both',
    'D': 'both', "D'": 'both', 'D2': 'both',
    'Dw': 'both', "Dw'": 'both', 'Dw2': 'both',
    'd': 'both', "d'": 'both', 'd2': 'both',

    # Slice moves (typically awkward)
    'M': 'both', "M'": 'both', 'M2': 'both',
    'E': 'both', "E'": 'both', 'E2': 'both',
    'S': 'both', "S'": 'both', 'S2': 'both',

    'x': 'both', "x'": 'both', 'x2': 'both',
    'y': 'both', "y'": 'both', 'y2': 'both',
    'z': 'both', "z'": 'both', 'z2': 'both',
}

# Finger assignments for different moves
FINGER_ASSIGNMENTS: dict[str, str] = {
    # Thumb moves (generally comfortable)
    'R': 'thumb', "R'": 'thumb', 'R2': 'thumb',
    'L': 'thumb', "L'": 'thumb', 'L2': 'thumb',

    # Index finger moves (most common U moves)
    'U': 'index', "U'": 'index', 'U2': 'index',
    'D': 'index', "D'": 'index', 'D2': 'index',

    # Middle finger moves
    'F': 'middle', "F'": 'middle', 'F2': 'middle',
    'B': 'middle', "B'": 'middle', 'B2': 'middle',

    # Ring finger moves (slice moves, generally awkward)
    'M': 'ring', "M'": 'ring', 'M2': 'ring',
    'E': 'ring', "E'": 'ring', 'E2': 'ring',
    'S': 'ring', "S'": 'ring', 'S2': 'ring',
}

# Ergonomic weights for different move types (0-1, higher = more ergonomic)
ERGONOMIC_WEIGHTS: dict[str, float] = {
    # Outer face moves - Right hand dominant moves (most natural)
    'R': 1.0, "R'": 1.0, 'R2': 0.95,
    'U': 1.0, "U'": 1.0, 'U2': 0.9,
    'F': 0.85, "F'": 0.85, 'F2': 0.8,

    # Left hand moves (less natural for most right-handed cubers)
    'L': 0.75, "L'": 0.75, 'L2': 0.7,
    'D': 0.6, "D'": 0.6, 'D2': 0.55,
    'B': 0.5, "B'": 0.5, 'B2': 0.45,

    # Slice moves
    'M': 0.7, "M'": 0.7, 'M2': 0.65,
    'S': 0.6, "S'": 0.6, 'S2': 0.55,
    'E': 0.5, "E'": 0.5, 'E2': 0.45,

    # Cube rotations
    'x': 0.4, "x'": 0.4, 'x2': 0.35,
    'y': 0.6, "y'": 0.6, 'y2': 0.55,
    'z': 0.35, "z'": 0.35, 'z2': 0.3,

    # Wide moves (SiGN notation)
    'r': 0.8, "r'": 0.8, 'r2': 0.75,
    'u': 0.85, "u'": 0.85, 'u2': 0.8,
    'f': 0.7, "f'": 0.7, 'f2': 0.65,
    'l': 0.65, "l'": 0.65, 'l2': 0.6,
    'd': 0.55, "d'": 0.55, 'd2': 0.5,
    'b': 0.45, "b'": 0.45, 'b2': 0.4,

    # Wide moves (standard notation)
    'Rw': 0.8, "Rw'": 0.8, 'Rw2': 0.75,
    'Uw': 0.85, "Uw'": 0.85, 'Uw2': 0.8,
    'Fw': 0.7, "Fw'": 0.7, 'Fw2': 0.65,
    'Lw': 0.65, "Lw'": 0.65, 'Lw2': 0.6,
    'Dw': 0.55, "Dw'": 0.55, 'Dw2': 0.5,
    'Bw': 0.45, "Bw'": 0.45, 'Bw2': 0.4,
}

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
    base_weight = ERGONOMIC_WEIGHTS.get(move_key, 0.5)

    if hand_dominance == HandDominance.AMBIDEXTROUS:
        return base_weight

    # Adjust based on hand dominance
    hand = HAND_ASSIGNMENTS.get(move_key, 'both')

    if hand_dominance == HandDominance.LEFT:
        if hand == 'right':
            return max(0.0, base_weight * 0.75)
        if hand == 'left':
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
    if face2 in ADJACENT_FACES.get(face1, set()):
        return TRANSITION_PENALTIES['adjacent']

    # Check for hand switches
    key1 = get_move_key(move1)
    key2 = get_move_key(move2)
    hand1 = HAND_ASSIGNMENTS.get(key1, 'both')
    hand2 = HAND_ASSIGNMENTS.get(key2, 'both')
    if hand1 not in {hand2, 'both'} and hand2 != 'both':
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
                if any(idx in used_indices
                       for idx in range(i, i + pattern_length)):
                    continue

                window = algorithm_moves[i:i + pattern_length]
                if window == pattern_list:
                    match = TriggerMatch(
                        pattern=pattern,
                        start_index=i,
                        end_index=i + pattern_length - 1,
                        matched_moves=' '.join(window),
                    )
                    matches.append(match)

                    used_indices.update(range(i, i + pattern_length))

                    break  # Move to next pattern

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
        speed_multiplier = sum(
            m.pattern.speed_multiplier * len(m.matched_moves.split())
            for m in matches
        ) / total_moves
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
) -> float:
    """
    Estimate the maximum theoretical turns per second for this algorithm.

    Args:
        algorithm: The algorithm to analyze.
        hand_dominance: The hand dominance preference.

    Returns:
        Estimated TPS (typically 2.0-15.0).

    """
    if len(algorithm) == 0:
        return 0.0

    base_tps = 8.0

    move_weights = [
        get_move_ergonomic_weight(move, hand_dominance)
        for move in algorithm if not move.is_pause
    ]

    if not move_weights:
        return base_tps

    avg_weight = sum(move_weights) / len(move_weights)
    flow = calculate_flow_score(algorithm)
    regrips = compute_regrip_count(algorithm)
    non_pause_count = len(move_weights)

    _, _, _, balance_ratio = compute_hand_balance(algorithm)

    weight_multiplier = avg_weight
    flow_multiplier = 0.7 + (0.3 * flow)
    regrip_penalty = max(0.8, 1.0 - (regrips / non_pause_count * 2))
    balance_bonus = 0.9 + (0.2 * balance_ratio)

    estimated_tps = (
        base_tps * weight_multiplier * flow_multiplier
        * regrip_penalty * balance_bonus
    )

    return max(2.0, min(15.0, estimated_tps))


def calculate_ergonomic_score(
    algorithm: 'Algorithm',
    hand_dominance: HandDominance = HandDominance.RIGHT,
) -> float:
    """
    Calculate an overall ergonomic score for the algorithm.

    Combines multiple ergonomic factors into a single score.

    Args:
        algorithm: The algorithm to analyze.
        hand_dominance: The hand dominance preference.

    Returns:
        Ergonomic score from 0.0 to 1.0.

    """
    if len(algorithm) == 0:
        return 1.0

    move_weights = [
        get_move_ergonomic_weight(move, hand_dominance)
        for move in algorithm if not move.is_pause
    ]

    if not move_weights:
        return 1.0

    avg_move_score = sum(move_weights) / len(move_weights)
    flow = calculate_flow_score(algorithm)

    _, _, _, balance_ratio = compute_hand_balance(algorithm)
    hand_balance = balance_ratio * 2  # Convert 0-0.5 range to 0-1

    regrips = compute_regrip_count(algorithm)
    regrip_score = max(0.0, 1.0 - (regrips / len(move_weights)))

    return max(0.0, min(1.0,
        avg_move_score * 0.4
        + flow * 0.3
        + hand_balance * 0.15
        + regrip_score * 0.15,
    ))


def classify_algorithm_difficulty(
    algorithm: 'Algorithm',
    hand_dominance: HandDominance = HandDominance.RIGHT,
) -> str:
    """
    Classify the algorithm into difficulty categories based on ergonomics.

    Args:
        algorithm: The algorithm to classify.
        hand_dominance: The hand dominance preference.

    Returns:
        One of: 'Beginner', 'Intermediate', 'Advanced', 'Expert'.

    """
    score = calculate_ergonomic_score(algorithm, hand_dominance)
    regrips = compute_regrip_count(algorithm)
    flow = calculate_flow_score(algorithm)

    if (score >= BEGINNER_SCORE
            and regrips <= BEGINNER_REGRIPS and flow >= BEGINNER_FLOW):
        return 'Beginner'
    if (score >= INTERMEDIATE_SCORE
            and regrips <= INTERMEDIATE_REGRIPS
            and flow >= INTERMEDIATE_FLOW):
        return 'Intermediate'
    if score >= ADVANCED_SCORE and regrips <= ADVANCED_REGRIPS:
        return 'Advanced'
    return 'Expert'


def suggest_ergonomic_improvements(algorithm: 'Algorithm') -> list[str]:
    """
    Suggest specific improvements to make the algorithm more ergonomic.

    Args:
        algorithm: The algorithm to analyze.

    Returns:
        List of improvement suggestions.

    """
    if len(algorithm) == 0:
        return []

    suggestions: list[str] = []

    regrips = compute_regrip_count(algorithm)
    non_pause_count = sum(1 for m in algorithm if not m.is_pause)

    if non_pause_count == 0:
        return []

    if regrips > non_pause_count * REGRIP_RATIO_THRESHOLD:
        suggestions.append(
            'Consider reducing cube rotations to minimize regrips',
        )

    _, _, _, balance_ratio = compute_hand_balance(algorithm)
    if balance_ratio * 2 < BALANCE_THRESHOLD:
        suggestions.append('Try to balance moves between both hands')

    flow = calculate_flow_score(algorithm)
    if flow < FLOW_THRESHOLD:
        suggestions.append(
            'Look for alternatives to reduce awkward move transitions',
        )

    move_weights = [
        get_move_ergonomic_weight(move)
        for move in algorithm if not move.is_pause
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
        hand = HAND_ASSIGNMENTS.get(move_key, 'both')

        if hand == 'right':
            right_count += 1
        elif hand == 'left':
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
) -> tuple[int, int, int, int]:
    """
    Calculate finger usage distribution for the algorithm.

    Args:
        moves: 'Algorithm' to analyze.

    Returns:
        Tuple of (thumb_count, index_count, middle_count, ring_count).

    """
    thumb_count = 0
    index_count = 0
    middle_count = 0
    ring_count = 0

    for move in moves:
        if move.is_pause:
            continue

        move_key = get_move_key(move)
        finger = FINGER_ASSIGNMENTS.get(move_key, 'index')  # Default to index

        if finger == 'thumb':
            thumb_count += 1
        elif finger == 'index':
            index_count += 1
        elif finger == 'middle':
            middle_count += 1
        elif finger == 'ring':
            ring_count += 1

    return thumb_count, index_count, middle_count, ring_count


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
    regrip_count = 0

    for i, move in enumerate(moves):
        if move.is_pause:
            continue

        # Rotations always require regrip
        if move.is_rotation_move:
            regrip_count += 1
            continue

        # Check transition from previous non-pause move
        if i > 0:
            prev_move = moves[i - 1]
            if not prev_move.is_pause:
                penalty = get_transition_penalty(prev_move, move)
                if penalty >= TRANSITION_PENALTIES['opposite']:
                    regrip_count += 1

    return regrip_count


def compute_flow_breaks(moves: 'Algorithm') -> int:
    """
    Count awkward transitions that break the flow of execution.

    Uses transition penalty system to detect difficult transitions.

    Args:
        moves: 'Algorithm' to analyze.

    Returns:
        Number of awkward transitions detected.

    """
    if len(moves) < 2:
        return 0

    flow_breaks = 0
    prev_move = None

    for move in moves:
        if move.is_pause:
            continue

        if prev_move is not None:
            penalty = get_transition_penalty(prev_move, move)
            if penalty >= TRANSITION_PENALTIES['opposite']:
                flow_breaks += 1

        prev_move = move

    return flow_breaks


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


def compute_comfort_score(
    hand_balance_ratio: float,
    fingertrick_difficulty: float,
    regrip_count: int,
    flow_breaks: int,
    total_moves: int,
) -> float:
    """
    Calculate overall comfort score (0-100, higher is better).

    Combines various ergonomic factors into a single score.

    Args:
        hand_balance_ratio: Hand balance ratio from compute_hand_balance.
        fingertrick_difficulty: Difficulty score (0-1) from
            compute_fingertrick_difficulty.
        regrip_count: Number of regrips in the algorithm.
        flow_breaks: Number of awkward transitions.
        total_moves: Total number of moves in the algorithm.

    Returns:
        Comfort score from 0 to 100 (higher is more comfortable).

    """
    if total_moves == 0:
        return 100.0

    # Hand balance component (0-25 points)
    balance_score = hand_balance_ratio * 25

    # Difficulty component (0-25 points, inverted)
    difficulty_score = max(0, 25 - (fingertrick_difficulty * 25))

    # Regrip component (0-25 points, fewer regrips is better)
    regrip_ratio = min(1.0, regrip_count / total_moves)
    regrip_score = max(0, 25 - (regrip_ratio * 25))

    # Flow component (0-25 points, fewer breaks is better)
    flow_ratio = min(1.0, flow_breaks / max(1, total_moves - 1))
    flow_score = max(0, 25 - (flow_ratio * 25))

    return balance_score + difficulty_score + regrip_score + flow_score


def get_ergonomic_rating(comfort_score: float) -> str:
    """
    Convert comfort score to ergonomic rating.

    Args:
        comfort_score: Comfort score from 0 to 100.

    Returns:
        Human-readable rating string (Excellent, Good, Fair, Poor, Very Poor).

    """
    if comfort_score >= 80:
        return 'Excellent'
    if comfort_score >= 65:
        return 'Good'
    if comfort_score >= 50:
        return 'Fair'
    if comfort_score >= 35:
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
            flow_breaks=0,
            estimated_execution_time=0.0,
            fingertrick_difficulty=0.0,
            thumb_moves=0,
            index_finger_moves=0,
            middle_finger_moves=0,
            ring_finger_moves=0,
            comfort_score=100.0,
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
    thumb, index, middle, ring = compute_finger_distribution(algorithm)

    # Calculate difficulty metrics
    regrip_count = compute_regrip_count(algorithm)
    flow_breaks = compute_flow_breaks(algorithm)
    fingertrick_difficulty = compute_fingertrick_difficulty(
        algorithm, hand_dominance,
    )

    # Count awkward moves (those with low ergonomic weight)
    awkward_moves = sum(
        1 for move in algorithm
        if not move.is_pause
        and get_move_ergonomic_weight(move, hand_dominance) < AWKWARD_THRESHOLD
    )

    # Calculate execution time
    execution_time = compute_estimated_execution_time(algorithm, regrip_count)

    # Calculate overall comfort score
    comfort_score = compute_comfort_score(
        balance_ratio,
        fingertrick_difficulty,
        regrip_count,
        flow_breaks,
        total_moves,
    )

    # Get qualitative rating
    ergonomic_rating = get_ergonomic_rating(comfort_score)

    # Advanced metrics
    flow_score_val = calculate_flow_score(algorithm)
    ergonomic_score = calculate_ergonomic_score(algorithm, hand_dominance)

    trigger_matches = find_trigger_patterns(algorithm, hand_dominance)
    trigger_bonus, speed_mult = calculate_trigger_bonus(trigger_matches)
    ergonomic_score = min(1.0, ergonomic_score + trigger_bonus)

    estimated_tps = estimate_tps_potential(algorithm, hand_dominance)
    estimated_tps = max(2.0, min(15.0, estimated_tps * speed_mult))

    difficulty_classification = classify_algorithm_difficulty(
        algorithm, hand_dominance,
    )
    suggestions_list = suggest_ergonomic_improvements(algorithm)

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
        flow_breaks=flow_breaks,
        estimated_execution_time=execution_time,
        fingertrick_difficulty=fingertrick_difficulty,
        thumb_moves=thumb,
        index_finger_moves=index,
        middle_finger_moves=middle,
        ring_finger_moves=ring,
        comfort_score=comfort_score,
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
