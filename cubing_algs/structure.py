"""
Detect and classify conjugates and commutators in algorithms.

This module provides functionality to analyze an Algorithm and detect
meaningful conjugate [A: B] and commutator [A, B] patterns, producing
a compressed notation that illustrates the algorithm's structure.

Conjugate: [A: B] = A B A' (setup A, apply B, undo setup)
Commutator: [A, B] = A B A' B' (creates 3-cycles and piece transformations)

Classification System:
- Pure Commutators: 8-move optimal 3-cycles (2+2+2+2 structure)
- A9 Commutators: 9-move commutators with one move cancellation
- Orthogonal Commutators: 10-move commutators without cancellations
- Simple Conjugates: Short setup (1-2 moves) for piece manipulation
- Nested Conjugates: Conjugates containing other structures

The module follows speedcubing conventions and the Beyer-Hardwick (BH)
classification system for systematic algorithm analysis.
"""
from bisect import bisect_left
from typing import TYPE_CHECKING
from typing import Literal
from typing import NamedTuple

if TYPE_CHECKING:
    from cubing_algs.algorithm import Algorithm  # pragma: no cover

# Scoring constants
ACTION_WEIGHT_DIVISOR = 10.0  # Divisor for action length weighting
SCORE_MULTIPLIER = 100  # Multiplier to scale scores to readable range

# Thresholds for auto-calculated parameters
MIN_SETUP_LENGTH = 2  # Minimum setup length (allows pure commutators)
SETUP_LENGTH_DIVISOR = 3  # Divisor for calculating max setup from algo length
SHORT_ALGO_THRESHOLD = 6  # Threshold for "very short" algorithms
MEDIUM_ALGO_THRESHOLD = 12  # Threshold for "medium" algorithms
SHORT_ALGO_MIN_SCORE = 0.1  # Min score for short algorithms (very permissive)
MEDIUM_ALGO_MIN_SCORE = 3.0  # Min score for medium algorithms
LONG_ALGO_MIN_SCORE = 5.0  # Min score for long algorithms

# Classification constants
PURE_COMMUTATOR_SETUP_LEN = 2  # Setup length for pure commutators
PURE_COMMUTATOR_ACTION_LEN = 2  # Action length for pure commutators
COMMUTATOR_A9_TOTAL_MOVES = 10  # Total moves in A9 commutator (before cancel)
MULTI_SETUP_MIN_LENGTH = 3  # Min setup length for "multi-setup" conjugates

# Scoring bonus for pure commutators (2+2+2+2 = 8 moves).
# A pure [2,2] commutator has base score 10.0; a [2,4] scores 20.0.
# The 2.5x bonus lifts pure to 25.0, preferring it over [2,4] competitors.
PURE_COMMUTATOR_SCORE_BONUS = 2.5

# Efficiency rating constants
EFFICIENCY_EXCELLENT_RATIO = 0.75  # Ratio of pure/A9 for "Excellent"
EFFICIENCY_GOOD_RATIO = 0.5  # Ratio of pure/A9 for "Good"
EFFICIENCY_EXCELLENT_AVG_MOVES = 9  # Avg moves for "Excellent"
EFFICIENCY_GOOD_AVG_MOVES = 10  # Avg moves for "Good"
EFFICIENCY_FAIR_AVG_MOVES = 12  # Avg moves for "Fair"

# Nested detection limits
DEFAULT_MAX_NESTING_DEPTH = 10  # Maximum recursion depth for nested structures
# Very permissive score for classification checks
CLASSIFICATION_MIN_SCORE = 0.1


type StructureType = Literal['conjugate', 'commutator']
type StructureClassification = Literal[
    'pure', 'A9',
    'orthogonal', 'extended',
    'other', 'simple',
    'nested', 'multi-setup',
    '',
]


class Structure(NamedTuple):
    """Represents a detected structure (conjugate or commutator)."""

    type: StructureType
    setup: 'Algorithm'  # The A part
    action: 'Algorithm'  # The B part
    start: int  # Start index in original algorithm
    end: int  # End index in original algorithm
    score: float  # Quality score (higher is better)
    classification: StructureClassification
    has_cancellations: bool = False  # Whether moves cancel
    move_count: int = 0  # Total move count
    is_pure: bool = False  # Pure commutator (8 moves)

    def __str__(self) -> str:
        """
        Return the compressed notation for this structure.

        Returns:
            Compressed notation string ([A: B] or [A, B]).

        """
        if self.type == 'conjugate':
            return f'[{self.setup}: {self.action}]'
        return f'[{self.setup}, {self.action}]'


class StructureData(NamedTuple):
    """Container for comprehensive structure analysis results."""

    # Original algorithm representation
    original: str
    compressed: str

    # Structure counts
    total_structures: int
    conjugate_count: int
    commutator_count: int

    # Nesting analysis
    max_nesting_depth: int
    nested_structure_count: int

    # Compression metrics
    original_length: int
    compressed_notation_char_length: int
    compression_ratio: float

    # Structure quality
    average_structure_score: float
    best_structure_score: float

    # Detailed structures
    structures: list[Structure]

    # Setup and action analysis
    shortest_setup_length: int
    longest_setup_length: int
    average_setup_length: float
    shortest_action_length: int
    longest_action_length: int
    average_action_length: float

    # Coverage metrics
    coverage_ratio: float  # Ratio of moves covered by structures (0.0-1.0)
    uncovered_moves: int

    # Classification statistics
    pure_commutator_count: int  # Pure 8-move commutators
    a9_commutator_count: int  # 9-move commutators with cancellation
    nested_conjugate_count: int  # Conjugates with nested structures
    simple_conjugate_count: int  # Simple conjugates (1-2 move setup)
    structures_with_cancellations: int  # Structures with move cancellations
    average_move_count: float  # Average moves per structure
    efficiency_rating: str  # Overall efficiency assessment


# Keyed by str(algo); plain dict is safe because algorithm sizes are small
# (speedcubing algorithms rarely exceed 30 moves, bounding search space).
type StructureCache = dict[str, list[Structure]]


class StructureStats(NamedTuple):
    """Aggregated metrics computed in a single pass over detected structures."""

    average_structure_score: float
    best_structure_score: float
    shortest_setup_length: int
    longest_setup_length: int
    average_setup_length: float
    shortest_action_length: int
    longest_action_length: int
    average_action_length: float
    covered_moves: int
    pure_commutator_count: int
    a9_commutator_count: int
    nested_conjugate_count: int
    simple_conjugate_count: int
    structures_with_cancellations: int
    average_move_count: float
    efficiency_rating: str


def calculate_max_setup_length(algo_length: int) -> int:
    """
    Calculate the maximum setup length based on algorithm length.

    The setup should not dominate the structure, so we limit it to roughly
    1/3 of the algorithm length, with a minimum of 2 to allow pure commutators.

    Args:
        algo_length: Length of the algorithm in moves

    Returns:
        Maximum reasonable setup length

    """
    return max(MIN_SETUP_LENGTH, algo_length // SETUP_LENGTH_DIVISOR)


def calculate_min_score(algo_length: int) -> float:
    """
    Calculate the minimum quality score based on algorithm length.

    Shorter algorithms accept any meaningful structure, while longer algorithms
    require higher quality structures to avoid false positives.

    Args:
        algo_length: Length of the algorithm in moves

    Returns:
        Minimum score threshold

    """
    if algo_length < SHORT_ALGO_THRESHOLD:
        return SHORT_ALGO_MIN_SCORE
    if algo_length <= MEDIUM_ALGO_THRESHOLD:
        return MEDIUM_ALGO_MIN_SCORE
    return LONG_ALGO_MIN_SCORE


def inverse_sequence(algo: 'Algorithm') -> 'Algorithm':
    """
    Return the inverse of an algorithm (reversed with inverted moves).

    Args:
        algo: The algorithm to invert.

    Returns:
        The inverted algorithm.

    """
    from cubing_algs.transform.invert import invert_moves  # noqa: PLC0415

    return algo.transform(invert_moves)


def detect_move_cancellations(
    first: 'Algorithm',
    second: 'Algorithm',
) -> bool:
    """
    Detect if moves can cancel between two sequences.

    Checks if the last move of first and first move of second
    are on the same face and can cancel.

    Args:
        first: The first algorithm sequence.
        second: The second algorithm sequence.

    Returns:
        True if moves can cancel, False otherwise.

    """
    if not first or not second:
        return False

    last_move = first[-1]
    first_move = second[0]

    # Check if they're on the same face (ignoring direction and amount)
    return last_move.raw_base_move == first_move.raw_base_move


class Candidate(NamedTuple):
    """
    A structure found by the search, before it is built and classified.

    The search works on positions and lengths only: the setup and action
    algorithms and the classification are built for the retained
    candidates alone.
    """

    type: StructureType
    start: int  # Start index in the searched algorithm
    end: int  # End index in the searched algorithm
    setup_len: int  # Length of the A part
    action_len: int  # Length of the B part
    score: float  # Quality score (higher is better)
    is_pure: bool  # Pure commutator (8 moves)


class MoveIndex(NamedTuple):
    """
    An algorithm prepared for the search of inverse sub-sequences.

    Moves are compared as strings, so the search builds no intermediate
    Algorithm. The positions of each move let the search jump straight to
    the places where an inverse sub-sequence can start.
    """

    moves: list[str]  # Move strings, in order
    inverses: list[str]  # Inverse of the move at the same position
    positions: dict[str, list[int]]  # Ascending positions of each move


def build_move_index(algo: 'Algorithm') -> MoveIndex:
    """
    Prepare an untimed algorithm for the structure search.

    Args:
        algo: The algorithm to index, without timing.

    Returns:
        The move strings, their inverses and the positions of each move.

    """
    moves = [move.data for move in algo]
    inverses = [move.inverted.data for move in algo]
    positions: dict[str, list[int]] = {}
    for position, move in enumerate(moves):
        positions.setdefault(move, []).append(position)

    return MoveIndex(moves, inverses, positions)


def inverse_at(index: MoveIndex, start: int, length: int) -> list[str]:
    """
    Return the inverse of a sub-sequence of the indexed algorithm.

    Args:
        index: The indexed algorithm.
        start: Start of the sub-sequence.
        length: Length of the sub-sequence.

    Returns:
        The move strings of the inverse sub-sequence.

    """
    return index.inverses[start:start + length][::-1]


def has_commutator_cancellations(
    setup: 'Algorithm',
    action: 'Algorithm',
) -> bool:
    """
    Detect if moves can cancel at a boundary of the commutator [A, B].

    The three boundaries of A B A' B' are checked: A|B, B|A' and A'|B'.

    Args:
        setup: The A part of the commutator.
        action: The B part of the commutator.

    Returns:
        True if moves can cancel at one of the boundaries.

    """
    setup_inv = inverse_sequence(setup)
    action_inv = inverse_sequence(action)

    return (
        detect_move_cancellations(setup, action) or
        detect_move_cancellations(action, setup_inv) or
        detect_move_cancellations(setup_inv, action_inv)
    )


def classify_commutator(
    setup: 'Algorithm',
    action: 'Algorithm',
) -> StructureClassification:
    """
    Classify a commutator based on speedcubing taxonomy.

    Classifications:
    - 'pure': 8-move pure commutator (2+2+2+2)
    - 'A9': 9-move with cancellation
    - 'orthogonal': 10-move with no cancellations
    - 'extended': Longer than 10 moves

    Args:
        setup: The A part of the commutator
        action: The B part of the commutator

    Returns:
        Classification string (pure, A9, orthogonal, extended, or other).

    """
    setup_len = len(setup)
    action_len = len(action)
    total_moves = setup_len * 2 + action_len * 2

    # Pure commutator: 2 + 2 + 2 + 2 = 8 moves
    if (setup_len == PURE_COMMUTATOR_SETUP_LEN and
            action_len == PURE_COMMUTATOR_ACTION_LEN):
        return 'pure'

    has_cancel = has_commutator_cancellations(setup, action)

    # A9: Would be 10 moves but has one cancellation
    if total_moves == COMMUTATOR_A9_TOTAL_MOVES and has_cancel:
        return 'A9'

    # Orthogonal: 10 moves, no cancellations
    if total_moves == COMMUTATOR_A9_TOTAL_MOVES and not has_cancel:
        return 'orthogonal'

    # Extended commutators
    if total_moves > COMMUTATOR_A9_TOTAL_MOVES:
        return 'extended'

    return 'other'


def contains_commutator(algo: 'Algorithm') -> bool:
    """
    Check if a commutator is detected in an algorithm.

    The detection uses the permissive thresholds of the classification:
    the setup length adapted to the algorithm length and the
    CLASSIFICATION_MIN_SCORE.

    Args:
        algo: The algorithm to search.

    Returns:
        True if at least one detected structure is a commutator.

    """
    if algo.has_times:
        algo = untime_algorithm(algo)

    candidates = select_candidates(
        build_move_index(algo),
        calculate_max_setup_length(len(algo)),
        CLASSIFICATION_MIN_SCORE,
    )

    return any(c.type == 'commutator' for c in candidates)


def classify_conjugate(
    setup: 'Algorithm',
    action: 'Algorithm',
    nesting_depth: int = 0,
) -> StructureClassification:
    """
    Classify a conjugate based on structure and efficiency.

    Classifications:
    - 'simple': Short setup (1-2 moves) with commutator action
    - 'nested': Action contains a structure
    - 'multi-setup': Long setup (3+ moves)

    Args:
        setup: The setup (A) part of the conjugate.
        action: The action (B) part of the conjugate.
        nesting_depth: The nesting depth; at DEFAULT_MAX_NESTING_DEPTH
            and beyond, the action is no longer searched.

    Returns:
        Classification string (simple, nested or multi-setup).

    """
    if (nesting_depth < DEFAULT_MAX_NESTING_DEPTH and
            contains_commutator(action)):
        return 'nested'

    if len(setup) >= MULTI_SETUP_MIN_LENGTH:
        return 'multi-setup'

    return 'simple'


def score_structure(
    setup_len: int,
    action_len: int,
    *,
    is_commutator: bool = False,
    is_pure: bool = False,
) -> float:
    """
    Score a potential structure based on compression ratio and meaningfulness.

    Higher scores indicate better structures. We prefer:
    - Shorter setups relative to actions
    - Non-trivial actions (longer is better)
    - Overall compression benefit
    - Pure commutators (8-move optimal 3-cycles) over longer alternatives

    Args:
        setup_len: Length of the setup (A) part of the structure.
        action_len: Length of the action (B) part of the structure.
        is_commutator: True for commutator [A, B] = A B A' B',
            False for conjugate [A: B] = A B A'.
        is_pure: True for pure 8-move commutators (setup=2, action=2).
            Applies a bonus multiplier so pure commutators outrank longer
            competitors detected at the same position.

    Returns:
        Quality score (higher is better, 0-100+ range).

    """
    if setup_len == 0 or action_len == 0:
        return 0.0

    # Compression ratio: how much we save by using bracket notation
    # Conjugate [A: B] = A B A' → original = 2|A| + |B|
    # Commutator [A, B] = A B A' B' → original = 2|A| + 2|B|
    if is_commutator:
        original_length = setup_len * 2 + action_len * 2
    else:
        original_length = setup_len * 2 + action_len
    compressed_length = setup_len + action_len
    compression_ratio = (original_length - compressed_length) / original_length

    # Favor longer actions (more meaningful)
    action_weight = min(action_len / ACTION_WEIGHT_DIVISOR, 1.0)

    # Penalize very long setups relative to action
    setup_penalty = 1.0
    if setup_len > action_len:
        setup_penalty = action_len / setup_len

    base = compression_ratio * action_weight * setup_penalty * SCORE_MULTIPLIER
    if is_pure and is_commutator:
        return base * PURE_COMMUTATOR_SCORE_BONUS
    return base


def find_conjugate(
    index: MoveIndex,
    start: int,
    max_setup_len: int,
) -> Candidate | None:
    """
    Find the best conjugate [A: B] = A B A' starting at the given position.

    For each setup length, only the positions holding the first move of
    A' are tried as the end of B. On equal scores the shortest setup,
    then the shortest action, wins.

    Args:
        index: The indexed algorithm to search
        start: Starting position
        max_setup_len: Maximum setup length

    Returns:
        Best conjugate candidate found, or None if no valid structure exists.

    """
    moves = index.moves
    algo_len = len(moves)
    best: Candidate | None = None

    for setup_len in range(1, max_setup_len + 1):
        if start + setup_len * 2 > algo_len:
            break

        setup_inv = inverse_at(index, start, setup_len)
        occurrences = index.positions.get(setup_inv[0], [])
        first = bisect_left(occurrences, start + setup_len + 1)

        # A' starts right after B, and must fit in the algorithm
        for action_end in occurrences[first:]:
            if action_end + setup_len > algo_len:
                break
            if moves[action_end:action_end + setup_len] != setup_inv:
                continue

            action_len = action_end - start - setup_len
            score = score_structure(setup_len, action_len)
            if best is None or score > best.score:
                best = Candidate(
                    type='conjugate',
                    start=start,
                    end=action_end + setup_len,
                    setup_len=setup_len,
                    action_len=action_len,
                    score=score,
                    is_pure=False,
                )

    return best


def find_commutator(
    index: MoveIndex,
    start: int,
    max_part_len: int,
) -> Candidate | None:
    """
    Find the best commutator [A, B] = A B A' B' at the given position.

    For each A length, only the positions holding the first move of A'
    are tried as the end of B. On equal scores the shortest A, then the
    shortest B, wins.

    Args:
        index: The indexed algorithm to search
        start: Starting position
        max_part_len: Maximum length for A and B parts

    Returns:
        Best commutator candidate found, or None if no valid structure exists.

    """
    moves = index.moves
    algo_len = len(moves)
    best: Candidate | None = None

    for a_len in range(1, max_part_len + 1):
        if start + a_len * 2 > algo_len:
            break

        a_inv = inverse_at(index, start, a_len)
        occurrences = index.positions.get(a_inv[0], [])
        first = bisect_left(occurrences, start + a_len + 1)

        # A B A' B' must fit in the algorithm: the longest B is bounded
        last_b_end = start + a_len + (algo_len - start - a_len * 2) // 2

        for b_end in occurrences[first:]:
            if b_end > last_b_end:
                break

            b_len = b_end - start - a_len
            if (
                moves[b_end:b_end + a_len] != a_inv or
                moves[b_end + a_len:b_end + a_len + b_len] != inverse_at(
                    index, start + a_len, b_len,
                )
            ):
                continue

            is_pure = (
                a_len == PURE_COMMUTATOR_SETUP_LEN
                and b_len == PURE_COMMUTATOR_ACTION_LEN
            )
            score = score_structure(
                a_len, b_len, is_commutator=True, is_pure=is_pure,
            )
            if best is None or score > best.score:
                best = Candidate(
                    type='commutator',
                    start=start,
                    end=b_end + a_len + b_len,
                    setup_len=a_len,
                    action_len=b_len,
                    score=score,
                    is_pure=is_pure,
                )

    return best


def select_candidates(
    index: MoveIndex,
    max_setup_len: int,
    min_score: float,
) -> list[Candidate]:
    """
    Select the structures of an algorithm, greedily from left to right.

    At each position the best commutator and the best conjugate compete,
    the commutator winning ties. A structure scoring at least min_score
    is kept and the search resumes after it.

    Args:
        index: The indexed algorithm to search
        max_setup_len: Maximum setup sequence length
        min_score: Minimum structure score

    Returns:
        Selected candidates, sorted by position.

    """
    candidates: list[Candidate] = []
    i = 0

    while i < len(index.moves):
        commutator = find_commutator(index, i, max_setup_len)
        conjugate = find_conjugate(index, i, max_setup_len)

        # Every commutator A B A' B' contains conjugate A B A',
        # so conjugate is always found when commutator is
        best = None
        if commutator and conjugate:
            best = (
                commutator if commutator.score >= conjugate.score
                else conjugate
            )
        elif conjugate:
            best = conjugate
        elif commutator:
            best = commutator

        if best and best.score >= min_score:
            candidates.append(best)
            i = best.end
        else:
            i += 1

    return candidates


def build_structure(
    algo: 'Algorithm',
    candidate: Candidate,
    nesting_depth: int = 0,
) -> Structure:
    """
    Build and classify the structure of a selected candidate.

    Args:
        algo: The algorithm the candidate was found in
        candidate: The selected candidate
        nesting_depth: The nesting depth

    Returns:
        The structure, with its setup and action algorithms.

    """
    action_start = candidate.start + candidate.setup_len
    setup = algo[candidate.start:action_start]
    action = algo[action_start:action_start + candidate.action_len]

    if candidate.type == 'conjugate':
        classification = classify_conjugate(setup, action, nesting_depth)
        has_cancel = detect_move_cancellations(setup, action)
    else:
        classification = classify_commutator(setup, action)
        has_cancel = has_commutator_cancellations(setup, action)

    return Structure(
        type=candidate.type,
        setup=setup,
        action=action,
        start=candidate.start,
        end=candidate.end,
        score=candidate.score,
        classification=classification,
        has_cancellations=has_cancel,
        move_count=candidate.end - candidate.start,
        is_pure=candidate.is_pure,
    )


def detect_structures(
    algo: 'Algorithm',
    max_setup_len: int | None = None,
    min_score: float | None = None,
    nesting_depth: int = 0,
) -> list[Structure]:
    """
    Detect all meaningful conjugate and commutator structures in an algorithm.

    The function automatically determines appropriate thresholds based on
    algorithm length if not explicitly provided.

    Args:
        algo: The algorithm to analyze
        max_setup_len: Maximum setup sequence length (auto-calculated)
        min_score: Minimum structure score (auto-calculated)
        nesting_depth: The nesting depth

    Returns:
        List of detected structures, sorted by position

    """
    # Move equality includes timestamps, which would keep the inverse
    # lookups from ever matching
    if algo.has_times:
        algo = untime_algorithm(algo)

    # Use heuristics if parameters not provided
    algo_len = len(algo)
    if max_setup_len is None:
        max_setup_len = calculate_max_setup_length(algo_len)
    if min_score is None:
        min_score = calculate_min_score(algo_len)

    candidates = select_candidates(
        build_move_index(algo), max_setup_len, min_score,
    )

    return [
        build_structure(algo, candidate, nesting_depth)
        for candidate in candidates
    ]


def compress_recursive(  # noqa: C901, PLR0912
    algo: 'Algorithm',
    structures: list[Structure],
    offset: int = 0,
    structure_cache: StructureCache | None = None,
) -> str:
    """
    Recursively compress an algorithm using detected structures.

    Args:
        algo: The algorithm to compress
        structures: List of structures detected in the original algorithm
        offset: Offset to map positions from algo to original algorithm
        structure_cache: Cache for detected structures (key: str(algo))

    Returns:
        Compressed algorithm string with bracket notation.

    """
    if structure_cache is None:
        structure_cache = {}

    result: list[str] = []
    i = 0

    while i < len(algo):
        # Find structure at current position (accounting for offset)
        found = None
        for struct in structures:
            if struct.start == offset + i:
                found = struct
                break

        if found:
            # Recursively compress nested structures in setup and action
            # Use cache to avoid redundant detection
            setup_key = str(found.setup)
            if setup_key not in structure_cache:
                structure_cache[setup_key] = detect_structures(found.setup)
            setup_structures = structure_cache[setup_key]

            action_key = str(found.action)
            if action_key not in structure_cache:
                structure_cache[action_key] = detect_structures(found.action)
            action_structures = structure_cache[action_key]

            # Recursively compress if nested structures found
            if setup_structures:
                setup_str = compress_recursive(
                    found.setup, setup_structures, 0, structure_cache,
                )
            else:
                setup_str = setup_key

            if action_structures:
                action_str = compress_recursive(
                    found.action, action_structures, 0, structure_cache,
                )
            else:
                action_str = action_key

            if found.type == 'conjugate':
                result.append(f'[{setup_str}: {action_str}]')
            else:
                result.append(f'[{setup_str}, {action_str}]')

            # Skip past the entire structure
            i += found.end - found.start
        else:
            # No structure, output the move
            result.append(str(algo[i]))
            i += 1

    return ' '.join(result)


def compress(
    algo: 'Algorithm',
    max_setup_len: int | None = None,
    min_score: float | None = None,
    structures: list[Structure] | None = None,
    structure_cache: StructureCache | None = None,
) -> str:
    """
    Compress an algorithm into bracket notation showing its structure.

    This function detects conjugates [A: B] and commutators [A, B] within
    the algorithm and returns a compressed notation that illustrates the
    structure.

    Detection thresholds are automatically determined based on algorithm
    length if not explicitly provided.

    Args:
        algo: The algorithm to compress
        max_setup_len: Maximum setup sequence length (auto-calculated)
        min_score: Minimum structure score (auto-calculated)
        structures: Pre-computed structures to skip redundant detection
        structure_cache: Shared cache for nested structure detection

    Returns:
        Compressed notation string

    Examples:
        >>> algo = Algorithm.parse_moves("R U R' U'")
        >>> compress(algo)
        '[R, U]'

        >>> algo = Algorithm.parse_moves("F R U R' U' F'")
        >>> compress(algo)
        '[F: [R, U]]'

    """
    if structures is None:
        structures = detect_structures(algo, max_setup_len, min_score)

    if structure_cache is None:
        structure_cache = {}

    # Early return for single structure (no sorting/filtering needed)
    if len(structures) <= 1:
        return compress_recursive(algo, structures, 0, structure_cache)

    # Build a non-overlapping set of structures using greedy approach
    # Sort by start position for efficient overlap detection
    sorted_structures = sorted(structures, key=lambda s: s.start)
    non_overlapping: list[Structure] = []
    last_end = 0

    for struct in sorted_structures:
        # Structures sorted by start: check against last_end only
        if struct.start >= last_end:
            non_overlapping.append(struct)
            last_end = struct.end

    return compress_recursive(algo, non_overlapping, 0, structure_cache)


def count_all_structures(
    structures: list[Structure],
    max_depth: int = DEFAULT_MAX_NESTING_DEPTH,
    current_depth: int = 0,
    structure_cache: StructureCache | None = None,
) -> tuple[int, int, int]:
    """
    Recursively count all structures including nested ones.

    Args:
        structures: List of structures to count
        max_depth: Maximum recursion depth (default: 10)
        current_depth: Current recursion depth (used internally)
        structure_cache: Cache for detected structures (key: str(algo))

    Returns:
        (total_count, conjugate_count, commutator_count)

    """
    if structure_cache is None:
        structure_cache = {}

    # Early termination if max depth reached
    if current_depth >= max_depth:
        total = len(structures)
        conjugate_count = sum(1 for s in structures if s.type == 'conjugate')
        commutator_count = sum(1 for s in structures if s.type == 'commutator')
        return total, conjugate_count, commutator_count

    total = len(structures)
    conjugate_count = sum(1 for s in structures if s.type == 'conjugate')
    commutator_count = sum(1 for s in structures if s.type == 'commutator')

    for struct in structures:
        # Check for nested structures in setup and action
        # Use cache to avoid redundant detection (use string keys)
        setup_key = str(struct.setup)
        if setup_key not in structure_cache:
            structure_cache[setup_key] = detect_structures(
                struct.setup,
            )
        setup_structures = structure_cache[setup_key]

        action_key = str(struct.action)
        if action_key not in structure_cache:
            structure_cache[action_key] = detect_structures(
                struct.action,
            )
        action_structures = structure_cache[action_key]

        # Recursively count nested structures
        if setup_structures:
            setup_total, setup_conj, setup_comm = count_all_structures(
                setup_structures,
                max_depth,
                current_depth + 1,
                structure_cache,
            )
            total += setup_total
            conjugate_count += setup_conj
            commutator_count += setup_comm

        if action_structures:
            action_total, action_conj, action_comm = count_all_structures(
                action_structures,
                max_depth,
                current_depth + 1,
                structure_cache,
            )
            total += action_total
            conjugate_count += action_conj
            commutator_count += action_comm

    return total, conjugate_count, commutator_count


def calculate_nesting_depth(
    structures: list[Structure],
    structure_cache: StructureCache | None = None,
    max_depth: int = DEFAULT_MAX_NESTING_DEPTH,
    current_depth: int = 0,
) -> tuple[int, int]:
    """
    Calculate the maximum nesting depth and count of nested structures.

    Args:
        structures: List of structures to analyze
        structure_cache: Cache for detected structures (key: str(algo))
        max_depth: Maximum recursion depth (default: 10)
        current_depth: Current recursion depth (used internally)

    Returns:
        Tuple of (maximum nesting depth, number of nested structures).

    """
    if structure_cache is None:
        structure_cache = {}

    # Early termination if max depth reached
    if current_depth >= max_depth:
        return (1 if structures else 0), 0

    depth = 0
    nested_count = 0

    for struct in structures:
        # Check if setup or action contains nested structures
        # Use cache to avoid redundant detection (use string keys)
        setup_key = str(struct.setup)
        if setup_key not in structure_cache:
            structure_cache[setup_key] = detect_structures(struct.setup)
        setup_structures = structure_cache[setup_key]

        action_key = str(struct.action)
        if action_key not in structure_cache:
            structure_cache[action_key] = detect_structures(struct.action)
        action_structures = structure_cache[action_key]

        if setup_structures or action_structures:
            nested_count += 1
            # Recursively calculate depth
            setup_depth, _ = (
                calculate_nesting_depth(
                    setup_structures, structure_cache,
                    max_depth, current_depth + 1,
                )
                if setup_structures else (0, 0)
            )
            action_depth, _ = (
                calculate_nesting_depth(
                    action_structures, structure_cache,
                    max_depth, current_depth + 1,
                )
                if action_structures else (0, 0)
            )
            depth = max(depth, 1 + max(setup_depth, action_depth))
        else:
            depth = max(depth, 1)

    return depth, nested_count


def calculate_efficiency_rating(
    pure_count: int,
    a9_count: int,
    avg_moves: float,
    total_structures: int,
) -> str:
    """
    Calculate an efficiency rating based on structure classifications.

    Ratings:
    - 'Excellent': Mostly pure commutators and A9s
    - 'Good': Mix of efficient structures
    - 'Fair': Average efficiency
    - 'Poor': Mostly inefficient structures

    Args:
        pure_count: Number of pure commutators.
        a9_count: Number of A9 commutators.
        avg_moves: Average move count per structure.
        total_structures: Total number of structures.

    Returns:
        Efficiency rating string (Excellent, Good, Fair, Poor, or N/A).

    """
    if total_structures == 0:
        return 'N/A'

    efficient_ratio = (pure_count + a9_count) / total_structures

    if (efficient_ratio >= EFFICIENCY_EXCELLENT_RATIO and
            avg_moves <= EFFICIENCY_EXCELLENT_AVG_MOVES):
        return 'Excellent'
    if (efficient_ratio >= EFFICIENCY_GOOD_RATIO or
            avg_moves <= EFFICIENCY_GOOD_AVG_MOVES):
        return 'Good'
    if avg_moves <= EFFICIENCY_FAIR_AVG_MOVES:
        return 'Fair'
    return 'Poor'


def compute_structure_stats(structures: list[Structure]) -> StructureStats:  # noqa: PLR0914
    """
    Compute aggregated metrics over a list of structures in a single pass.

    Returns:
        StructureStats with all per-structure metrics aggregated.

    """
    if not structures:
        return StructureStats(
            average_structure_score=0.0,
            best_structure_score=0.0,
            shortest_setup_length=0,
            longest_setup_length=0,
            average_setup_length=0.0,
            shortest_action_length=0,
            longest_action_length=0,
            average_action_length=0.0,
            covered_moves=0,
            pure_commutator_count=0,
            a9_commutator_count=0,
            nested_conjugate_count=0,
            simple_conjugate_count=0,
            structures_with_cancellations=0,
            average_move_count=0.0,
            efficiency_rating=calculate_efficiency_rating(0, 0, 0.0, 0),
        )

    avg_score = sum(s.score for s in structures) / len(structures)
    best_score = max(s.score for s in structures)

    shortest_setup = longest_setup = 0
    shortest_action = longest_action = 0
    total_setup_len = 0
    total_action_len = 0
    covered_moves = 0
    total_move_count = 0
    pure_comm_count = 0
    a9_comm_count = 0
    nested_conj_count = 0
    simple_conj_count = 0
    cancel_count = 0

    for i, s in enumerate(structures):
        setup_len = len(s.setup)
        action_len = len(s.action)

        if i == 0:
            shortest_setup = longest_setup = setup_len
            shortest_action = longest_action = action_len
        else:
            shortest_setup = min(shortest_setup, setup_len)
            longest_setup = max(longest_setup, setup_len)
            shortest_action = min(shortest_action, action_len)
            longest_action = max(longest_action, action_len)

        total_setup_len += setup_len
        total_action_len += action_len
        covered_moves += s.end - s.start
        total_move_count += s.move_count

        if s.type == 'commutator':
            if s.is_pure:
                pure_comm_count += 1
            elif s.classification == 'A9':
                a9_comm_count += 1
        elif s.classification == 'nested':
            nested_conj_count += 1
        elif s.classification == 'simple':
            simple_conj_count += 1

        if s.has_cancellations:
            cancel_count += 1

    struct_count = len(structures)
    avg_move_count = total_move_count / struct_count

    return StructureStats(
        average_structure_score=avg_score,
        best_structure_score=best_score,
        shortest_setup_length=shortest_setup,
        longest_setup_length=longest_setup,
        average_setup_length=total_setup_len / struct_count,
        shortest_action_length=shortest_action,
        longest_action_length=longest_action,
        average_action_length=total_action_len / struct_count,
        covered_moves=covered_moves,
        pure_commutator_count=pure_comm_count,
        a9_commutator_count=a9_comm_count,
        nested_conjugate_count=nested_conj_count,
        simple_conjugate_count=simple_conj_count,
        structures_with_cancellations=cancel_count,
        average_move_count=avg_move_count,
        efficiency_rating=calculate_efficiency_rating(
            pure_comm_count, a9_comm_count, avg_move_count, struct_count,
        ),
    )


def untime_algorithm(algo: 'Algorithm') -> 'Algorithm':
    """
    Return the algorithm with the timing information removed.

    Args:
        algo: The algorithm to strip.

    Returns:
        The same algorithm without timestamps.

    """
    from cubing_algs.transform.timing import untime_moves  # noqa: PLC0415

    return algo.transform(untime_moves)


def compute_structure(  # noqa: PLR0914
    algo: 'Algorithm',
    max_setup_len: int | None = None,
    min_score: float | None = None,
) -> StructureData:
    """
    Compute comprehensive structure analysis for an algorithm.

    This function analyzes various aspects of algorithm structure including:
    - Detection of conjugate and commutator patterns
    - Nesting analysis and depth calculation
    - Compression metrics and ratios
    - Setup and action length statistics
    - Coverage analysis

    Detection thresholds are automatically determined based on algorithm
    length if not explicitly provided.

    Timing is dropped first: move equality includes timestamps, which
    would keep the inverse-sequence lookups from ever matching.

    Args:
        algo: The algorithm to analyze
        max_setup_len: Maximum setup sequence length (auto-calculated)
        min_score: Minimum structure score (auto-calculated)

    Returns:
        StructureData with all calculated structure metrics.

    """
    algo = untime_algorithm(algo)

    original_str = str(algo)
    structures = detect_structures(algo, max_setup_len, min_score)

    # Shared cache threads through all nested-detection calls below
    structure_cache: StructureCache = {}

    compressed_str = compress(
        algo, max_setup_len, min_score, structures, structure_cache,
    )
    total_count, conjugate_count, commutator_count = (
        count_all_structures(structures, structure_cache=structure_cache)
        if structures else (0, 0, 0)
    )
    max_depth, nested_count = (
        calculate_nesting_depth(structures, structure_cache)
        if structures else (0, 0)
    )

    original_length = len(algo)
    compressed_length = len(compressed_str)
    compression_ratio = (
        1.0 - (compressed_length / len(original_str))
        if original_length > 0 else 0.0
    )

    stats = compute_structure_stats(structures)
    uncovered = original_length - stats.covered_moves
    coverage = (
        stats.covered_moves / original_length if original_length > 0 else 0.0
    )

    return StructureData(
        original=original_str,
        compressed=compressed_str,
        total_structures=total_count,
        conjugate_count=conjugate_count,
        commutator_count=commutator_count,
        max_nesting_depth=max_depth,
        nested_structure_count=nested_count,
        original_length=original_length,
        compressed_notation_char_length=compressed_length,
        compression_ratio=compression_ratio,
        average_structure_score=stats.average_structure_score,
        best_structure_score=stats.best_structure_score,
        structures=structures,
        shortest_setup_length=stats.shortest_setup_length,
        longest_setup_length=stats.longest_setup_length,
        average_setup_length=stats.average_setup_length,
        shortest_action_length=stats.shortest_action_length,
        longest_action_length=stats.longest_action_length,
        average_action_length=stats.average_action_length,
        coverage_ratio=coverage,
        uncovered_moves=uncovered,
        pure_commutator_count=stats.pure_commutator_count,
        a9_commutator_count=stats.a9_commutator_count,
        nested_conjugate_count=stats.nested_conjugate_count,
        simple_conjugate_count=stats.simple_conjugate_count,
        structures_with_cancellations=stats.structures_with_cancellations,
        average_move_count=stats.average_move_count,
        efficiency_rating=stats.efficiency_rating,
    )
