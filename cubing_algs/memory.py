"""
Memorability analysis for Rubik's cube algorithms.

This module computes a memorability score (0.0-1.0) by combining
cognitive factors: length, chunking (Miller's law), structural patterns,
repetition, face familiarity, flow, and move familiarity.

Higher scores indicate algorithms that are easier to memorize,
following the same convention as the ergonomics module.
"""
import math
from collections import Counter
from typing import TYPE_CHECKING
from typing import NamedTuple

if TYPE_CHECKING:
    from cubing_algs.algorithm import Algorithm  # pragma: no cover
    from cubing_algs.move import Move  # pragma: no cover


# Sub-score weights (must sum to 1.0)
WEIGHT_LENGTH = 0.25
WEIGHT_CHUNK = 0.25
WEIGHT_STRUCTURE = 0.15
WEIGHT_REPETITION = 0.10
WEIGHT_FACE_FAMILIARITY = 0.10
WEIGHT_FLOW = 0.10
WEIGHT_MOVE_FAMILIARITY = 0.05

# Length score: sigmoid parameters
LENGTH_SIGMOID_CENTER = 12
LENGTH_SIGMOID_STEEPNESS = 0.35

# Chunk score: Miller's law parameters
MILLER_EASY_CHUNKS = 5
MILLER_HARD_CHUNKS = 9
CHUNK_VARIETY_PENALTY = 0.05  # Score loss per distinct trigger beyond 1

# Structure score parameters
STRUCTURE_COVERAGE_WEIGHT = 0.6
STRUCTURE_COMPRESSION_WEIGHT = 0.4

# Repetition parameters
REPETITION_MIN_LEN = 2
REPETITION_MAX_LEN = 6
REPETITION_MAX_SCORE = 0.7  # Max score reachable from repeats alone

# Face familiarity weights (higher = more familiar)
FACE_FAMILIARITY: dict[str, float] = {
    'R': 1.0, 'U': 1.0,
    'F': 0.8,
    'L': 0.75,
    'D': 0.5,
    'B': 0.3,
}

# Move familiarity: unfamiliar move faces/types
UNFAMILIAR_FACES = frozenset({'B', 'D'})
UNFAMILIAR_THRESHOLD = 0.67  # >=67% unfamiliar → score 0

# Rating thresholds (higher score = easier to memorize)
RATING_THRESHOLDS: list[tuple[float, str]] = [
    (0.8, 'Trivial'),
    (0.6, 'Easy'),
    (0.4, 'Moderate'),
    (0.2, 'Hard'),
    (0.0, 'Very Hard'),
]


class MemoryData(NamedTuple):
    """
    Container for memorability computation results.

    All scores are on a 0.0-1.0 scale where higher means easier
    to memorize, matching the ergonomics module convention.

    Attributes:
        memory_score: Composite memorability score (0.0-1.0, higher = easier).
        memory_rating: Human-readable rating, from 'Very Hard' to 'Trivial'.
        length_score: Shortness sub-score (0.0-1.0, higher = shorter).
        chunk_score: Chunkability sub-score per Miller's law
            (0.0-1.0, higher = fewer chunks to remember).
        structure_score: Structural pattern sub-score
            (0.0-1.0, higher = more compressible structure).
        repetition_score: Repeated pattern sub-score
            (0.0-1.0, higher = more repetition helping recall).
        face_familiarity_score: Face usage sub-score
            (0.0-1.0, higher = fewer and more familiar faces).
        flow_score: Flow sub-score (0.0-1.0, higher = fewer regrips).
        move_familiarity_score: Move type sub-score
            (0.0-1.0, higher = more familiar move types).
        move_count: Number of non-pause moves.
        effective_chunks: Number of effective memory chunks.
        distinct_triggers: Number of distinct trigger types.
        trigger_coverage_percent: Fraction of moves covered by triggers (0-1).
        distinct_faces: Number of distinct outer faces used.
        has_structure: Whether any structure was detected.
        repeated_patterns: Number of repeated subsequence occurrences.
        unfamiliar_move_percent: Fraction of unfamiliar moves (0-1).

    """

    # Composite
    memory_score: float
    memory_rating: str

    # Sub-scores (each 0.0-1.0, higher = easier)
    length_score: float
    chunk_score: float
    structure_score: float
    repetition_score: float
    face_familiarity_score: float
    flow_score: float
    move_familiarity_score: float

    # Raw data
    move_count: int
    effective_chunks: int
    distinct_triggers: int
    trigger_coverage_percent: float
    distinct_faces: int
    has_structure: bool
    repeated_patterns: int
    unfamiliar_move_percent: float


def compute_length_score(stm: int) -> float:
    """
    Compute length sub-score using sigmoid curve.

    Centered at STM=12, steepness 0.35.
    STM 4 → ~0.9, STM 12 → ~0.5, STM 20 → ~0.1.

    Args:
        stm: Slice Turn Metric count.

    Returns:
        Score from 0.0 to 1.0, higher = shorter = easier.

    """
    return 1.0 / (1.0 + math.exp(
        LENGTH_SIGMOID_STEEPNESS * (stm - LENGTH_SIGMOID_CENTER),
    ))


def compute_chunk_score(
    effective_chunks: int,
    distinct_triggers: int,
) -> float:
    """
    Compute chunk sub-score using Miller's law.

    5 chunks = easy, 9+ chunks = hard.
    Variety penalty: many distinct trigger types is harder.

    Args:
        effective_chunks: Number of effective memory chunks.
        distinct_triggers: Number of distinct trigger types.

    Returns:
        Score from 0.0 to 1.0, higher = fewer chunks = easier.

    """
    # Map chunks to 1.0-0.0 via linear interpolation in Miller range
    if effective_chunks <= MILLER_EASY_CHUNKS:
        base = 1.0 - (effective_chunks / MILLER_EASY_CHUNKS) * 0.4
    elif effective_chunks <= MILLER_HARD_CHUNKS:
        ratio = (
            (effective_chunks - MILLER_EASY_CHUNKS)
            / (MILLER_HARD_CHUNKS - MILLER_EASY_CHUNKS)
        )
        base = 0.6 - ratio * 0.4
    else:
        base = max(0.0, 0.2 - (effective_chunks - MILLER_HARD_CHUNKS) * 0.05)

    # Variety penalty: more distinct triggers = harder
    variety_penalty = max(0, distinct_triggers - 1) * CHUNK_VARIETY_PENALTY
    return min(1.0, max(0.0, base - variety_penalty))


def compute_structure_score(
    coverage_ratio: float,
    compression_ratio: float,
    *,
    has_structure: bool,
) -> float:
    """
    Compute structure sub-score.

    Full coverage + compression → score ~1.0 (easy to memorize).
    No structure → score 0.0 (hard).

    Args:
        coverage_ratio: Fraction of moves covered by structures (0-1).
        compression_ratio: Compression ratio from structure analysis.
        has_structure: Whether any structure was detected.

    Returns:
        Score from 0.0 to 1.0, higher = more structure = easier.

    """
    if not has_structure:
        return 0.0

    coverage_benefit = coverage_ratio * STRUCTURE_COVERAGE_WEIGHT
    compression_benefit = (
        max(0.0, compression_ratio) * STRUCTURE_COMPRESSION_WEIGHT
    )
    return min(1.0, coverage_benefit + compression_benefit)


def find_repeated_subsequences(
    moves: list[str],
    min_len: int = REPETITION_MIN_LEN,
    max_len: int = REPETITION_MAX_LEN,
) -> int:
    """
    Count repeated n-gram subsequences in a move list.

    Uses sliding window to find repeated patterns of length min_len to max_len.

    Args:
        moves: List of move strings.
        min_len: Minimum subsequence length.
        max_len: Maximum subsequence length.

    Returns:
        Number of repeated subsequence occurrences (total - unique).

    """
    if len(moves) < min_len * 2:
        return 0

    total_repeats = 0
    for n in range(min_len, min(max_len + 1, len(moves) // 2 + 1)):
        ngrams: Counter[tuple[str, ...]] = Counter()
        for i in range(len(moves) - n + 1):
            gram = tuple(moves[i:i + n])
            ngrams[gram] += 1
        # Count excess occurrences (repeats beyond first)
        total_repeats += sum(
            count - 1 for count in ngrams.values() if count > 1
        )

    return total_repeats


def compute_repetition_score(repeated_patterns: int, stm: int) -> float:
    """
    Compute repetition sub-score.

    More repeats → higher score (easier to memorize).

    Args:
        repeated_patterns: Number of repeated subsequences found.
        stm: Slice Turn Metric count for normalization.

    Returns:
        Score from 0.0 to REPETITION_MAX_SCORE, higher = easier.

    """
    if stm == 0:
        return 1.0

    # Normalize repeats by algorithm length
    repeat_ratio = repeated_patterns / stm
    return min(REPETITION_MAX_SCORE, repeat_ratio)


def get_move_face(move: 'Move') -> str | None:
    """
    Extract the face letter from a move.

    Returns None for rotations, pauses, and slice moves.

    Args:
        move: Move object to analyze.

    Returns:
        Face letter (R, U, F, L, D, B) or None.

    """
    if move.is_pause or move.is_rotation_move or move.is_inner_move:
        return None
    return move.base_move


def compute_face_familiarity_score(moves: 'list[Move]') -> float:
    """
    Compute face familiarity sub-score.

    Fewer/familiar faces = easier. RU-only → ~0.8; all 6 faces → 0.0.
    Weighted by face familiarity.

    Args:
        moves: List of Move objects.

    Returns:
        Score from 0.0 to 1.0, higher = fewer/more familiar faces = easier.

    """
    faces_used: set[str] = set()
    for move in moves:
        face = get_move_face(move)
        if face is not None:
            faces_used.add(face)

    if not faces_used:
        return 1.0

    # Diversity cost: number of distinct faces used
    face_count_cost = (len(faces_used) / 6.0) * 0.6

    # Unfamiliarity cost: sum of (1 - familiarity) for each face used,
    # normalized by the maximum theoretical unfamiliarity (≈ 1.65)
    unfamiliarity_sum = sum(
        1.0 - FACE_FAMILIARITY[face]
        for face in faces_used
    )
    max_unfamiliarity = sum(1.0 - w for w in FACE_FAMILIARITY.values())
    unfamiliarity_cost = (unfamiliarity_sum / max_unfamiliarity) * 0.4

    return max(0.0, 1.0 - face_count_cost - unfamiliarity_cost)


def compute_flow_memory_score(
    interruptions: int,
    stm: int,
) -> float:
    """
    Compute flow sub-score for memorability.

    More flow interruptions → harder to build muscle memory →
    harder to recall → lower score.

    Args:
        interruptions: Number of regrips in the algorithm.
        stm: Slice Turn Metric count for normalization.

    Returns:
        Score from 0.0 to 1.0, higher = smoother flow = easier.

    """
    if stm == 0:
        return 1.0

    ratio = interruptions / stm
    return max(0.0, 1.0 - ratio * 2.0)


def is_unfamiliar_move(move: 'Move') -> bool:
    """
    Check whether a move is unfamiliar to a typical solver.

    Unfamiliar moves are rotations, slices, wide moves,
    and B/D face moves.

    Args:
        move: Move object to analyze.

    Returns:
        True if the move is unfamiliar.

    """
    return (
        move.is_rotation_move
        or move.is_inner_move
        or move.is_wide_move
        or move.base_move in UNFAMILIAR_FACES
    )


def compute_unfamiliar_percent(moves: 'list[Move]') -> float:
    """
    Compute the fraction of unfamiliar moves in a move list.

    Args:
        moves: List of Move objects (non-pause).

    Returns:
        Fraction from 0.0 to 1.0.

    """
    if not moves:
        return 0.0

    unfamiliar_count = sum(1 for move in moves if is_unfamiliar_move(move))
    return unfamiliar_count / len(moves)


def compute_move_familiarity_score(moves: 'list[Move]') -> float:
    """
    Compute move familiarity sub-score.

    Based on the percentage of moves that are B/D/slice/wide/rotation.
    >=67% unfamiliar → score 0.

    Args:
        moves: List of Move objects (non-pause).

    Returns:
        Score from 0.0 to 1.0, higher = more familiar moves = easier.

    """
    if not moves:
        return 1.0

    unfamiliar_pct = compute_unfamiliar_percent(moves)
    return max(0.0, 1.0 - unfamiliar_pct / UNFAMILIAR_THRESHOLD)


def get_memory_rating(score: float) -> str:
    """
    Convert memorability score to a human-readable rating.

    Args:
        score: Memorability score (0.0-1.0, higher = easier).

    Returns:
        Rating string: Trivial, Easy, Moderate, Hard, or Very Hard.

    """
    for threshold, rating in RATING_THRESHOLDS:
        if score >= threshold:
            return rating
    return 'Very Hard'


def compute_memory(algorithm: 'Algorithm') -> MemoryData:  # noqa: PLR0914
    """
    Compute comprehensive memorability metrics for an algorithm.

    Combines multiple cognitive factors into a single memorability score:
    length, chunking, structure, repetition, face familiarity, flow,
    and move familiarity. All scores are 0.0-1.0, higher = easier
    to memorize.

    Args:
        algorithm: The algorithm to analyze.

    Returns:
        MemoryData containing all calculated memorability metrics.

    """
    # Filter out pauses
    non_pause_moves = [m for m in algorithm if not m.is_pause]
    move_count = len(non_pause_moves)

    if move_count == 0:
        return MemoryData(
            memory_score=1.0,
            memory_rating='Trivial',
            length_score=1.0,
            chunk_score=1.0,
            structure_score=1.0,
            repetition_score=1.0,
            face_familiarity_score=1.0,
            flow_score=1.0,
            move_familiarity_score=1.0,
            move_count=0,
            effective_chunks=0,
            distinct_triggers=0,
            trigger_coverage_percent=0.0,
            distinct_faces=0,
            has_structure=False,
            repeated_patterns=0,
            unfamiliar_move_percent=0.0,
        )

    # --- Reuse existing analysis ---
    stm = algorithm.metrics.stm
    ergo = algorithm.ergonomics
    struct = algorithm.structure

    # --- Length score ---
    length_score = compute_length_score(stm)

    # --- Chunk score ---
    trigger_count = ergo.trigger_count
    trigger_coverage = ergo.trigger_coverage
    distinct_triggers = len(set(ergo.detected_patterns))
    effective_chunks = max(0, trigger_count + (stm - trigger_coverage))
    chunk_score = compute_chunk_score(effective_chunks, distinct_triggers)

    # --- Structure score ---
    has_structure = struct.total_structures > 0
    structure_score = compute_structure_score(
        struct.coverage_ratio,
        struct.compression_ratio,
        has_structure=has_structure,
    )

    # --- Repetition score ---
    move_strings = [str(m) for m in non_pause_moves]
    repeated_patterns = find_repeated_subsequences(move_strings)
    repetition_score = compute_repetition_score(repeated_patterns, stm)

    # --- Face familiarity score ---
    face_familiarity_score = compute_face_familiarity_score(non_pause_moves)
    faces_used = {
        get_move_face(m) for m in non_pause_moves
    } - {None}
    distinct_faces = len(faces_used)

    # --- Flow score ---
    flow_mem_score = compute_flow_memory_score(
        ergo.regrip_count, stm,
    )

    # --- Move familiarity score ---
    familiarity_score = compute_move_familiarity_score(non_pause_moves)
    unfamiliar_pct = compute_unfamiliar_percent(non_pause_moves)

    # --- Composite score ---
    memory_score = (
        length_score * WEIGHT_LENGTH
        + chunk_score * WEIGHT_CHUNK
        + structure_score * WEIGHT_STRUCTURE
        + repetition_score * WEIGHT_REPETITION
        + face_familiarity_score * WEIGHT_FACE_FAMILIARITY
        + flow_mem_score * WEIGHT_FLOW
        + familiarity_score * WEIGHT_MOVE_FAMILIARITY
    )
    memory_score = max(0.0, min(1.0, memory_score))

    trigger_coverage_pct = trigger_coverage / stm if stm > 0 else 0.0

    return MemoryData(
        memory_score=memory_score,
        memory_rating=get_memory_rating(memory_score),
        length_score=length_score,
        chunk_score=chunk_score,
        structure_score=structure_score,
        repetition_score=repetition_score,
        face_familiarity_score=face_familiarity_score,
        flow_score=flow_mem_score,
        move_familiarity_score=familiarity_score,
        move_count=move_count,
        effective_chunks=effective_chunks,
        distinct_triggers=distinct_triggers,
        trigger_coverage_percent=trigger_coverage_pct,
        distinct_faces=distinct_faces,
        has_structure=has_structure,
        repeated_patterns=repeated_patterns,
        unfamiliar_move_percent=unfamiliar_pct,
    )
