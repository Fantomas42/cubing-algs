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

from cubing_algs.scrambler.random import DEFAULT_RNG


def _shuffle_in_place(
        perm: list[int],
        orient: list[int],
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
            idx_i = indices[i]
            idx_j = indices[j]
            perm[idx_i], perm[idx_j] = perm[idx_j], perm[idx_i]
            orient[idx_i], orient[idx_j] = orient[idx_j], orient[idx_i]
            even_swaps = not even_swaps
    return even_swaps


def _fix_parity_with_buffer(  # noqa: PLR0913, PLR0917
        cp: list[int],
        co: list[int],
        ep: list[int],
        eo: list[int],
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
        idx_1, idx_2 = buffer_edges[0], buffer_edges[1]
        ep[idx_1], ep[idx_2] = ep[idx_2], ep[idx_1]
        eo[idx_1], eo[idx_2] = eo[idx_2], eo[idx_1]
    elif len(buffer_corners) >= 2:
        idx_1, idx_2 = buffer_corners[0], buffer_corners[1]
        cp[idx_1], cp[idx_2] = cp[idx_2], cp[idx_1]
        co[idx_1], co[idx_2] = co[idx_2], co[idx_1]


def _calculate_parity(permutation: list[int]) -> int:
    """
    Calculate the parity of a permutation.

    Parity is 0 for even permutations (even number of swaps) and
    1 for odd permutations (odd number of swaps).

    Args:
        permutation: Permutation array.

    Returns:
        0 for even parity, 1 for odd parity.

    """
    n = len(permutation)
    visited = [False] * n
    parity = 0

    for i in range(n):
        if visited[i] or permutation[i] == i:
            continue

        # Count cycle length
        cycle_len = 0
        j = i
        while not visited[j]:
            visited[j] = True
            j = permutation[j]
            cycle_len += 1

        # Cycle of length k contributes (k-1) swaps
        parity ^= (cycle_len - 1) % 2

    return parity


def random_permutation(
        corners: list[int],
        edges: list[int],
        rng: Random | None = None,
) -> tuple[list[int], list[int], list[int], list[int]]:
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

    cp = list(range(8))
    co = [0] * 8
    ep = list(range(12))
    eo = [0] * 12

    even_num_swaps = True

    # Fischer-Yates shuffle corners
    for i in range(len(corners) - 1):
        j = rng.randint(i, len(corners) - 1)
        if i != j:
            idx_i = corners[i]
            idx_j = corners[j]
            cp[idx_i], cp[idx_j] = cp[idx_j], cp[idx_i]
            even_num_swaps = not even_num_swaps

    # Fischer-Yates shuffle edges
    for i in range(len(edges) - 1):
        j = rng.randint(i, len(edges) - 1)
        if i != j:
            idx_i = edges[i]
            idx_j = edges[j]
            ep[idx_i], ep[idx_j] = ep[idx_j], ep[idx_i]
            even_num_swaps = not even_num_swaps

    # Fix parity if needed by swapping within permuted pieces
    if not even_num_swaps:
        if len(corners) == 0:
            # No corners - must swap edges
            ep[edges[0]], ep[edges[1]] = ep[edges[1]], ep[edges[0]]
        elif len(edges) == 0 or rng.random() < 0.5:  # noqa: PLR2004
            # Swap corners
            cp[corners[0]], cp[corners[1]] = cp[corners[1]], cp[corners[0]]
        else:
            # Swap edges
            ep[edges[0]], ep[edges[1]] = ep[edges[1]], ep[edges[0]]

    return cp, co, ep, eo


def random_corner_orientation(
        corners: list[int],
        rng: Random | None = None,
) -> list[int]:
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

    co = [0] * 8

    if not corners:
        return co

    # Randomize all but the last corner
    total = 0
    for i in range(len(corners) - 1):
        idx = corners[i]
        co[idx] = rng.randint(0, 2)
        total += co[idx]

    # Fix the last corner to maintain constraint
    last_idx = corners[-1]
    co[last_idx] = (-total) % 3

    return co


def random_edge_orientation(
        edges: list[int],
        rng: Random | None = None,
) -> list[int]:
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

    eo = [0] * 12

    if not edges:
        return eo

    # Randomize all but the last edge
    total = 0
    for i in range(len(edges) - 1):
        idx = edges[i]
        eo[idx] = rng.randint(0, 1)
        total += eo[idx]

    # Fix the last edge to maintain constraint
    last_idx = edges[-1]
    eo[last_idx] = total % 2

    return eo


def flip_n_edges(
        edges: list[int],
        n: int,
        rng: Random | None = None,
) -> list[int]:
    """
    Flip exactly n edges (n must be even).

    Args:
        edges: Indices of edges that can be flipped.
        n: Number of edges to flip (must be even).
        rng: Random number generator (uses DEFAULT_RNG if None).

    Returns:
        Edge orientation array with exactly n edges flipped.

    Raises:
        ValueError: If n is odd or n > len(edges).

    """
    if n % 2 != 0:
        msg = f'Cannot flip an odd number of edges (n={n})'
        raise ValueError(msg)

    if n > len(edges):
        msg = f'Cannot flip {n} edges, only {len(edges)} edges available'
        raise ValueError(msg)

    if rng is None:
        rng = DEFAULT_RNG

    eo = [0] * 12

    # Randomly select n edges to flip
    edges_to_flip = rng.sample(edges, n)
    for idx in edges_to_flip:
        eo[idx] = 1

    return eo


def arrange_pieces(  # noqa: PLR0913, PLR0917
        cp: list[int],
        co: list[int],
        ep: list[int],
        eo: list[int],
        corners: list[int],
        edges: list[int],
        buffer_corners: list[int] | None = None,
        buffer_edges: list[int] | None = None,
        rng: Random | None = None,
) -> tuple[list[int], list[int], list[int], list[int]]:
    """
    Arrange specified pieces to their solved positions.

    Uses buffer pieces to maintain parity. The strategy is:
    1. Randomly permute all specified pieces + buffers
    2. Iteratively swap pieces to their correct positions
    3. Fix parity using buffer pieces if needed

    Args:
        cp: Corner permutations.
        co: Corner orientations.
        ep: Edge permutions.
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

    # Work with copies
    cp = cp.copy()
    co = co.copy()
    ep = ep.copy()
    eo = eo.copy()

    buffer_corners = buffer_corners or []
    buffer_edges = buffer_edges or []

    # Randomly permute specified pieces and buffers IN PLACE
    all_corners = corners + buffer_corners
    all_edges = edges + buffer_edges

    _shuffle_in_place(cp, co, all_corners, rng)
    _shuffle_in_place(ep, eo, all_edges, rng)

    # Ensure initial parities match
    if (
            all_corners
            and all_edges
            and _calculate_parity(cp) != _calculate_parity(ep)
    ):
        _fix_parity_with_buffer(
            cp, co, ep, eo, buffer_corners, buffer_edges,
        )

    # Now solve the specified pieces
    even_swaps = True

    # Solve corners
    for idx in corners:
        if cp[idx] == idx:
            continue

        # Find where the correct piece is
        target_pos = cp.index(idx)

        # Swap it into place
        cp[idx], cp[target_pos] = cp[target_pos], cp[idx]
        co[idx], co[target_pos] = co[target_pos], co[idx]
        even_swaps = not even_swaps

    # Solve edges
    for idx in edges:
        if ep[idx] == idx:
            continue

        # Find where the correct piece is
        target_pos = ep.index(idx)

        # Swap it into place
        ep[idx], ep[target_pos] = ep[target_pos], ep[idx]
        eo[idx], eo[target_pos] = eo[target_pos], eo[idx]
        even_swaps = not even_swaps

    # Fix parity if needed
    if not even_swaps:
        _fix_parity_with_buffer(
            cp, co, ep, eo, buffer_corners, buffer_edges,
        )

    return cp, co, ep, eo


def derange_pieces(  # noqa: C901, PLR0912, PLR0913, PLR0917
        cp: list[int],
        co: list[int],
        ep: list[int],
        eo: list[int],
        corners: list[int],
        edges: list[int],
        buffer_corners: list[int] | None = None,
        buffer_edges: list[int] | None = None,
        rng: Random | None = None,
) -> tuple[list[int], list[int], list[int], list[int]]:
    """
    Ensure specified pieces are NOT in solved positions (derangement).

    Uses buffer pieces to maintain parity. Strategy:
    1. Randomly permute specified pieces + buffers
    2. For any pieces that ended up solved, swap them
    3. Fix parity using buffer pieces if needed

    Args:
        cp: Corner permutations.
        co: Corner orientations.
        ep: Edge permutions.
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

    # Work with copies
    cp = cp.copy()
    co = co.copy()
    ep = ep.copy()
    eo = eo.copy()

    buffer_corners = buffer_corners or []
    buffer_edges = buffer_edges or []

    # Randomly permute IN PLACE
    all_corners = corners + buffer_corners
    all_edges = edges + buffer_edges

    _shuffle_in_place(cp, co, all_corners, rng)
    _shuffle_in_place(ep, eo, all_edges, rng)

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
                cp[idx], cp[other_idx] = cp[other_idx], cp[idx]
                co[idx], co[other_idx] = co[other_idx], co[idx]
                even_swaps = not even_swaps
                swapped = True
                break

        # Try buffer corners if no swap found
        if not swapped:
            for other_idx in buffer_corners:
                if cp[other_idx] != idx and cp[idx] != other_idx:
                    cp[idx], cp[other_idx] = cp[other_idx], cp[idx]
                    co[idx], co[other_idx] = co[other_idx], co[idx]
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
                ep[idx], ep[other_idx] = ep[other_idx], ep[idx]
                eo[idx], eo[other_idx] = eo[other_idx], eo[idx]
                even_swaps = not even_swaps
                swapped = True
                break

        # Try buffer edges if no swap found
        if not swapped:
            for other_idx in buffer_edges:
                if ep[other_idx] != idx and ep[idx] != other_idx:
                    ep[idx], ep[other_idx] = ep[other_idx], ep[idx]
                    eo[idx], eo[other_idx] = eo[other_idx], eo[idx]
                    even_swaps = not even_swaps
                    break

    # Ensure final parities match
    if _calculate_parity(cp) != _calculate_parity(ep):
        _fix_parity_with_buffer(
            cp, co, ep, eo, buffer_corners, buffer_edges,
        )

    return cp, co, ep, eo


def orient_corners(
        co: list[int],
        corners: list[int],
        buffer_corners: list[int] | None = None,
        rng: Random | None = None,
) -> list[int]:
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

    co = co.copy()
    buffer_corners = buffer_corners or []

    # Orient specified corners
    total_twist = 0
    for idx in corners:
        total_twist += co[idx]
        co[idx] = 0

    # Fix constraint using buffer
    if total_twist % 3 != 0:
        if buffer_corners:
            victim = rng.choice(buffer_corners)
            co[victim] = (co[victim] + total_twist) % 3
        elif corners:
            # No buffer - adjust one of the specified corners
            victim = rng.choice(corners)
            co[victim] = total_twist % 3

    return co


def disorient_corners(
        co: list[int],
        corners: list[int],
        buffer_corners: list[int] | None = None,
        rng: Random | None = None,
) -> list[int]:
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
    if total_twist % 3 != 0:
        if buffer_corners:
            victim = rng.choice(buffer_corners)
            co[victim] = (co[victim] - total_twist) % 3
        elif corners:
            # No buffer - try to adjust without solving
            victim = rng.choice(corners)
            needed = (-total_twist) % 3
            if needed != 0:
                co[victim] = needed
            else:
                # Can't fix without solving a corner
                # Find another corner to adjust
                for idx in corners:
                    if idx != victim:
                        co[idx] = (co[idx] + 1) % 3
                        co[victim] = (co[victim] + 2) % 3
                        break

    return co


def orient_edges(
        eo: list[int],
        edges: list[int],
        buffer_edges: list[int] | None = None,
        rng: Random | None = None,
) -> list[int]:
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

    eo = eo.copy()
    buffer_edges = buffer_edges or []

    # Orient specified edges
    total_flips = 0
    for idx in edges:
        total_flips += eo[idx]
        eo[idx] = 0

    # Fix constraint using buffer
    if total_flips % 2 != 0:
        if buffer_edges:
            victim = rng.choice(buffer_edges)
            eo[victim] = (eo[victim] + 1) % 2
        elif edges:
            # No buffer - adjust one of the specified edges
            victim = rng.choice(edges)
            eo[victim] = 1

    return eo


def disorient_edges(
        eo: list[int],
        edges: list[int],
        buffer_edges: list[int] | None = None,
        rng: Random | None = None,
) -> list[int]:
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
    if total_flips % 2 != 0:
        if buffer_edges:
            victim = rng.choice(buffer_edges)
            eo[victim] = (eo[victim] + 1) % 2
        elif edges:
            # No buffer - unflip one edge
            victim = rng.choice(edges)
            eo[victim] = 0

    return eo
