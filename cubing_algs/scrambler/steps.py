"""
Step-based scramble generation for speedcubing methods.

This module provides high-level functions to generate scrambles for specific
speedcubing steps (e.g., PLL, OLL, F2L) by manipulating cube state and using
a solver to generate the scramble algorithm.
"""
from random import Random

from cubing_algs.algorithm import Algorithm
from cubing_algs.exceptions import InvalidStepError
from cubing_algs.parsing import parse_moves
from cubing_algs.scrambler.pieces import arrange_pieces
from cubing_algs.scrambler.pieces import derange_pieces
from cubing_algs.scrambler.pieces import disorient_corners
from cubing_algs.scrambler.pieces import disorient_edges
from cubing_algs.scrambler.pieces import orient_corners
from cubing_algs.scrambler.pieces import orient_edges
from cubing_algs.scrambler.pieces import random_corner_orientation
from cubing_algs.scrambler.pieces import random_edge_orientation
from cubing_algs.scrambler.pieces import random_permutation
from cubing_algs.scrambler.random import DEFAULT_RNG
from cubing_algs.scrambler.utils import ALL_CORNERS
from cubing_algs.scrambler.utils import U_CORNERS
from cubing_algs.scrambler.utils import U_EDGES
from cubing_algs.scrambler.utils import parse_piece_spec
from cubing_algs.scrambler.utils import solve_to_algorithm
from cubing_algs.scrambler.utils import vcube_to_kociemba_string
from cubing_algs.transform.mirror import mirror_moves
from cubing_algs.vcube import VCube

# Solved center orientation array
SOLVED_CENTERS: list[int] = [0, 1, 2, 3, 4, 5]

# AUF choices for random U layer adjustment
AUF_CHOICES: list[str] = ['', 'U', 'U2', "U'"]

# Type alias for cube state tuple
CubeState = tuple[list[int], list[int], list[int], list[int]]


def _apply_auf(
        cp: list[int],
        co: list[int],
        ep: list[int],
        eo: list[int],
        rng: Random,
) -> CubeState:
    """
    Apply random AUF (Adjustment of U Face) to cube state.

    Args:
        cp: Corner permutations.
        co: Corner orientations.
        ep: Edge permutations.
        eo: Edge orientations.
        rng: Random number generator.

    Returns:
        Tuple of (cp, co, ep, eo) with AUF applied.

    """
    auf_move = rng.choice(AUF_CHOICES)
    if auf_move:
        temp_cube = VCube.from_cubies(cp, co, ep, eo, SOLVED_CENTERS)
        temp_cube.rotate(auf_move)
        cp, co, ep, eo, _ = temp_cube.to_cubies
    return cp, co, ep, eo


def _apply_moves(
        cp: list[int],
        co: list[int],
        ep: list[int],
        eo: list[int],
        moves: str,
) -> CubeState:
    """
    Apply move sequence to cube state.

    Args:
        cp: Corner permutations.
        co: Corner orientations.
        ep: Edge permutations.
        eo: Edge orientations.
        moves: Move sequence string (e.g., "R U R'").

    Returns:
        Tuple of (cp, co, ep, eo) with moves applied.

    """
    temp_cube = VCube.from_cubies(cp, co, ep, eo, SOLVED_CENTERS)
    temp_cube.rotate(moves)
    cp, co, ep, eo, _ = temp_cube.to_cubies
    return cp, co, ep, eo


def _state_to_scramble(
        cp: list[int],
        co: list[int],
        ep: list[int],
        eo: list[int],
) -> Algorithm:
    """
    Convert cube state to scramble algorithm using Kociemba solver.

    Args:
        cp: Corner permutations.
        co: Corner orientations.
        ep: Edge permutations.
        eo: Edge orientations.

    Returns:
        Algorithm that produces this state from solved.

    """
    cube = VCube.from_cubies(cp, co, ep, eo, SOLVED_CENTERS)
    kociemba_state = vcube_to_kociemba_string(cube)
    solution = solve_to_algorithm(kociemba_state)

    if not solution or not solution.strip():
        return parse_moves('')

    return mirror_moves(parse_moves(solution))


# Supported step types
SUPPORTED_STEPS = [
    # Last Layer steps
    'LL', 'OLL', 'PLL', 'CLL', 'OLLCP', 'COLL', 'ZBLL', '2GLL',
    'OCLL', 'ELL', 'EPLL', 'CPLL', 'ZZLL',
    # F2L variants
    'F2L', 'ZZF2L', 'ZZRB', 'PetrusF2L',
    # Last Slot variants
    'LS', 'ELS', 'ZZLS', 'TSLE', 'CLS', 'CPLS', 'EJLS', 'EJF2L',
    'TTLL', 'WV', 'SV', 'VLS', 'VHLS',
    # Roux method
    'CMLL', 'CMLLEO', 'SB',
    # Petrus method
    'Petrus2x2x3', 'PetrusEO',
]


def _generate_step_state(  # noqa: C901, PLR0912, PLR0914, PLR0915
        step: str,
        rng: Random | None = None,
) -> tuple[list[int], list[int], list[int], list[int]]:
    """
    Generate cube state for a specific speedcubing step.

    This function implements the logic for each step type, manipulating
    the cubie arrays (cp, co, ep, eo) to create the desired partial-solve state.

    Args:
        step: Step name (must be in SUPPORTED_STEPS).
        rng: Random number generator (uses DEFAULT_RNG if None).

    Returns:
        Tuple of (cp, co, ep, eo) representing the cube state.

    Raises:
        InvalidStepError: If step is not recognized.

    """
    if rng is None:
        rng = DEFAULT_RNG

    step = step.upper()

    # Initialize with solved state
    cp = list(range(8))
    co = [0] * 8
    ep = list(range(12))
    eo = [0] * 12

    # Last Layer (LL) - permute and orient U layer
    if step in {'LL', 'OLL', 'CLL', 'OLLCP'}:
        cp, co, ep, eo = random_permutation(U_CORNERS, U_EDGES, rng)
        co = random_corner_orientation(U_CORNERS, rng)
        eo = random_edge_orientation(U_EDGES, rng)

    # PLL - only permutation on U layer
    elif step == 'PLL':
        cp, co, ep, eo = random_permutation(U_CORNERS, U_EDGES, rng)

    # OCLL, COLL, ZBLL - corners oriented, all permuted
    elif step in {'OCLL', 'COLL', 'ZBLL'}:
        cp, co, ep, eo = random_permutation(U_CORNERS, U_EDGES, rng)
        co = random_corner_orientation(U_CORNERS, rng)

    # 2GLL - specific pattern with phase edges
    elif step == '2GLL':
        cp, co, ep, eo = _apply_auf(cp, co, ep, eo, rng)

        # Permute phase edges only (no corners)
        phase_edges = [1, 3]  # UF, UB
        cp, co, ep, eo = random_permutation([], phase_edges, rng)
        co = random_corner_orientation(U_CORNERS, rng)

    # ELL - edge orientation and permutation on U layer
    elif step == 'ELL':
        cp, co, ep, eo = random_permutation([], U_EDGES, rng)
        eo = random_edge_orientation(U_EDGES, rng)

    # EPLL - only edge permutation on U layer
    elif step == 'EPLL':
        cp, co, ep, eo = random_permutation([], U_EDGES, rng)

    # CPLL - only corner permutation on U layer
    elif step == 'CPLL':
        cp, co, ep, eo = random_permutation(U_CORNERS, [], rng)

    # CMLL, CMLLEO - Roux method steps
    elif step in {'CMLL', 'CMLLEO'}:
        cmll_edges = parse_piece_spec('U DF DB', 'edge')
        cp, co, ep, eo = random_permutation(U_CORNERS, cmll_edges, rng)
        co = random_corner_orientation(U_CORNERS, rng)
        eo = random_edge_orientation(cmll_edges, rng)

    # ZZLL - ZZ method last layer
    elif step == 'ZZLL':
        phase_edges = [1, 3]  # UF, UB
        cp, co, ep, eo = random_permutation(U_CORNERS, phase_edges, rng)
        co = random_corner_orientation(U_CORNERS, rng)
        cp, co, ep, eo = _apply_auf(cp, co, ep, eo, rng)

    # F2L - First Two Layers
    elif step == 'F2L':
        f2l_edges = parse_piece_spec('U FR FL BR BL', 'edge')
        cp, co, ep, eo = random_permutation(ALL_CORNERS, f2l_edges, rng)
        co = random_corner_orientation(ALL_CORNERS, rng)
        eo = random_edge_orientation(f2l_edges, rng)

    # ZZF2L - ZZ method F2L
    elif step == 'ZZF2L':
        zzf2l_edges = parse_piece_spec('R U L', 'edge')
        cp, co, ep, eo = random_permutation(ALL_CORNERS, zzf2l_edges, rng)
        co = random_corner_orientation(ALL_CORNERS, rng)

    # ZZRB, PetrusF2L - right block steps
    elif step in {'ZZRB', 'PETRUSF2L'}:
        ru_corners = parse_piece_spec('R U', 'corner')
        ru_edges = parse_piece_spec('R U', 'edge')
        cp, co, ep, eo = random_permutation(ru_corners, ru_edges, rng)
        co = random_corner_orientation(ru_corners, rng)

    # SB - Roux Second Block
    elif step == 'SB':
        sb_corners = parse_piece_spec('R U', 'corner')
        sb_edges = parse_piece_spec('R U DF DB', 'edge')
        cp, co, ep, eo = random_permutation(sb_corners, sb_edges, rng)
        co = random_corner_orientation(sb_corners, rng)
        eo = random_edge_orientation(sb_edges, rng)

    # Last Slot (LS) steps
    elif step in {'LS', 'ELS'}:
        ls_corners = parse_piece_spec('U DFR', 'corner')
        ls_edges = parse_piece_spec('U FR', 'edge')
        cp, co, ep, eo = random_permutation(ls_corners, ls_edges, rng)
        co = random_corner_orientation(ls_corners, rng)
        eo = random_edge_orientation(ls_edges, rng)

    # ZZLS, TSLE - ZZ last slot
    elif step in {'ZZLS', 'TSLE'}:
        ls_corners = parse_piece_spec('U DFR', 'corner')
        ls_edges = parse_piece_spec('U FR', 'edge')
        cp, co, ep, eo = random_permutation(ls_corners, ls_edges, rng)
        co = random_corner_orientation(ls_corners, rng)

    # CLS, CPLS - Corner + Last Slot
    elif step in {'CLS', 'CPLS'}:
        cls_corners = parse_piece_spec('U DFR', 'corner')
        cp, co, ep, eo = random_permutation(cls_corners, U_EDGES, rng)
        co = random_corner_orientation(cls_corners, rng)

    # EJLS, EJF2L - Edge Just Last Slot
    elif step in {'EJLS', 'EJF2L'}:
        cp, co, ep, eo = random_permutation(U_CORNERS, U_EDGES, rng)
        # Randomize all U corners orientation
        co = random_corner_orientation(U_CORNERS, rng)
        # Ensure DFR (index 4) is disoriented
        if co[4] == 0:
            # Make it non-zero
            co[4] = rng.choice([1, 2])
            # Fix constraint using a U corner
            victim = rng.choice(U_CORNERS)
            co[victim] = (co[victim] - co[4]) % 3

    # TTLL - Two-Twist Last Layer
    elif step == 'TTLL':
        ttll_corners = parse_piece_spec('U DFR', 'corner')
        cp, co, ep, eo = random_permutation(ttll_corners, U_EDGES, rng)

    # WV - Winter Variation
    elif step == 'WV':
        cp, co, ep, eo = random_permutation(U_CORNERS, U_EDGES, rng)
        co = random_corner_orientation(U_CORNERS, rng)
        cp, co, ep, eo = _apply_moves(cp, co, ep, eo, "R U R'")

    # SV - Summer Variation
    elif step == 'SV':
        cp, co, ep, eo = random_permutation(U_CORNERS, U_EDGES, rng)
        co = random_corner_orientation(U_CORNERS, rng)
        cp, co, ep, eo = _apply_moves(cp, co, ep, eo, "R U' R'")

    # VLS, VHLS - Valk Last Slot
    elif step in {'VLS', 'VHLS'}:
        cp, co, ep, eo = random_permutation(U_CORNERS, U_EDGES, rng)
        co = random_corner_orientation(U_CORNERS, rng)
        eo = random_edge_orientation(U_EDGES, rng)
        cp, co, ep, eo = _apply_moves(cp, co, ep, eo, "R U' R'")

    # Petrus2x2x3
    elif step == 'PETRUS2X2X3':
        petrus_corners = parse_piece_spec('U R F', 'corner')
        petrus_edges = parse_piece_spec('U R F', 'edge')
        cp, co, ep, eo = random_permutation(petrus_corners, petrus_edges, rng)
        co = random_corner_orientation(petrus_corners, rng)
        eo = random_edge_orientation(petrus_edges, rng)

    # PetrusEO - Petrus Edge Orientation
    elif step == 'PETRUSEO':
        petrus_corners = parse_piece_spec('U F', 'corner')
        petrus_edges = parse_piece_spec('U F', 'edge')
        cp, co, ep, eo = random_permutation(petrus_corners, petrus_edges, rng)
        co = random_corner_orientation(petrus_corners, rng)
        eo = random_edge_orientation(petrus_edges, rng)

    else:
        msg = (
            f"Step '{step}' not recognized. "
            f"Supported steps: {', '.join(SUPPORTED_STEPS)}"
        )
        raise InvalidStepError(msg)

    return cp, co, ep, eo


def scramble_step(
        step: str,
        rng: Random | None = None,
        *, include_auf: bool = True,
) -> Algorithm:
    """
    Generate a scramble for a specific speedcubing step.

    Creates a cube state where only the specified step remains unsolved,
    then generates a solving algorithm (inverted for scramble).

    Args:
        step: Step name (e.g., "PLL", "OLL", "ZBLL").
        rng: Random number generator (uses DEFAULT_RNG if None).
        include_auf: Whether to include random AUF (U layer adjustment).

    Returns:
        Algorithm scramble for the specified step.

    Example:
        >>> scramble = scramble_step("PLL")
        >>> print(scramble)
        # Scramble with only U layer permuted

    """
    if rng is None:
        rng = DEFAULT_RNG

    # Generate the step state
    cp, co, ep, eo = _generate_step_state(step, rng)

    # Apply random AUF if requested
    skip_auf_steps = {'WV', 'SV', 'VLS', 'VHLS', '2GLL', 'ZZLL'}
    if include_auf and step.upper() not in skip_auf_steps:
        cp, co, ep, eo = _apply_auf(cp, co, ep, eo, rng)

    return _state_to_scramble(cp, co, ep, eo)


def scramble_ocll_case(
        case: str,
        rng: Random | None = None,
) -> Algorithm:
    """
    Generate scramble for specific OCLL case pattern.

    Args:
        case: Case name - "T", "U", "L", "H", "Pi", "Sune",
            "AntiSune", or "Solved".
        rng: Random number generator (uses DEFAULT_RNG if None).

    Returns:
        Algorithm scramble for the specified OCLL case.

    Raises:
        InvalidStepError: If case is not recognized.

    """
    if rng is None:
        rng = DEFAULT_RNG

    case = case.upper()

    # Start with solved state and permute U layer
    cp, co, ep, eo = random_permutation(U_CORNERS, U_EDGES, rng)

    # Orient U corners first
    co = orient_corners(co, U_CORNERS, [], rng)

    # Apply specific corner twists
    # U corner indices: URF=0, UFL=1, ULB=2, UBR=3
    if case == 'T':
        co[2] = 1  # ULB clockwise 1
        co[3] = 2  # UBR clockwise 2

    elif case == 'U':
        co[2] = 2  # ULB clockwise 2
        co[3] = 1  # UBR clockwise 1

    elif case == 'L':
        co[2] = 2  # ULB clockwise 2
        co[0] = 1  # URF clockwise 1

    elif case == 'H':
        co[2] = 1  # ULB clockwise 1
        co[3] = 2  # UBR clockwise 2
        co[0] = 1  # URF clockwise 1
        co[1] = 2  # UFL clockwise 2

    elif case in {'PI', 'BRUNO'}:
        co[2] = 1  # ULB clockwise 1
        co[1] = 2  # UFL clockwise 2
        co[3] = 1  # UBR clockwise 1
        co[0] = 2  # URF clockwise 2

    elif case in {'S', 'SUNE'}:
        co[0] = 2  # URF clockwise 2
        co[3] = 2  # UBR clockwise 2
        co[2] = 2  # ULB clockwise 2

    elif case in {'AS', 'ANTISUNE', 'ANTI-SUNE'}:
        co[0] = 1  # URF clockwise 1
        co[1] = 1  # UFL clockwise 1
        co[2] = 1  # ULB clockwise 1

    elif case in {'0', 'O', 'SOLVED'}:
        # All corners already oriented
        pass

    else:
        msg = (
            f"OCLL case '{case}' not recognized. "
            "Valid cases: T, U, L, H, Pi, Sune, AntiSune, Solved"
        )
        raise InvalidStepError(msg)

    # Random AUF
    cp, co, ep, eo = _apply_auf(cp, co, ep, eo, rng)

    return _state_to_scramble(cp, co, ep, eo)


def scramble_with_piece_constraints(  # noqa: PLR0913, PLR0914, PLR0917
        solve_corners: str = '',
        solve_edges: str = '',
        orient_corners_spec: str = '',
        orient_edges_spec: str = '',
        derange_corners: str = '',
        derange_edges: str = '',
        disorient_corners_spec: str = '',
        disorient_edges_spec: str = '',
        buffer_corners: str = 'D',
        buffer_edges: str = 'E',
        rng: Random | None = None,
) -> Algorithm:
    """
    Generate scramble with fine-grained piece-level constraints.

    This function provides maximum control over cube state by allowing you to
    specify exactly which pieces should be solved, oriented, or scrambled.

    Args:
        solve_corners: Corners to place in solved positions
            (e.g., "U", "URF UBR").
        solve_edges: Edges to place in solved positions
            (e.g., "U", "UR UF").
        orient_corners_spec: Corners to orient correctly
            (e.g., "all", "U").
        orient_edges_spec: Edges to orient correctly (e.g., "all", "D").
        derange_corners: Corners that must NOT be in solved positions.
        derange_edges: Edges that must NOT be in solved positions.
        disorient_corners_spec: Corners that must NOT be correctly
            oriented.
        disorient_edges_spec: Edges that must NOT be correctly oriented.
        buffer_corners: Corners to use as buffers for fixing constraints
            (default "D").
        buffer_edges: Edges to use as buffers for fixing constraints
            (default "E").
        rng: Random number generator (uses DEFAULT_RNG if None).

    Returns:
        Algorithm scramble satisfying the specified constraints.

    Examples:
        >>> # PLL-like state: U layer permuted, all pieces oriented
        >>> scramble_with_piece_constraints(
        ...     orient_corners_spec="all",
        ...     orient_edges_spec="all",
        ...     buffer_corners="D",
        ...     buffer_edges="E"
        ... )

        >>> # F2L solved, last layer scrambled
        >>> scramble_with_piece_constraints(
        ...     solve_corners="D",
        ...     solve_edges="D E",
        ...     buffer_corners="U",
        ...     buffer_edges="U"
        ... )

        >>> # ZBLL-like: Last layer oriented
        >>> scramble_with_piece_constraints(
        ...     orient_corners_spec="U",
        ...     orient_edges_spec="U",
        ...     buffer_corners="D",
        ...     buffer_edges="E"
        ... )

    """
    if rng is None:
        rng = DEFAULT_RNG

    # Start with solved state
    cp = list(range(8))
    co = [0] * 8
    ep = list(range(12))
    eo = [0] * 12

    # Parse piece specifications
    solve_corners_list = (
        parse_piece_spec(solve_corners, 'corner') if solve_corners else []
    )
    solve_edges_list = (
        parse_piece_spec(solve_edges, 'edge') if solve_edges else []
    )
    derange_corners_list = (
        parse_piece_spec(derange_corners, 'corner') if derange_corners else []
    )
    derange_edges_list = (
        parse_piece_spec(derange_edges, 'edge') if derange_edges else []
    )
    buffer_corners_list = parse_piece_spec(buffer_corners, 'corner')
    buffer_edges_list = parse_piece_spec(buffer_edges, 'edge')

    # Step 1: Handle position constraints (solve/derange)
    # First, scramble everything that's not explicitly solved
    all_corners_set = set(range(8))
    all_edges_set = set(range(12))

    # Pieces to scramble = all pieces - (solve pieces + buffer pieces)
    scramble_corners = list(
        all_corners_set - set(solve_corners_list) - set(buffer_corners_list),
    )
    scramble_edges = list(
        all_edges_set - set(solve_edges_list) - set(buffer_edges_list),
    )

    # Scramble non-solved pieces
    if scramble_corners or scramble_edges:
        cp, co, ep, eo = derange_pieces(
            cp, co, ep, eo,
            scramble_corners or [],
            scramble_edges or [],
            buffer_corners_list,
            buffer_edges_list,
            rng,
        )

    # Arrange solved pieces
    if solve_corners_list or solve_edges_list:
        cp, co, ep, eo = arrange_pieces(
            cp, co, ep, eo,
            solve_corners_list,
            solve_edges_list,
            buffer_corners_list,
            buffer_edges_list,
            rng,
        )

    # Handle derange constraint (make sure these are NOT solved)
    if derange_corners_list or derange_edges_list:
        cp, co, ep, eo = derange_pieces(
            cp, co, ep, eo,
            derange_corners_list,
            derange_edges_list,
            buffer_corners_list,
            buffer_edges_list,
            rng,
        )

    # Step 2: Handle orientation constraints
    if orient_corners_spec:
        orient_corners_list = parse_piece_spec(orient_corners_spec, 'corner')
        co = orient_corners(co, orient_corners_list, buffer_corners_list, rng)

    if orient_edges_spec:
        orient_edges_list = parse_piece_spec(orient_edges_spec, 'edge')
        eo = orient_edges(eo, orient_edges_list, buffer_edges_list, rng)

    if disorient_corners_spec:
        disorient_corners_list = parse_piece_spec(
            disorient_corners_spec, 'corner',
        )
        co = disorient_corners(
            co, disorient_corners_list, buffer_corners_list, rng,
        )

    if disorient_edges_spec:
        disorient_edges_list = parse_piece_spec(
            disorient_edges_spec, 'edge',
        )
        eo = disorient_edges(
            eo, disorient_edges_list, buffer_edges_list, rng,
        )

    return _state_to_scramble(cp, co, ep, eo)
