"""
Step-based scramble generation for speedcubing methods.

This module provides high-level functions to generate scrambles for specific
speedcubing steps (e.g., PLL, OLL, F2L) by manipulating cube state and using
a solver to generate the scramble algorithm.
"""
from random import Random
from typing import Final

from cubing_algs.algorithm import Algorithm
from cubing_algs.annotations import CubeCubies
from cubing_algs.constants import F2L_EDGE_CORNERS
from cubing_algs.constants import SOLVED_CO
from cubing_algs.constants import SOLVED_CP
from cubing_algs.constants import SOLVED_EO
from cubing_algs.constants import SOLVED_EP
from cubing_algs.constants import SOLVED_SO
from cubing_algs.constants import U_CORNERS
from cubing_algs.constants import U_EDGES
from cubing_algs.exceptions import InvalidStepError
from cubing_algs.scrambler.constants import CROSS_DIFFICULTIES
from cubing_algs.scrambler.constants import DEFAULT_RNG
from cubing_algs.scrambler.constants import MOVES_AUF
from cubing_algs.scrambler.moves import build_cube_move_set
from cubing_algs.scrambler.moves import random_moves
from cubing_algs.scrambler.parse import parse_piece_spec
from cubing_algs.scrambler.pieces import cubies_to_scramble
from cubing_algs.scrambler.pieces import disorient_corners
from cubing_algs.scrambler.pieces import orient_corners
from cubing_algs.scrambler.pieces import random_corner_orientation
from cubing_algs.scrambler.pieces import random_edge_orientation
from cubing_algs.scrambler.pieces import random_permutation
from cubing_algs.transform.mirror import mirror_moves
from cubing_algs.vcube import VCube


def apply_moves(
        cubies: CubeCubies,
        moves: str | Algorithm,
) -> CubeCubies:
    """
    Apply move sequence to cube state.

    Args:
        cubies: State of the cube in cubies.
        moves: Move sequence string (e.g., "R U R'").

    Returns:
        Tuple of (cp, co, ep, eo) with moves applied.

    """
    temp_cube = VCube.from_cubies(*cubies, SOLVED_SO)
    temp_cube.rotate(moves)
    cp, co, ep, eo, _ = temp_cube.to_cubies
    return cp, co, ep, eo


def apply_auf(
        cubies: CubeCubies,
        rng: Random,
) -> CubeCubies:
    """
    Apply random AUF (Adjustment of U Face) to cube state.

    Args:
        cubies: State of the cube in cubies.
        rng: Random number generator.

    Returns:
        Tuple of (cp, co, ep, eo) with AUF applied.

    """
    auf_move = rng.choice(MOVES_AUF)

    if auf_move:
        return apply_moves(cubies, auf_move)

    return cubies


# Supported step types
SUPPORTED_STEPS: Final[list[str]] = [
    # Last Layer steps
    'LL', 'OLL', 'PLL', 'CLL', 'OLLCP', 'COLL', 'ZBLL', '2GLL',
    'OCLL', 'ELL', 'EPLL', 'CPLL', 'ZZLL',
    # F2L variants
    'F2L', 'ZZF2L', 'ZZRB', 'PETRUSF2L',
    # Last Slot variants
    'LS', 'ELS', 'ZZLS', 'TSLE', 'CLS', 'CPLS', 'EJLS', 'EJF2L',
    'TTLL', 'WV', 'SV', 'VLS', 'VHLS',
    # Roux method
    'CMLL', 'CMLLEO', 'SB',
    # Petrus method
    'PETRUS2x2x3', 'PETRUSEO',
]


def generate_step_state(  # noqa: C901, PLR0912, PLR0914, PLR0915
        step: str,
        rng: Random | None = None,
) -> CubeCubies:
    """
    Generate cube state for a specific speedcubing step.

    This function implements the logic for each step type, manipulating
    the cubie arrays (cp, co, ep, eo) to create the desired partial-solve state.

    Notes: The cubies are user oriented, so to change the face colors impacted
    a rotation of the cube or an algorithm translation should be applied.

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
    cp = SOLVED_CP.copy()
    co = SOLVED_CO.copy()
    ep = SOLVED_EP.copy()
    eo = SOLVED_EO.copy()

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

    # 2GLL - specific pattern with phase edges permutation only
    elif step == '2GLL':
        cp, co, ep, eo = apply_auf((cp, co, ep, eo), rng)
        cp, co, ep, eo = random_permutation([], U_EDGES, rng)
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
        phase_edges = parse_piece_spec('UF UB', 'edge')
        cp, co, ep, eo = random_permutation(U_CORNERS, phase_edges, rng)
        co = random_corner_orientation(U_CORNERS, rng)
        cp, co, ep, eo = apply_auf((cp, co, ep, eo), rng)

    # F2L - First Two Layers
    elif step == 'F2L':
        f2l_edges = parse_piece_spec('U FR FL BR BL', 'edge')
        cp, co, ep, eo = random_permutation(SOLVED_CP, f2l_edges, rng)
        co = random_corner_orientation(SOLVED_CP, rng)
        eo = random_edge_orientation(f2l_edges, rng)

    # ZZF2L - ZZ method F2L
    elif step == 'ZZF2L':
        zzf2l_edges = parse_piece_spec('R U L', 'edge')
        cp, co, ep, eo = random_permutation(SOLVED_CP, zzf2l_edges, rng)
        co = random_corner_orientation(SOLVED_CP, rng)

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
        ejls_corners = parse_piece_spec('U DFR', 'corner')
        ejls_corner = parse_piece_spec('DFR', 'corner')
        cp, co, ep, eo = random_permutation(U_CORNERS, U_EDGES, rng)
        co = random_corner_orientation(ejls_corners, rng)
        co = disorient_corners(co, ejls_corner, U_CORNERS, rng)

    # TTLL - Two-Twist Last Layer
    elif step == 'TTLL':
        ttll_corners = parse_piece_spec('U DFR', 'corner')
        cp, co, ep, eo = random_permutation(ttll_corners, U_EDGES, rng)

    # WV - Winter Variation
    elif step == 'WV':
        cp, co, ep, eo = random_permutation(U_CORNERS, U_EDGES, rng)
        co = random_corner_orientation(U_CORNERS, rng)
        cp, co, ep, eo = apply_moves((cp, co, ep, eo), "R U R'")

    # SV - Summer Variation
    elif step == 'SV':
        cp, co, ep, eo = random_permutation(U_CORNERS, U_EDGES, rng)
        co = random_corner_orientation(U_CORNERS, rng)
        cp, co, ep, eo = apply_moves((cp, co, ep, eo), "R U' R'")

    # VLS, VHLS - Valk Last Slot
    elif step in {'VLS', 'VHLS'}:
        cp, co, ep, eo = random_permutation(U_CORNERS, U_EDGES, rng)
        co = random_corner_orientation(U_CORNERS, rng)
        eo = random_edge_orientation(U_EDGES, rng)
        cp, co, ep, eo = apply_moves((cp, co, ep, eo), "R U' R'")

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
        *, include_auf: bool = False,
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

    cubies = generate_step_state(step, rng)

    if include_auf:
        cubies = apply_auf(cubies, rng)

    return cubies_to_scramble(cubies)


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
    cubies = apply_auf((cp, co, ep, eo), rng)

    return cubies_to_scramble(cubies)


def scramble_easy_cross(
        difficulty: str = 'normal',
        rng: Random | None = None,
) -> tuple[Algorithm, Algorithm]:
    """
    Generate an easy cross scramble using only basic face moves.

    Creates a simple scramble suitable for practicing cross patterns
    in speedcubing methods like CFOP.

    Args:
        difficulty: Optional difficulty string.
        rng: Optional random number generator.

    Returns:
        Algorithms to reach the scramble and cross solution

    """
    # Scramble keeping the cross
    f2l_edges = parse_piece_spec('U FR FL BR BL', 'edge')

    cp, co, ep, eo = random_permutation(SOLVED_CP, f2l_edges, rng)
    co = random_corner_orientation(SOLVED_CP, rng)
    eo = random_edge_orientation(f2l_edges, rng)

    # Apply moves to break the cross
    move_set = build_cube_move_set(3)
    move_iterations = CROSS_DIFFICULTIES.get(difficulty, 5)
    moves = random_moves(3, move_set, move_iterations, rng)

    cubies = apply_moves((cp, co, ep, eo), moves)

    # Build scramble and solution
    scramble = cubies_to_scramble(cubies)
    solution = moves.transform(mirror_moves)

    return scramble, solution


def scramble_x_cross(
        difficulty: str = 'normal',
        slot: str = 'FR',
        rng: Random | None = None,
) -> tuple[Algorithm, Algorithm]:
    """
    Generate an x-cross scramble using only basic face moves.

    Creates a simple scramble suitable for practicing x-cross patterns
    in speedcubing methods like CFOP.

    Args:
        difficulty: Optional difficulty string.
        slot: Optional F2L aimed.
        rng: Optional random number generator.

    Returns:
        Algorithms to reach the scramble and cross solution

    """
    # Scramble keeping the cross and a F2L slot
    corners = []
    edges = []

    for edge, corner in F2L_EDGE_CORNERS.items():
        if edge != slot:
            corners.append(corner)
            edges.append(edge)

    f2l_corners = parse_piece_spec(f'U { " ".join(corners) }', 'corner')
    f2l_edges = parse_piece_spec(f'U { " ".join(edges) }', 'edge')

    cp, co, ep, eo = random_permutation(f2l_corners, f2l_edges, rng)
    co = random_corner_orientation(f2l_corners, rng)
    eo = random_edge_orientation(f2l_edges, rng)

    # Apply moves to break the x-cross
    move_set = build_cube_move_set(3)
    move_iterations = CROSS_DIFFICULTIES.get(difficulty, 5) + 2
    moves = random_moves(3, move_set, move_iterations, rng)

    cubies = apply_moves((cp, co, ep, eo), moves)

    # Build scramble and solution
    scramble = cubies_to_scramble(cubies)
    solution = moves.transform(mirror_moves)

    return scramble, solution
