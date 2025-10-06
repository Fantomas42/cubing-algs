"""
Ergonomics analysis tools for Rubik's cube algorithms.

This module provides functions to analyze the ergonomic properties
of algorithms, including hand balance, fingertrick difficulty,
regrip requirements, and overall execution comfort.
"""
from typing import TYPE_CHECKING
from typing import NamedTuple

from cubing_algs.move import Move

if TYPE_CHECKING:
    from cubing_algs.algorithm import Algorithm  # pragma: no cover


class ErgonomicsData(NamedTuple):
    """
    Container for ergonomics computation results.
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


# Hand assignment for different move types based on speedcubing conventions
HAND_ASSIGNMENTS = {
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
FINGER_ASSIGNMENTS = {
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

# Difficulty ratings for different move types
MOVE_DIFFICULTY = {
    # Easy moves
    'R': 1.0, "R'": 1.0, 'R2': 1.2,
    'L': 1.0, "L'": 1.0, 'L2': 1.2,
    'U': 1.0, "U'": 1.0, 'U2': 1.1,
    'D': 1.1, "D'": 1.1, 'D2': 1.3,
    'F': 1.2, "F'": 1.2, 'F2': 1.4,
    'B': 1.3, "B'": 1.3, 'B2': 1.5,

    # Wide moves (slightly harder)
    'Rw': 1.1, "Rw'": 1.1, 'Rw2': 1.3,
    'Lw': 1.1, "Lw'": 1.1, 'Lw2': 1.3,
    'Uw': 1.1, "Uw'": 1.1, 'Uw2': 1.2,
    'Dw': 1.2, "Dw'": 1.2, 'Dw2': 1.4,
    'Fw': 1.3, "Fw'": 1.3, 'Fw2': 1.5,
    'Bw': 1.4, "Bw'": 1.4, 'Bw2': 1.6,

    # Slice moves (awkward)
    'M': 1.5, "M'": 1.5, 'M2': 1.8,
    'E': 1.6, "E'": 1.6, 'E2': 1.9,
    'S': 1.7, "S'": 1.7, 'S2': 2.0,

    'x': 1.0, "x'": 1.0, 'x2': 1.1,
    'y': 1.0, "y'": 1.0, 'y2': 1.1,
    'z': 1.1, "z'": 1.1, 'z2': 1.2,
}

# Threshold for considering a move awkward
AWKWARD_THRESHOLD = 1.4

# Moves that typically require regrips
REGRIP_MOVES = {
    'B', "B'", 'B2', 'Bw', "Bw'", 'Bw2', 'b', "b'", 'b2',
    'D', "D'", 'D2', 'Dw', "Dw'", 'Dw2', 'd', "d'", 'd2',
    'E', "E'", 'E2', 'S', "S'", 'S2',
}

# Move pairs that create flow breaks (awkward transitions)
AWKWARD_TRANSITIONS = {
    ('R', 'L'), ('L', 'R'), ("R'", "L'"), ("L'", "R'"),
    ('F', 'B'), ('B', 'F'), ("F'", "B'"), ("B'", "F'"),
    ('M', 'R'), ('R', 'M'), ("M'", "R'"), ("R'", "M'"),
    ('M', 'L'), ('L', 'M'), ("M'", "L'"), ("L'", "M'"),
}


def get_move_key(move: Move) -> str:
    """
    Get the standardized key for move lookup.

    Handles SiGN notation and layered moves by converting them
    to their base equivalents.
    """
    if move.is_pause or move.is_rotation_move:
        return str(move)

    # Convert SiGN notation to standard
    if move.is_sign_move:
        move = move.to_standard

    # Get unlayered version for lookup
    base_move = move.unlayered

    return str(base_move)


def compute_hand_balance(moves: 'Algorithm') -> tuple[int, int, int, float]:
    """
    Calculate hand balance metrics for the algorithm.
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


def compute_finger_distribution(moves: 'Algorithm') -> tuple[
        int, int, int, int]:
    """
    Calculate finger usage distribution for the algorithm.
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

    Based on moves that typically require grip changes.
    """
    regrip_count = 0

    for move in moves:
        if move.is_pause:
            continue

        move_key = get_move_key(move)
        if any(regrip_move in move_key for regrip_move in REGRIP_MOVES):
            regrip_count += 1

    return regrip_count


def compute_flow_breaks(moves: 'Algorithm') -> int:
    """
    Count awkward transitions that break the flow of execution.

    Based on move sequences that are difficult to execute smoothly.
    """
    if len(moves) < 2:
        return 0

    flow_breaks = 0
    prev_move = None

    for move in moves:
        if move.is_pause:
            continue

        if prev_move is not None:
            # Get base move only
            prev_key = get_move_key(prev_move).split("'")[0].split('2')[0]
            curr_key = get_move_key(move).split("'")[0].split('2')[0]

            if (prev_key, curr_key) in AWKWARD_TRANSITIONS:
                flow_breaks += 1

        prev_move = move

    return flow_breaks


def compute_fingertrick_difficulty(moves: 'Algorithm') -> float:
    """
    Calculate overall fingertrick difficulty score.

    Based on individual move difficulties and sequence complexity.
    """
    if not moves:
        return 0.0

    total_difficulty = 0.0
    move_count = 0

    for move in moves:
        if move.is_pause:
            continue

        move_key = get_move_key(move)
        difficulty = MOVE_DIFFICULTY.get(move_key, 1.0)
        total_difficulty += difficulty
        move_count += 1

    return total_difficulty / move_count if move_count > 0 else 0.0


def compute_estimated_execution_time(moves: 'Algorithm',
                                     regrip_count: int) -> float:
    """
    Estimate algorithm execution time in seconds.

    Based on average move times and regrip penalties.
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
    """
    if total_moves == 0:
        return 100.0

    # Hand balance component (0-25 points)
    balance_score = hand_balance_ratio * 25

    # Difficulty component (0-25 points, inverted)
    max_difficulty = 2.0  # Maximum expected difficulty
    difficulty_score = max(
        0, 25 - (fingertrick_difficulty / max_difficulty * 25),
    )

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


def compute_ergonomics(algorithm: 'Algorithm') -> ErgonomicsData:  # noqa: PLR0914
    """
    Compute comprehensive ergonomics metrics for an algorithm.

    This function analyzes various aspects of algorithm ergonomics including:
    - Hand balance and coordination requirements
    - Fingertrick difficulty and execution comfort
    - Regrip requirements and flow interruptions
    - Estimated execution time and overall comfort rating

    Returns:
        ErgonomicsData: Namedtuple containing all calculated ergonomic metrics:
            - total_moves: Total number of moves (excluding pauses)
            - right_hand_moves: Number of right-hand dominant moves
            - left_hand_moves: Number of left-hand dominant moves
            - both_hand_moves: Number of moves requiring both hands
            - hand_balance_ratio: Hand balance (0.5 is perfect,
              closer to 0/1 is imbalanced)
            - regrip_count: Estimated number of regrips required
            - awkward_moves: Number of inherently difficult moves
            - flow_breaks: Number of awkward transitions between moves
            - estimated_execution_time: Estimated time to execute (seconds)
            - fingertrick_difficulty: Average difficulty score per move
            - thumb_moves: Moves primarily using thumb
            - index_finger_moves: Moves primarily using index finger
            - middle_finger_moves: Moves primarily using middle finger
            - ring_finger_moves: Moves primarily using ring finger
            - comfort_score: Overall comfort rating (0-100)
            - ergonomic_rating: Qualitative comfort assessment
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
    fingertrick_difficulty = compute_fingertrick_difficulty(algorithm)

    # Count awkward moves (those with high difficulty scores)
    awkward_moves = sum(
        1 for move in algorithm
        if not move.is_pause
        and MOVE_DIFFICULTY.get(get_move_key(move), 1.0) > AWKWARD_THRESHOLD
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
    )
