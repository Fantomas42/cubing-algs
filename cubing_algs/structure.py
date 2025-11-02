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

import typing
from collections import OrderedDict
from collections.abc import MutableMapping
from dataclasses import dataclass
from typing import TYPE_CHECKING
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
PURE_COMMUTATOR_TOTAL_MOVES = 8  # Total moves in pure commutator
COMMUTATOR_A9_TOTAL_MOVES = 10  # Total moves in A9 commutator (before cancel)
SIMPLE_CONJUGATE_MAX_SETUP = 2  # Max setup length for "simple" conjugates
MULTI_SETUP_MIN_LENGTH = 3  # Min setup length for "multi-setup" conjugates

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

# Early termination threshold
EARLY_TERMINATION_SCORE = 50.0  # Stop searching if structure score exceeds this

# Cache size limits (LRU behavior)
MAX_INVERSE_CACHE_SIZE = 1000  # Maximum entries in inverse cache
MAX_STRING_CACHE_SIZE = 1000  # Maximum entries in string cache
MAX_STRUCTURE_CACHE_SIZE = 500  # Maximum entries in structure cache


class BoundedCache[K, V](MutableMapping[K, V]):
    """
    Bounded cache with LRU eviction using OrderedDict.

    This is a lightweight wrapper around OrderedDict that automatically
    evicts the least recently used item when capacity is reached.
    """

    def __init__(self, maxsize: int) -> None:
        """Initialize bounded cache with maximum size."""
        self._cache: OrderedDict[K, V] = OrderedDict()
        self._maxsize = maxsize

    def __getitem__(self, key: K) -> V:
        """
        Get item from cache and mark as recently used.

        Args:
            key: Cache key to retrieve.

        Returns:
            Cached value for the given key.

        """
        value = self._cache[key]
        self._cache.move_to_end(key)
        return value

    def __setitem__(self, key: K, value: V) -> None:
        """Set item in cache, evicting least recently used if at capacity."""
        if key in self._cache:
            self._cache.move_to_end(key)
        elif len(self._cache) >= self._maxsize:
            self._cache.popitem(last=False)  # Remove oldest (LRU)
        self._cache[key] = value

    def __delitem__(self, key: K) -> None:
        """Remove item from cache."""
        del self._cache[key]

    def __iter__(self) -> typing.Iterator[K]:
        """
        Iterate over cache keys.

        Returns:
            Iterator over cache keys.

        """
        return iter(self._cache)

    def __len__(self) -> int:
        """
        Return number of items in cache.

        Returns:
            Number of cached items.

        """
        return len(self._cache)


@dataclass
class Structure:
    """Represents a detected structure (conjugate or commutator)."""

    type: str  # 'conjugate' or 'commutator'
    setup: 'Algorithm'  # The A part
    action: 'Algorithm'  # The B part
    start: int  # Start index in original algorithm
    end: int  # End index in original algorithm
    score: float  # Quality score (higher is better)
    classification: str = ''  # Classification type (pure, A9, orthogonal, etc.)
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
    compressed_notation_length: int
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
    coverage_percent: float  # Percentage of moves covered by structures
    uncovered_moves: int

    # Classification statistics (NEW)
    pure_commutator_count: int  # Pure 8-move commutators
    a9_commutator_count: int  # 9-move commutators with cancellation
    nested_conjugate_count: int  # Conjugates with nested structures
    simple_conjugate_count: int  # Simple conjugates (1-2 move setup)
    structures_with_cancellations: int  # Structures with move cancellations
    average_move_count: float  # Average moves per structure
    efficiency_rating: str  # Overall efficiency assessment


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
    from cubing_algs.transform.mirror import mirror_moves  # noqa: PLC0415

    return algo.transform(mirror_moves)


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


def classify_commutator(
    setup: 'Algorithm',
    action: 'Algorithm',
    inverse_cache: dict[str, 'Algorithm'] | BoundedCache[str, 'Algorithm'],
) -> str:
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
        inverse_cache: Cache for inverse sequences (key: str(pattern))

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

    # Check for potential cancellations (use cached inverse)
    setup_key = str(setup)
    if setup_key not in inverse_cache:
        inverse_cache[setup_key] = inverse_sequence(setup)
    setup_inv = inverse_cache[setup_key]

    has_cancel = (
        detect_move_cancellations(setup, action) or
        detect_move_cancellations(action, setup_inv)
    )

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


def classify_conjugate(setup: 'Algorithm', action: 'Algorithm') -> str:
    """
    Classify a conjugate based on structure and efficiency.

    Classifications:
    - 'simple': Short setup (1-2 moves) with commutator action
    - 'nested': Action contains a structure
    - 'multi-setup': Long setup (3+ moves)
    - 'standard': Regular conjugate pattern

    Args:
        setup: The setup (A) part of the conjugate.
        action: The action (B) part of the conjugate.

    Returns:
        Classification string (simple, nested, multi-setup, or standard).

    """
    setup_len = len(setup)

    # Check if action contains nested structures
    # Use very low threshold to detect any potential nested structure
    max_setup = calculate_max_setup_length(len(action))
    action_structures = detect_structures(
        action,
        max_setup_len=max_setup,
        min_score=CLASSIFICATION_MIN_SCORE,
    )
    has_nested = any(s.type == 'commutator' for s in action_structures)

    if has_nested:
        return 'nested'

    if setup_len <= SIMPLE_CONJUGATE_MAX_SETUP:
        return 'simple'

    if setup_len >= MULTI_SETUP_MIN_LENGTH:
        return 'multi-setup'

    return 'standard'


def is_inverse_at(
    algo: 'Algorithm',
    start: int,
    pattern: 'Algorithm',
    inverse_cache: dict[str, 'Algorithm'] | BoundedCache[str, 'Algorithm'],
) -> bool:
    """
    Check if the inverse of pattern appears at the given position.

    Args:
        algo: The algorithm to check
        start: Position to check
        pattern: The pattern to invert and match
        inverse_cache: Cache for inverse sequences (key: str(pattern))

    Returns:
        True if the inverse appears at the position, False otherwise.

    """
    if start + len(pattern) > len(algo):
        return False

    # Use cache (cache by string representation)
    pattern_key = str(pattern)
    if pattern_key not in inverse_cache:
        inverse_cache[pattern_key] = inverse_sequence(pattern)
    inverse = inverse_cache[pattern_key]

    # Vectorized comparison: slice comparison is faster than element-by-element
    return algo[start:start + len(inverse)] == inverse


def score_structure(setup: 'Algorithm', action: 'Algorithm') -> float:
    """
    Score a potential structure based on compression ratio and meaningfulness.

    Higher scores indicate better structures. We prefer:
    - Shorter setups relative to actions
    - Non-trivial actions (longer is better)
    - Overall compression benefit

    Args:
        setup: The setup (A) part of the structure.
        action: The action (B) part of the structure.

    Returns:
        Quality score (higher is better, 0-100+ range).

    """
    if len(setup) == 0 or len(action) == 0:
        return 0.0

    # Compression ratio: how much we save by using bracket notation
    original_length = len(setup) * 2 + len(action)
    compressed_length = len(setup) + len(action)
    compression_ratio = (original_length - compressed_length) / original_length

    # Favor longer actions (more meaningful)
    action_weight = min(len(action) / ACTION_WEIGHT_DIVISOR, 1.0)

    # Penalize very long setups relative to action
    setup_penalty = 1.0
    if len(setup) > len(action):
        setup_penalty = len(action) / len(setup)

    return compression_ratio * action_weight * setup_penalty * SCORE_MULTIPLIER


def detect_conjugate(
    algo: 'Algorithm',
    start: int,
    max_setup_len: int,
    inverse_cache: dict[str, 'Algorithm'] | BoundedCache[str, 'Algorithm'],
) -> Structure | None:
    """
    Detect a conjugate pattern [A: B] = A B A' starting at the given position.

    Args:
        algo: The algorithm to search
        start: Starting position
        max_setup_len: Maximum setup length
        inverse_cache: Cache for inverse sequences (key: str(algo))

    Returns:
        Best conjugate structure found, or None if no valid structure exists.

    """
    best_structure: Structure | None = None

    # Cache algorithm length to avoid repeated calls
    algo_len = len(algo)

    # Try different setup lengths
    for setup_len in range(1, max_setup_len + 1):
        if start + setup_len * 2 > algo_len:
            break

        # Early termination: if we have a very high-scoring structure
        if best_structure and best_structure.score >= EARLY_TERMINATION_SCORE:
            break

        from cubing_algs.algorithm import Algorithm as Algo  # noqa: PLC0415

        setup = Algo(algo[start:start + setup_len])

        # Look for A' after some action B
        for action_len in range(1, algo_len - start - setup_len * 2 + 1):
            action_end = start + setup_len + action_len

            if action_end + setup_len > algo_len:
                break

            action = Algo(algo[start + setup_len:action_end])

            # Check if A' appears after B (uses cached inverse)
            if is_inverse_at(
                algo, action_end, setup, inverse_cache,
            ):
                score = score_structure(setup, action)

                if best_structure is None or score > best_structure.score:
                    # Classify and analyze the conjugate
                    classification = classify_conjugate(setup, action)
                    has_cancel = detect_move_cancellations(setup, action)
                    move_count = setup_len * 2 + action_len

                    best_structure = Structure(
                        type='conjugate',
                        setup=setup,
                        action=action,
                        start=start,
                        end=action_end + setup_len,
                        score=score,
                        classification=classification,
                        has_cancellations=has_cancel,
                        move_count=move_count,
                        is_pure=False,
                    )

                    # Early termination: if score is very high, stop searching
                    if score >= EARLY_TERMINATION_SCORE:
                        return best_structure

    return best_structure


def detect_commutator(
    algo: 'Algorithm',
    start: int,
    max_part_len: int,
    inverse_cache: dict[str, 'Algorithm'] | BoundedCache[str, 'Algorithm'],
) -> Structure | None:
    """
    Detect a commutator pattern [A, B] = A B A' B'.

    Args:
        algo: The algorithm to search
        start: Starting position
        max_part_len: Maximum length for A and B parts
        inverse_cache: Cache for inverse sequences (key: str(algo))

    Returns:
        Best commutator structure found, or None if no valid structure exists.

    """
    best_structure: Structure | None = None

    # Cache algorithm length to avoid repeated calls
    algo_len = len(algo)

    # Try different A lengths
    for a_len in range(1, max_part_len + 1):
        if start + a_len * 2 > algo_len:
            break

        # Early termination: if we have a very high-scoring structure
        if best_structure and best_structure.score >= EARLY_TERMINATION_SCORE:
            break

        from cubing_algs.algorithm import Algorithm as Algo  # noqa: PLC0415

        a_part = Algo(algo[start:start + a_len])

        # Try different B lengths
        for b_len in range(1, algo_len - start - a_len * 2 + 1):
            b_end = start + a_len + b_len

            if b_end + a_len + b_len > algo_len:
                break

            b_part = Algo(algo[start + a_len:b_end])

            # Check if A' B' appears after A B (uses cached inverses)
            if (
                is_inverse_at(
                    algo, b_end, a_part, inverse_cache,
                )
                and is_inverse_at(
                    algo, b_end + a_len, b_part, inverse_cache,
                )
            ):
                score = score_structure(a_part, b_part)

                if best_structure is None or score > best_structure.score:
                    # Get/compute inverse for cancellation check
                    a_part_key = str(a_part)
                    if a_part_key not in inverse_cache:
                        inverse_cache[a_part_key] = inverse_sequence(a_part)
                    a_part_inv = inverse_cache[a_part_key]

                    # Classify and analyze the commutator
                    classification = classify_commutator(
                        a_part, b_part, inverse_cache,
                    )
                    has_cancel = (
                        detect_move_cancellations(a_part, b_part) or
                        detect_move_cancellations(b_part, a_part_inv)
                    )
                    move_count = a_len * 2 + b_len * 2
                    is_pure_comm = (
                        a_len == PURE_COMMUTATOR_SETUP_LEN
                        and b_len == PURE_COMMUTATOR_ACTION_LEN
                    )

                    best_structure = Structure(
                        type='commutator',
                        setup=a_part,
                        action=b_part,
                        start=start,
                        end=b_end + a_len + b_len,
                        score=score,
                        classification=classification,
                        has_cancellations=has_cancel,
                        move_count=move_count,
                        is_pure=is_pure_comm,
                    )

                    # Early termination: if score is very high, stop searching
                    if score >= EARLY_TERMINATION_SCORE:
                        return best_structure

    return best_structure


def detect_structures(
    algo: 'Algorithm',
    max_setup_len: int | None = None,
    min_score: float | None = None,
    max_depth: int = DEFAULT_MAX_NESTING_DEPTH,  # noqa: ARG001
) -> list[Structure]:
    """
    Detect all meaningful conjugate and commutator structures in an algorithm.

    The function automatically determines appropriate thresholds based on
    algorithm length if not explicitly provided.

    Args:
        algo: The algorithm to analyze
        max_setup_len: Maximum setup sequence length (auto-calculated)
        min_score: Minimum structure score (auto-calculated)
        max_depth: Max recursion depth for nested detection (default: 10)

    Returns:
        List of detected structures, sorted by position

    """
    # Use heuristics if parameters not provided
    algo_len = len(algo)
    if max_setup_len is None:
        max_setup_len = calculate_max_setup_length(algo_len)
    if min_score is None:
        min_score = calculate_min_score(algo_len)

    # Create single shared cache for both commutator and conjugate detection
    # Now safe because we eliminated the string_cache with id() keys
    inverse_cache: BoundedCache[str, Algorithm] = BoundedCache(
        MAX_INVERSE_CACHE_SIZE,
    )

    structures: list[Structure] = []
    i = 0

    while i < len(algo):
        # Try to detect commutator first (more specific)
        commutator = detect_commutator(
            algo, i, max_setup_len, inverse_cache,
        )

        # Try to detect conjugate (shares same cache)
        conjugate = detect_conjugate(
            algo, i, max_setup_len, inverse_cache,
        )

        # Pick the best one
        best = None
        if commutator and conjugate:
            best = (
                commutator if commutator.score >= conjugate.score
                else conjugate
            )
        elif commutator:
            best = commutator
        elif conjugate:
            best = conjugate

        if best and best.score >= min_score:
            structures.append(best)
            i = best.end
        else:
            i += 1

    return structures


def compress_recursive(  # noqa: C901, PLR0912
    algo: 'Algorithm',
    structures: list[Structure],
    offset: int = 0,
    structure_cache: dict[str, list[Structure]] | None = None,
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
    structures = detect_structures(algo, max_setup_len, min_score)

    # Early return for single structure (no sorting/filtering needed)
    if len(structures) <= 1:
        structure_cache: dict[str, list[Structure]] = {}
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

    # Create cache for nested structure detection (use string keys)
    structure_cache = {}
    return compress_recursive(algo, non_overlapping, 0, structure_cache)


def count_all_structures(
    structures: list[Structure],
    max_depth: int = DEFAULT_MAX_NESTING_DEPTH,
    current_depth: int = 0,
    structure_cache: dict[str, list[Structure]] | None = None,
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
                max_depth=max_depth - current_depth - 1,
            )
        setup_structures = structure_cache[setup_key]

        action_key = str(struct.action)
        if action_key not in structure_cache:
            structure_cache[action_key] = detect_structures(
                struct.action,
                max_depth=max_depth - current_depth - 1,
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
    structure_cache: dict[str, list[Structure]] | None = None,
) -> tuple[int, int]:
    """
    Calculate the maximum nesting depth and count of nested structures.

    Args:
        structures: List of structures to analyze
        structure_cache: Cache for detected structures (key: str(algo))

    Returns:
        Tuple of (maximum nesting depth, number of nested structures).

    """
    if structure_cache is None:
        structure_cache = {}

    max_depth = 0
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
                calculate_nesting_depth(setup_structures, structure_cache)
                if setup_structures else (0, 0)
            )
            action_depth, _ = (
                calculate_nesting_depth(action_structures, structure_cache)
                if action_structures else (0, 0)
            )
            max_depth = max(max_depth, 1 + max(setup_depth, action_depth))
        else:
            max_depth = max(max_depth, 1)

    return max_depth, nested_count


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


def compute_structure(  # noqa: C901, PLR0914, PLR0912, PLR0915
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

    Args:
        algo: The algorithm to analyze
        max_setup_len: Maximum setup sequence length (auto-calculated)
        min_score: Minimum structure score (auto-calculated)

    Returns:
        StructureData: Namedtuple containing all calculated structure metrics:
            - original: Original algorithm string
            - compressed: Compressed notation string
            - total_structures: Total number of structures detected
            - conjugate_count: Number of conjugate patterns
            - commutator_count: Number of commutator patterns
            - max_nesting_depth: Maximum nesting depth of structures
            - nested_structure_count: Number of nested structures
            - original_length: Length of original algorithm
            - compressed_notation_length: Length of compressed notation
            - compression_ratio: Ratio of compression (0.0-1.0)
            - average_structure_score: Average quality score
            - best_structure_score: Highest quality score
            - structures: List of detected Structure objects
            - shortest_setup_length: Shortest setup sequence length
            - longest_setup_length: Longest setup sequence length
            - average_setup_length: Average setup sequence length
            - shortest_action_length: Shortest action sequence length
            - longest_action_length: Longest action sequence length
            - average_action_length: Average action sequence length
            - coverage_percent: Percentage of moves covered by structures
            - uncovered_moves: Number of moves not in any structure

    """
    original_str = str(algo)
    structures = detect_structures(algo, max_setup_len, min_score)

    # Create shared cache for all nested structure detection (use string keys)
    structure_cache: dict[str, list[Structure]] = {}

    # Use cached compression
    compressed_str = compress(algo, max_setup_len, min_score)

    # Count structure types (including nested structures) with cache
    total_count, conjugate_count, commutator_count = (
        count_all_structures(structures, structure_cache=structure_cache)
        if structures else (0, 0, 0)
    )

    # Calculate nesting with cache
    max_depth, nested_count = (
        calculate_nesting_depth(structures, structure_cache)
        if structures else (0, 0)
    )

    # Compression metrics
    original_length = len(algo)
    compressed_length = len(compressed_str)
    compression_ratio = 0.0
    if original_length > 0:
        compression_ratio = 1.0 - (compressed_length / len(original_str))

    # Structure quality scores
    avg_score = 0.0
    best_score = 0.0
    if structures:
        avg_score = sum(s.score for s in structures) / len(structures)
        best_score = max(s.score for s in structures)

    # Batch all structure iterations into a single pass for better performance
    shortest_setup = 0
    longest_setup = 0
    total_setup_len = 0
    shortest_action = 0
    longest_action = 0
    total_action_len = 0
    covered_moves = 0
    total_move_count = 0
    pure_comm_count = 0
    a9_comm_count = 0
    nested_conj_count = 0
    simple_conj_count = 0
    cancel_count = 0

    if structures:
        # Single pass over all structures to compute all metrics
        for i, s in enumerate(structures):
            setup_len = len(s.setup)
            action_len = len(s.action)

            # Setup/action length tracking
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

            # Coverage
            covered_moves += s.end - s.start

            # Move count
            total_move_count += s.move_count

            # Classification counts - branch once on type to reduce comparisons
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
        avg_setup = total_setup_len / struct_count
        avg_action = total_action_len / struct_count
        avg_move_count = total_move_count / struct_count
    else:
        avg_setup = 0.0
        avg_action = 0.0
        avg_move_count = 0.0

    # Coverage analysis
    uncovered = original_length - covered_moves
    coverage = 0.0
    if original_length > 0:
        coverage = covered_moves / original_length

    # Efficiency rating based on classifications
    efficiency = calculate_efficiency_rating(
        pure_comm_count,
        a9_comm_count,
        avg_move_count,
        len(structures),
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
        compressed_notation_length=compressed_length,
        compression_ratio=compression_ratio,
        average_structure_score=avg_score,
        best_structure_score=best_score,
        structures=structures,
        shortest_setup_length=shortest_setup,
        longest_setup_length=longest_setup,
        average_setup_length=avg_setup,
        shortest_action_length=shortest_action,
        longest_action_length=longest_action,
        average_action_length=avg_action,
        coverage_percent=coverage,
        uncovered_moves=uncovered,
        pure_commutator_count=pure_comm_count,
        a9_commutator_count=a9_comm_count,
        nested_conjugate_count=nested_conj_count,
        simple_conjugate_count=simple_conj_count,
        structures_with_cancellations=cancel_count,
        average_move_count=avg_move_count,
        efficiency_rating=efficiency,
    )
