"""
Scramble generation for Rubik's cubes.

This module provides comprehensive scramble generation functionality:
- Random scrambles for cubes of various sizes (2x2x2 to NxNxN)
- Step-based scrambles for speedcubing practice (PLL, OLL, F2L, etc.)
- Fine-grained piece-level scramble constraints
- Utility functions for cube state manipulation

Submodules:
- random: Basic random scramble generation
- utils: Utility functions and constants
- pieces: Low-level piece manipulation
- steps: Step-based scramble generation
"""

# Re-export from random module
# Re-export from pieces module (including _calculate_parity for tests)
from cubing_algs.scrambler.pieces import _calculate_parity
from cubing_algs.scrambler.pieces import arrange_pieces
from cubing_algs.scrambler.pieces import derange_pieces
from cubing_algs.scrambler.pieces import disorient_corners
from cubing_algs.scrambler.pieces import disorient_edges
from cubing_algs.scrambler.pieces import flip_n_edges
from cubing_algs.scrambler.pieces import orient_corners
from cubing_algs.scrambler.pieces import orient_edges
from cubing_algs.scrambler.pieces import random_corner_orientation
from cubing_algs.scrambler.pieces import random_edge_orientation
from cubing_algs.scrambler.pieces import random_permutation
from cubing_algs.scrambler.random import DEFAULT_RNG
from cubing_algs.scrambler.random import EXCLUDE_ODD_FACES_LH
from cubing_algs.scrambler.random import EXCLUDE_ODD_FACES_RH
from cubing_algs.scrambler.random import FACE_REGEXP
from cubing_algs.scrambler.random import MOVES_EASY_CROSS
from cubing_algs.scrambler.random import build_cube_move_set
from cubing_algs.scrambler.random import is_valid_next_move
from cubing_algs.scrambler.random import random_moves
from cubing_algs.scrambler.random import scramble
from cubing_algs.scrambler.random import scramble_easy_cross
from cubing_algs.scrambler.steps import SUPPORTED_STEPS

# Re-export from steps module
from cubing_algs.scrambler.steps import InvalidStepError
from cubing_algs.scrambler.steps import scramble_ocll_case
from cubing_algs.scrambler.steps import scramble_step
from cubing_algs.scrambler.steps import scramble_with_piece_constraints

# Re-export from utils module
from cubing_algs.scrambler.utils import ALL_CORNERS
from cubing_algs.scrambler.utils import ALL_EDGES
from cubing_algs.scrambler.utils import B_CORNERS
from cubing_algs.scrambler.utils import B_EDGES
from cubing_algs.scrambler.utils import CORNER_NAMES
from cubing_algs.scrambler.utils import D_CORNERS
from cubing_algs.scrambler.utils import D_EDGES
from cubing_algs.scrambler.utils import E_EDGES
from cubing_algs.scrambler.utils import EDGE_NAMES
from cubing_algs.scrambler.utils import F_CORNERS
from cubing_algs.scrambler.utils import F_EDGES
from cubing_algs.scrambler.utils import L_CORNERS
from cubing_algs.scrambler.utils import L_EDGES
from cubing_algs.scrambler.utils import LAYER_MAP_CORNERS
from cubing_algs.scrambler.utils import LAYER_MAP_EDGES
from cubing_algs.scrambler.utils import R_CORNERS
from cubing_algs.scrambler.utils import R_EDGES
from cubing_algs.scrambler.utils import U_CORNERS
from cubing_algs.scrambler.utils import U_EDGES
from cubing_algs.scrambler.utils import InvalidPieceSpecError
from cubing_algs.scrambler.utils import parse_piece_spec
from cubing_algs.scrambler.utils import solve_to_algorithm
from cubing_algs.scrambler.utils import vcube_to_kociemba_string

__all__ = [
    # utils module
    'ALL_CORNERS',
    'ALL_EDGES',
    'B_CORNERS',
    'B_EDGES',
    'CORNER_NAMES',
    # random module
    'DEFAULT_RNG',
    'D_CORNERS',
    'D_EDGES',
    'EDGE_NAMES',
    'EXCLUDE_ODD_FACES_LH',
    'EXCLUDE_ODD_FACES_RH',
    'E_EDGES',
    'FACE_REGEXP',
    'F_CORNERS',
    'F_EDGES',
    'LAYER_MAP_CORNERS',
    'LAYER_MAP_EDGES',
    'L_CORNERS',
    'L_EDGES',
    'MOVES_EASY_CROSS',
    'R_CORNERS',
    'R_EDGES',
    'SUPPORTED_STEPS',
    'U_CORNERS',
    'U_EDGES',
    'InvalidPieceSpecError',
    # steps module
    'InvalidStepError',
    # pieces module
    '_calculate_parity',
    'arrange_pieces',
    'build_cube_move_set',
    'derange_pieces',
    'disorient_corners',
    'disorient_edges',
    'flip_n_edges',
    'is_valid_next_move',
    'orient_corners',
    'orient_edges',
    'parse_piece_spec',
    'random_corner_orientation',
    'random_edge_orientation',
    'random_moves',
    'random_permutation',
    'scramble',
    'scramble_easy_cross',
    'scramble_ocll_case',
    'scramble_step',
    'scramble_with_piece_constraints',
    'solve_to_algorithm',
    'vcube_to_kociemba_string',
]
