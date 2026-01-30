"""
Low-level piece manipulation for cube scrambling.

This module provides functions to manipulate individual cube pieces
(corners and edges) while maintaining physical constraints:
- Corner orientation sum: sum(co) % 3 == 0
- Edge orientation sum: sum(eo) % 2 == 0
- Permutation parity: parity(cp) == parity(ep)

All functions use buffer pieces to absorb necessary fixes.
"""
from random import Random

from cubing_algs.annotations import CubeCubies
from cubing_algs.annotations import Orientation
from cubing_algs.annotations import Permutation
from cubing_algs.constants import CORNER_MODULUS
from cubing_algs.constants import CORNER_NUMBER
from cubing_algs.constants import EDGE_MODULUS
from cubing_algs.constants import EDGE_NUMBER
from cubing_algs.constants import SOLVED_CO
from cubing_algs.constants import SOLVED_CP
from cubing_algs.constants import SOLVED_EO
from cubing_algs.constants import SOLVED_EP
from cubing_algs.integrity import compute_parity
from cubing_algs.scrambler.constants import DEFAULT_RNG


def swap_pieces(
        perm: Permutation,
        orient: Orientation,
        idx_a: int,
        idx_b: int,
) -> None:
    """
    Swap two pieces in permutation and orientation arrays.

    Args:
        perm: Permutation array (cp or ep).
        orient: Orientation array (co or eo).
        idx_a: First index to swap.
        idx_b: Second index to swap.

    """
    perm[idx_a], perm[idx_b] = perm[idx_b], perm[idx_a]
    orient[idx_a], orient[idx_b] = orient[idx_b], orient[idx_a]


def shuffle_in_place(
        perm: Permutation,
        orient: Orientation,
        indices: list[int],
        rng: Random,
) -> bool:
    """
    Fischer-Yates shuffle for pieces at specified indices.

    Shuffles both permutation and orientation arrays in place.

    Args:
        perm: Permutation array (cp or ep).
        orient: Orientation array (co or eo).
        indices: Indices of pieces to shuffle.
        rng: Random number generator.

    Returns:
        True if even number of swaps were made, False otherwise.

    """
    even_swaps = True
    for i in range(len(indices) - 1):
        j = rng.randint(i, len(indices) - 1)
        if i != j:
            swap_pieces(perm, orient, indices[i], indices[j])
            even_swaps = not even_swaps
    return even_swaps


def fix_parity_with_buffer(  # noqa: PLR0913, PLR0917
        cp: Permutation,
        co: Orientation,
        ep: Permutation,
        eo: Orientation,
        buffer_corners: list[int],
        buffer_edges: list[int],
) -> None:
    """
    Fix parity mismatch by swapping two buffer pieces.

    Swaps two pieces from either buffer_corners or buffer_edges to fix
    the parity constraint (parity(cp) == parity(ep)).

    Args:
        cp: Corner permutations.
        co: Corner orientations.
        ep: Edge permutations.
        eo: Edge orientations.
        buffer_corners: Corners that can absorb parity fixes.
        buffer_edges: Edges that can absorb parity fixes.

    """
    if len(buffer_edges) >= 2:
        swap_pieces(ep, eo, buffer_edges[0], buffer_edges[1])
    elif len(buffer_corners) >= 2:
        swap_pieces(cp, co, buffer_corners[0], buffer_corners[1])


def random_permutation(
        corners: list[int],
        edges: list[int],
        rng: Random | None = None,
) -> CubeCubies:
    """
    Generate random permutation for both corners and edges together.

    This function shuffles both corners and edges while maintaining the
    parity constraint (parity(cp) == parity(ep)). Parity is fixed by
    swapping within the permuted sets, never touching other pieces.

    Args:
        corners: Indices of corners to permute.
        edges: Indices of edges to permute.
        rng: Random number generator (uses DEFAULT_RNG if None).

    Returns:
        Tuple of (cp, co, ep, eo) - corner/edge permutation and orientation.

    """
    if rng is None:
        rng = DEFAULT_RNG

    cp = SOLVED_CP.copy()
    co = SOLVED_CO.copy()
    ep = SOLVED_EP.copy()
    eo = SOLVED_EO.copy()

    # Use _shuffle_in_place for Fischer-Yates shuffle
    # Note: co/eo are all zeros, so shuffling them has no effect
    corners_even = shuffle_in_place(cp, co, corners, rng)
    edges_even = shuffle_in_place(ep, eo, edges, rng)

    # Fix parity if needed by swapping within permuted pieces
    # Parity is odd if exactly one shuffle had odd swaps
    if corners_even != edges_even:
        if len(corners) == 0:
            # No corners - must swap edges
            swap_pieces(ep, eo, edges[0], edges[1])
        elif len(edges) == 0 or rng.random() < 0.5:  # noqa: PLR2004
            # Swap corners
            swap_pieces(cp, co, corners[0], corners[1])
        else:
            # Swap edges
            swap_pieces(ep, eo, edges[0], edges[1])

    return cp, co, ep, eo


def random_orientation(
        pieces: list[int],
        piece_count: int,
        modulus: int,
        rng: Random,
) -> Orientation:
    """
    Generate random orientation maintaining sum constraint.

    Args:
        pieces: Indices of pieces to orient.
        piece_count: Total number of pieces (8 for corners, 12 for edges).
        modulus: Constraint modulus (3 for corners, 2 for edges).
        rng: Random number generator.

    Returns:
        Orientation array with sum(orient[pieces]) % modulus == 0.

    """
    orient = [0] * piece_count

    if not pieces:
        return orient

    # Randomize all but the last piece
    total = 0
    for i in range(len(pieces) - 1):
        idx = pieces[i]
        orient[idx] = rng.randint(0, modulus - 1)
        total += orient[idx]

    # Fix the last piece to maintain constraint
    last_idx = pieces[-1]
    orient[last_idx] = (-total) % modulus

    return orient


def random_corner_orientation(
        corners: list[int],
        rng: Random | None = None,
) -> Orientation:
    """
    Generate random corner orientation maintaining sum(co) % 3 == 0.

    Args:
        corners: Indices of corners to orient.
        rng: Random number generator (uses DEFAULT_RNG if None).

    Returns:
        Corner orientation array (0, 1, or 2 for each corner).

    """
    if rng is None:
        rng = DEFAULT_RNG
    return random_orientation(corners, CORNER_NUMBER, CORNER_MODULUS, rng)


def random_edge_orientation(
        edges: list[int],
        rng: Random | None = None,
) -> Orientation:
    """
    Generate random edge orientation maintaining sum(eo) % 2 == 0.

    Args:
        edges: Indices of edges to orient.
        rng: Random number generator (uses DEFAULT_RNG if None).

    Returns:
        Edge orientation array (0 or 1 for each edge).

    """
    if rng is None:
        rng = DEFAULT_RNG
    return random_orientation(edges, EDGE_NUMBER, EDGE_MODULUS, rng)


def arrange_pieces(  # noqa: PLR0913, PLR0917
        cp: Permutation,
        co: Orientation,
        ep: Permutation,
        eo: Orientation,
        corners: list[int],
        edges: list[int],
        buffer_corners: list[int] | None = None,
        buffer_edges: list[int] | None = None,
        rng: Random | None = None,
) -> CubeCubies:
    """
    Arrange specified pieces to their solved positions.

    Uses buffer pieces to maintain parity. The strategy is:
    1. Randomly permute all specified pieces + buffers
    2. Iteratively swap pieces to their correct positions
    3. Fix parity using buffer pieces if needed

    Args:
        cp: Corner permutations.
        co: Corner orientations.
        ep: Edge permutations.
        eo: Edge orientations.
        corners: Indices of corners to solve.
        edges: Indices of edges to solve.
        buffer_corners: Corners that can absorb parity fixes.
        buffer_edges: Edges that can absorb parity fixes.
        rng: Random number generator (uses DEFAULT_RNG if None).

    Returns:
        Tuple of (cp, co, ep, eo) with specified pieces solved.

    """
    if rng is None:
        rng = DEFAULT_RNG

    # Work with copies to avoid mutating inputs
    cp = cp.copy()
    co = co.copy()
    ep = ep.copy()
    eo = eo.copy()

    buffer_corners = buffer_corners or []
    buffer_edges = buffer_edges or []

    # Randomly permute specified pieces and buffers in place
    all_corners = corners + buffer_corners
    all_edges = edges + buffer_edges

    shuffle_in_place(cp, co, all_corners, rng)
    shuffle_in_place(ep, eo, all_edges, rng)

    # Ensure initial parities match
    if (
            all_corners
            and all_edges
            and compute_parity(cp) != compute_parity(ep)
    ):
        fix_parity_with_buffer(
            cp, co, ep, eo, buffer_corners, buffer_edges,
        )

    # Now solve the specified pieces
    even_swaps = True

    # Solve corners
    for idx in corners:
        if cp[idx] == idx:
            continue
        target_pos = cp.index(idx)
        swap_pieces(cp, co, idx, target_pos)
        even_swaps = not even_swaps

    # Solve edges
    for idx in edges:
        if ep[idx] == idx:
            continue
        target_pos = ep.index(idx)
        swap_pieces(ep, eo, idx, target_pos)
        even_swaps = not even_swaps

    # Fix parity if needed
    if not even_swaps:
        fix_parity_with_buffer(
            cp, co, ep, eo, buffer_corners, buffer_edges,
        )

    return cp, co, ep, eo


def derange_pieces(  # noqa: C901, PLR0912, PLR0913, PLR0917
        cp: Permutation,
        co: Orientation,
        ep: Permutation,
        eo: Orientation,
        corners: list[int],
        edges: list[int],
        buffer_corners: list[int] | None = None,
        buffer_edges: list[int] | None = None,
        rng: Random | None = None,
) -> CubeCubies:
    """
    Ensure specified pieces are NOT in solved positions (derangement).

    Uses buffer pieces to maintain parity. Strategy:
    1. Randomly permute specified pieces + buffers
    2. For any pieces that ended up solved, swap them
    3. Fix parity using buffer pieces if needed

    Args:
        cp: Corner permutations.
        co: Corner orientations.
        ep: Edge permutations.
        eo: Edge orientations.
        corners: Indices of corners to derange.
        edges: Indices of edges to derange.
        buffer_corners: Corners that can absorb parity fixes.
        buffer_edges: Edges that can absorb parity fixes.
        rng: Random number generator (uses DEFAULT_RNG if None).

    Returns:
        Tuple of (cp, co, ep, eo) with specified pieces not solved.

    """
    if rng is None:
        rng = DEFAULT_RNG

    # Work with copies to avoid mutating inputs
    cp = cp.copy()
    co = co.copy()
    ep = ep.copy()
    eo = eo.copy()

    buffer_corners = buffer_corners or []
    buffer_edges = buffer_edges or []

    # Randomly permute in place
    all_corners = corners + buffer_corners
    all_edges = edges + buffer_edges

    shuffle_in_place(cp, co, all_corners, rng)
    shuffle_in_place(ep, eo, all_edges, rng)

    even_swaps = True

    # Fix any corners that are solved
    for i, idx in enumerate(corners):
        if cp[idx] != idx:
            continue

        # Find another piece to swap with
        swapped = False
        for j in range(i + 1, len(corners)):
            other_idx = corners[j]
            # Make sure swapping doesn't solve either piece
            if cp[other_idx] != idx and cp[idx] != other_idx:
                swap_pieces(cp, co, idx, other_idx)
                even_swaps = not even_swaps
                swapped = True
                break

        # Try buffer corners if no swap found
        if not swapped:
            for other_idx in buffer_corners:
                if cp[other_idx] != idx and cp[idx] != other_idx:
                    swap_pieces(cp, co, idx, other_idx)
                    even_swaps = not even_swaps
                    break

    # Fix any edges that are solved
    for i, idx in enumerate(edges):
        if ep[idx] != idx:
            continue

        # Find another piece to swap with
        swapped = False
        for j in range(i + 1, len(edges)):
            other_idx = edges[j]
            # Make sure swapping doesn't solve either piece
            if ep[other_idx] != idx and ep[idx] != other_idx:
                swap_pieces(ep, eo, idx, other_idx)
                even_swaps = not even_swaps
                swapped = True
                break

        # Try buffer edges if no swap found
        if not swapped:
            for other_idx in buffer_edges:
                if ep[other_idx] != idx and ep[idx] != other_idx:
                    swap_pieces(ep, eo, idx, other_idx)
                    even_swaps = not even_swaps
                    break

    # Ensure final parities match
    if compute_parity(cp) != compute_parity(ep):
        fix_parity_with_buffer(
            cp, co, ep, eo, buffer_corners, buffer_edges,
        )

    return cp, co, ep, eo


def orient_pieces(
        orient: Orientation,
        pieces: list[int],
        buffer_pieces: list[int],
        modulus: int,
        rng: Random,
) -> Orientation:
    """
    Orient specified pieces to solved orientation (orient=0).

    Args:
        orient: Current orientation array (co or eo).
        pieces: Indices of pieces to orient.
        buffer_pieces: Pieces that can absorb orientation fixes.
        modulus: Constraint modulus (3 for corners, 2 for edges).
        rng: Random number generator.

    Returns:
        Orientation array with specified pieces oriented.

    """
    orient = orient.copy()

    # Orient specified pieces
    total = 0
    for idx in pieces:
        total += orient[idx]
        orient[idx] = 0

    # Fix constraint using buffer
    if total % modulus != 0:
        if buffer_pieces:
            victim = rng.choice(buffer_pieces)
            orient[victim] = (orient[victim] + total) % modulus
        elif pieces:
            # No buffer - adjust one of the specified pieces
            victim = rng.choice(pieces)
            orient[victim] = total % modulus

    return orient


def orient_corners(
        co: Orientation,
        corners: list[int],
        buffer_corners: list[int] | None = None,
        rng: Random | None = None,
) -> Orientation:
    """
    Orient specified corners to solved orientation (co=0).

    Uses buffer corners to maintain sum(co) % 3 == 0.

    Args:
        co: Current corner orientation array.
        corners: Indices of corners to orient.
        buffer_corners: Corners that can absorb orientation fixes.
        rng: Random number generator (uses DEFAULT_RNG if None).

    Returns:
        Corner orientation array with specified corners oriented.

    """
    if rng is None:
        rng = DEFAULT_RNG
    return orient_pieces(
        co, corners, buffer_corners or [], CORNER_MODULUS, rng,
    )


def disorient_corners(
        co: Orientation,
        corners: list[int],
        buffer_corners: list[int] | None = None,
        rng: Random | None = None,
) -> Orientation:
    """
    Ensure specified corners are NOT in solved orientation (co != 0).

    Uses buffer corners to maintain sum(co) % 3 == 0.

    Args:
        co: Current corner orientation array.
        corners: Indices of corners to disorient.
        buffer_corners: Corners that can absorb orientation fixes.
        rng: Random number generator (uses DEFAULT_RNG if None).

    Returns:
        Corner orientation array with specified corners disoriented.

    """
    if rng is None:
        rng = DEFAULT_RNG

    co = co.copy()
    buffer_corners = buffer_corners or []

    # Disorient specified corners
    total_twist = 0
    for idx in corners:
        if co[idx] == 0:
            # Make it non-zero (1 or 2)
            twist = rng.choice([1, 2])
            co[idx] = twist
            total_twist += twist
        else:
            total_twist += co[idx]

    # Fix constraint using buffer
    if total_twist % CORNER_MODULUS != 0:
        if buffer_corners:
            victim = rng.choice(buffer_corners)
            co[victim] = (co[victim] - total_twist) % CORNER_MODULUS
        elif corners:
            # No buffer - try to adjust without solving
            victim = rng.choice(corners)
            needed = (-total_twist) % CORNER_MODULUS
            if needed != 0:
                co[victim] = needed
            else:
                # Can't fix without solving a corner
                # Find another corner to adjust
                for idx in corners:
                    if idx != victim:
                        co[idx] = (co[idx] + 1) % CORNER_MODULUS
                        co[victim] = (co[victim] + 2) % CORNER_MODULUS
                        break

    return co


def orient_edges(
        eo: Orientation,
        edges: list[int],
        buffer_edges: list[int] | None = None,
        rng: Random | None = None,
) -> Orientation:
    """
    Orient specified edges to solved orientation (eo=0).

    Uses buffer edges to maintain sum(eo) % 2 == 0.

    Args:
        eo: Current edge orientation array.
        edges: Indices of edges to orient.
        buffer_edges: Edges that can absorb orientation fixes.
        rng: Random number generator (uses DEFAULT_RNG if None).

    Returns:
        Edge orientation array with specified edges oriented.

    """
    if rng is None:
        rng = DEFAULT_RNG
    return orient_pieces(eo, edges, buffer_edges or [], EDGE_MODULUS, rng)


def disorient_edges(
        eo: Orientation,
        edges: list[int],
        buffer_edges: list[int] | None = None,
        rng: Random | None = None,
) -> Orientation:
    """
    Ensure specified edges are NOT in solved orientation (eo != 0).

    Uses buffer edges to maintain sum(eo) % 2 == 0.

    Args:
        eo: Current edge orientation array.
        edges: Indices of edges to disorient.
        buffer_edges: Edges that can absorb orientation fixes.
        rng: Random number generator (uses DEFAULT_RNG if None).

    Returns:
        Edge orientation array with specified edges disoriented.

    """
    if rng is None:
        rng = DEFAULT_RNG

    eo = eo.copy()
    buffer_edges = buffer_edges or []

    # Disorient specified edges
    total_flips = 0
    for idx in edges:
        if eo[idx] == 0:
            eo[idx] = 1
            total_flips += 1
        else:
            total_flips += eo[idx]

    # Fix constraint using buffer
    if total_flips % EDGE_MODULUS != 0:
        if buffer_edges:
            victim = rng.choice(buffer_edges)
            eo[victim] = (eo[victim] + 1) % EDGE_MODULUS
        elif edges:
            # No buffer - unflip one edge
            victim = rng.choice(edges)
            eo[victim] = 0

    return eo
