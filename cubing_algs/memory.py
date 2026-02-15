"""
Memory difficulty analysis for Rubik's cube algorithms.

This module computes a memory difficulty score (0-100) by combining
cognitive factors: length, chunking (Miller's law), structural patterns,
repetition, face diversity, flow, and move familiarity.

Higher scores indicate algorithms that are harder to memorize.
"""
from __future__ import annotations

import math
from collections import Counter
from dataclasses import dataclass
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from cubing_algs.algorithm import Algorithm  # pragma: no cover
    from cubing_algs.move import Move  # pragma: no cover


# Sub-score weights (must sum to 1.0)
WEIGHT_LENGTH = 0.25
WEIGHT_CHUNK = 0.25
WEIGHT_STRUCTURE = 0.15
WEIGHT_REPETITION = 0.10
WEIGHT_FACE_DIVERSITY = 0.10
WEIGHT_FLOW = 0.10
WEIGHT_MOVE_FAMILIARITY = 0.05

# Length score: sigmoid parameters
LENGTH_SIGMOID_CENTER = 12
LENGTH_SIGMOID_STEEPNESS = 0.35

# Chunk score: Miller's law parameters
MILLER_EASY_CHUNKS = 5
MILLER_HARD_CHUNKS = 9
CHUNK_VARIETY_PENALTY = 5.0  # Extra difficulty per distinct trigger beyond 1

# Structure score parameters
STRUCTURE_COVERAGE_WEIGHT = 0.6
STRUCTURE_COMPRESSION_WEIGHT = 0.4

# Repetition parameters
REPETITION_MIN_LEN = 2
REPETITION_MAX_LEN = 6
REPETITION_MAX_SCORE_REDUCTION = 70.0  # Max reduction from repeats

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
UNFAMILIAR_THRESHOLD = 0.67  # >67% unfamiliar → score 100

# Rating thresholds
RATING_THRESHOLDS: list[tuple[float, str]] = [
    (80.0, 'Very Hard'),
    (60.0, 'Hard'),
    (40.0, 'Moderate'),
    (20.0, 'Easy'),
    (0.0, 'Trivial'),
]


@dataclass(frozen=True)
class MemoryData:
    """Container for memory difficulty computation results."""

    # Composite
    memory_score: float
    memory_rating: str

    # Sub-scores (each 0-100)
    length_score: float
    chunk_score: float
    structure_score: float
    repetition_score: float
    face_diversity_score: float
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

    Centered at HTM=12, steepness 0.35.
    HTM 4 → ~10, HTM 12 → ~50, HTM 20 → ~90.

    Args:
        stm: Slice Turn Metric count.

    Returns:
        Score from 0 to 100.

    """
    return 100.0 / (1.0 + math.exp(
        -LENGTH_SIGMOID_STEEPNESS * (stm - LENGTH_SIGMOID_CENTER),
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
        Score from 0 to 100.

    """
    # Map chunks to 0-100 via linear interpolation in Miller range
    if effective_chunks <= MILLER_EASY_CHUNKS:
        base = (effective_chunks / MILLER_EASY_CHUNKS) * 40.0
    elif effective_chunks <= MILLER_HARD_CHUNKS:
        ratio = (
            (effective_chunks - MILLER_EASY_CHUNKS)
            / (MILLER_HARD_CHUNKS - MILLER_EASY_CHUNKS)
        )
        base = 40.0 + ratio * 40.0
    else:
        base = min(100.0, 80.0 + (effective_chunks - MILLER_HARD_CHUNKS) * 5.0)

    # Variety penalty: more distinct triggers = harder
    variety_penalty = max(0, distinct_triggers - 1) * CHUNK_VARIETY_PENALTY
    return min(100.0, base + variety_penalty)


def compute_structure_score(
    coverage_percent: float,
    compression_ratio: float,
    *,
    has_structure: bool,
) -> float:
    """
    Compute structure sub-score.

    Full coverage + compression → score ~0 (easy to memorize).
    No structure → score 100 (hard).

    Args:
        coverage_percent: Fraction of moves covered by structures (0-1).
        compression_ratio: Compression ratio from structure analysis.
        has_structure: Whether any structure was detected.

    Returns:
        Score from 0 to 100.

    """
    if not has_structure:
        return 100.0

    # Higher coverage and compression → lower score (easier)
    coverage_benefit = coverage_percent * STRUCTURE_COVERAGE_WEIGHT
    compression_benefit = (
        max(0.0, compression_ratio) * STRUCTURE_COMPRESSION_WEIGHT
    )
    total_benefit = coverage_benefit + compression_benefit
    return max(0.0, 100.0 * (1.0 - total_benefit))


def _find_repeated_subsequences(
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

    More repeats → lower score (easier to memorize).

    Args:
        repeated_patterns: Number of repeated subsequences found.
        stm: Slice Turn Metric count for normalization.

    Returns:
        Score from 0 to 100.

    """
    if stm == 0:
        return 0.0

    # Normalize repeats by algorithm length
    repeat_ratio = repeated_patterns / max(1, stm)
    reduction = min(REPETITION_MAX_SCORE_REDUCTION, repeat_ratio * 100.0)
    return max(0.0, 100.0 - reduction)


def _get_move_face(move: Move) -> str | None:
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


def compute_face_diversity_score(moves: list[Move]) -> float:
    """
    Compute face diversity sub-score.

    Fewer/familiar faces = easier. RU-only → ~10; all 6 faces → ~80+.
    Weighted by face familiarity.

    Args:
        moves: List of Move objects.

    Returns:
        Score from 0 to 100.

    """
    faces_used: set[str] = set()
    for move in moves:
        face = _get_move_face(move)
        if face is not None:
            faces_used.add(face)

    if not faces_used:
        return 0.0

    # Compute weighted diversity: sum of (1 - familiarity) for each face used
    unfamiliarity_sum = sum(
        1.0 - FACE_FAMILIARITY.get(face, 0.5)
        for face in faces_used
    )

    # Scale: max theoretical unfamiliarity = sum of all (1-weight) ≈ 2.65
    max_unfamiliarity = sum(1.0 - w for w in FACE_FAMILIARITY.values())
    if max_unfamiliarity:
        normalized = unfamiliarity_sum / max_unfamiliarity
    else:
        normalized = 0.0

    # Base score from number of distinct faces
    face_count_score = (len(faces_used) / 6.0) * 60.0
    unfamiliarity_score = normalized * 40.0

    return min(100.0, face_count_score + unfamiliarity_score)


def compute_flow_memory_score(
    regrip_count: int,
    flow_breaks: int,
    stm: int,
) -> float:
    """
    Compute flow sub-score for memory difficulty.

    More flow interruptions → harder to build muscle memory → harder to recall.

    Args:
        regrip_count: Number of regrips in the algorithm.
        flow_breaks: Number of flow breaks.
        stm: Slice Turn Metric count for normalization.

    Returns:
        Score from 0 to 100.

    """
    if stm == 0:
        return 0.0

    interruptions = regrip_count + flow_breaks
    ratio = interruptions / max(1, stm)
    return min(100.0, ratio * 200.0)


def compute_move_familiarity_score(moves: list[Move]) -> float:
    """
    Compute move familiarity sub-score.

    Percentage of moves that are B/D/slice/wide/rotation.
    >67% unfamiliar → score 100.

    Args:
        moves: List of Move objects (non-pause).

    Returns:
        Score from 0 to 100.

    """
    if not moves:
        return 0.0

    unfamiliar_count = 0
    for move in moves:
        is_unfamiliar = (
            move.is_rotation_move
            or move.is_inner_move
            or move.is_wide_move
            or move.base_move in UNFAMILIAR_FACES
        )
        if is_unfamiliar:
            unfamiliar_count += 1

    unfamiliar_pct = unfamiliar_count / len(moves)
    if unfamiliar_pct >= UNFAMILIAR_THRESHOLD:
        return 100.0

    return min(100.0, (unfamiliar_pct / UNFAMILIAR_THRESHOLD) * 100.0)


def get_memory_rating(score: float) -> str:
    """
    Convert memory score to a human-readable rating.

    Args:
        score: Memory difficulty score (0-100).

    Returns:
        Rating string: Trivial, Easy, Moderate, Hard, or Very Hard.

    """
    for threshold, rating in RATING_THRESHOLDS:
        if score >= threshold:
            return rating
    return 'Trivial'


def compute_memory(algorithm: Algorithm) -> MemoryData:  # noqa: PLR0914
    """
    Compute comprehensive memory difficulty metrics for an algorithm.

    Combines multiple cognitive factors into a single difficulty score:
    length, chunking, structure, repetition, face diversity, flow,
    and move familiarity.

    Args:
        algorithm: The algorithm to analyze.

    Returns:
        MemoryData containing all calculated memory metrics.

    """
    # Filter out pauses
    non_pause_moves = [m for m in algorithm if not m.is_pause]
    move_count = len(non_pause_moves)

    if move_count == 0:
        return MemoryData(
            memory_score=0.0,
            memory_rating='Trivial',
            length_score=0.0,
            chunk_score=0.0,
            structure_score=0.0,
            repetition_score=0.0,
            face_diversity_score=0.0,
            flow_score=0.0,
            move_familiarity_score=0.0,
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
    effective_chunks = trigger_count + (stm - trigger_coverage)
    chunk_score = compute_chunk_score(effective_chunks, distinct_triggers)

    # --- Structure score ---
    has_structure = struct.total_structures > 0
    structure_score = compute_structure_score(
        struct.coverage_percent,
        struct.compression_ratio,
        has_structure=has_structure,
    )

    # --- Repetition score ---
    move_strings = [str(m) for m in non_pause_moves]
    repeated_patterns = _find_repeated_subsequences(move_strings)
    repetition_score = compute_repetition_score(repeated_patterns, stm)

    # --- Face diversity score ---
    face_div_score = compute_face_diversity_score(non_pause_moves)
    faces_used = {
        _get_move_face(m) for m in non_pause_moves
    } - {None}
    distinct_faces = len(faces_used)

    # --- Flow score ---
    flow_mem_score = compute_flow_memory_score(
        ergo.regrip_count, ergo.flow_breaks, stm,
    )

    # --- Move familiarity score ---
    familiarity_score = compute_move_familiarity_score(non_pause_moves)
    unfamiliar_count = sum(
        1 for m in non_pause_moves
        if (m.is_rotation_move or m.is_inner_move or m.is_wide_move
            or m.base_move in UNFAMILIAR_FACES)
    )
    unfamiliar_pct = unfamiliar_count / move_count

    # --- Composite score ---
    memory_score = (
        length_score * WEIGHT_LENGTH
        + chunk_score * WEIGHT_CHUNK
        + structure_score * WEIGHT_STRUCTURE
        + repetition_score * WEIGHT_REPETITION
        + face_div_score * WEIGHT_FACE_DIVERSITY
        + flow_mem_score * WEIGHT_FLOW
        + familiarity_score * WEIGHT_MOVE_FAMILIARITY
    )
    memory_score = max(0.0, min(100.0, memory_score))

    trigger_coverage_pct = trigger_coverage / stm if stm > 0 else 0.0

    return MemoryData(
        memory_score=memory_score,
        memory_rating=get_memory_rating(memory_score),
        length_score=length_score,
        chunk_score=chunk_score,
        structure_score=structure_score,
        repetition_score=repetition_score,
        face_diversity_score=face_div_score,
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
