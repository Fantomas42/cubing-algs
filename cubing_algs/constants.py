"""
Constants and configuration values for the cubing-algs library.

This module defines all the fundamental constants used throughout the library
including move notations, facelet mappings, transformation tables, and
algorithm patterns. These constants support cube manipulation, move parsing,
transformations, and visual display.
"""
import re

from cubing_algs.annotations import CubeOrientation
from cubing_algs.annotations import Facelet
from cubing_algs.annotations import RegexPattern

DEFAULT_CUBE_SIZE = 3

# Safety cap on the number of passes optimize/size/wide transforms will
# run before giving up on reaching a fixed point.
MAX_ITERATIONS = 50

# Default maximum time difference (Move.timed units) between
# consecutive moves for them to be considered for reslicing
# (e.g. "L' R" -> "M x") when the algorithm carries timing data.
RESLICE_THRESHOLD = 50

# Default maximum time difference (Move.timed units) between
# consecutive moves for them to be considered for rewiding
# (e.g. "L x" -> "r") when the algorithm carries timing data.
REWIDE_THRESHOLD = 50

DOUBLE_CHAR = '2'

INVERT_CHAR = "'"

WIDE_CHAR = 'w'

PAUSE_CHAR = '.'

AUF_CHAR = 'U'

ROTATIONS = (
    'x', 'y', 'z',
)

INNER_MOVES = (
    'M', 'S', 'E',
)

OUTER_BASIC_MOVES = (
    'R', 'F', 'U',
    'L', 'B', 'D',
)

OUTER_WIDE_MOVES = tuple(
    move.lower()
    for move in OUTER_BASIC_MOVES
)

OUTER_MOVES = OUTER_BASIC_MOVES + OUTER_WIDE_MOVES

ALL_BASIC_MOVES = OUTER_MOVES + INNER_MOVES + ROTATIONS

OFFSET_X_CW = {
    'U': 'F',
    'D': 'B',

    'F': 'D',
    'B': 'U',

    'S': 'E',
    'E': "S'",

    'y': 'z',
    'z': "y'",
}

OFFSET_X_CC = {
    'U': 'B',
    'D': 'F',

    'F': 'U',
    'B': 'D',

    'S': "E'",
    'E': 'S',

    'y': "z'",
    'z': 'y',
}

OFFSET_Y_CW = {
    'R': 'B',
    'L': 'F',

    'F': 'R',
    'B': 'L',

    'M': 'S',
    'S': "M'",

    'x': "z'",
    'z': 'x',
}

OFFSET_Y_CC = {
    'R': 'F',
    'L': 'B',

    'F': 'L',
    'B': 'R',

    'M': "S'",
    'S': 'M',

    'x': 'z',
    'z': "x'",
}

OFFSET_Z_CW = {
    'U': 'L',
    'D': 'R',

    'R': 'U',
    'L': 'D',

    'M': 'E',
    'E': "M'",

    'x': 'y',
    'y': "x'",
}

OFFSET_Z_CC = {
    'U': 'R',
    'D': 'L',

    'R': 'D',
    'L': 'U',

    'M': "E'",
    'E': 'M',

    'x': "y'",
    'y': 'x',
}


OFFSET_TABLE = {
    'x': OFFSET_X_CW,
    "x'": OFFSET_X_CC,
    'y': OFFSET_Y_CW,
    "y'": OFFSET_Y_CC,
    'z': OFFSET_Z_CW,
    "z'": OFFSET_Z_CC,
}

UNSLICE_WIDE_MOVES = {
    'M': ["r'", 'R'],
    "M'": ['r', "R'"],
    'M2': ['r2', 'R2'],

    'S': ['f', "F'"],
    "S'": ["f'", 'F'],
    'S2': ['f2', 'F2'],

    'E': ["u'", 'U'],
    "E'": ['u', "U'"],
    'E2': ['u2', 'U2'],
}

UNSLICE_ROTATION_MOVES = {
    'M': ["L'", 'R', "x'"],
    "M'": ['L', "R'", 'x'],
    'M2': ['L2', 'R2', 'x2'],

    'S': ["F'", 'B', 'z'],
    "S'": ['F', "B'", "z'"],
    'S2': ['F2', 'B2', 'z2'],

    'E': ["D'", 'U', "y'"],
    "E'": ['D', "U'", 'y'],
    'E2': ['D2', 'U2', 'y2'],
}

RESLICE_M_MOVES = {
    # 2-move patterns (sorted form is canonical)
    "L' R": ['M', 'x'],
    "L R'": ["M'", "x'"],
    'L2 R2': ['M2', 'x2'],

    # 3-move patterns with rotation (sorted form is canonical)
    "L' R x'": ['M'],
    "L R' x": ["M'"],
    'L2 R2 x2': ['M2'],

    # Wide move patterns (sorted form is canonical)
    "L' l": ['M'],
    "R r'": ['M'],
    "L l'": ["M'"],
    "R' r": ["M'"],
    'L2 l2': ['M2'],
    'R2 r2': ['M2'],
}

RESLICE_S_MOVES = {
    # 2-move patterns (sorted form is canonical)
    "B F'": ['S', "z'"],
    "B' F": ["S'", 'z'],
    'B2 F2': ['S2', 'z2'],

    # 3-move patterns with rotation (sorted form is canonical)
    "B F' z": ['S'],
    "B' F z'": ["S'"],
    'B2 F2 z2': ['S2'],

    # Wide move patterns (sorted form is canonical)
    "F' f": ['S'],
    "B b'": ['S'],
    "F f'": ["S'"],
    "B' b": ["S'"],
    'B2 b2': ['S2'],
    'F2 f2': ['S2'],
}

RESLICE_E_MOVES = {
    # 2-move patterns (sorted form is canonical)
    "D' U": ['E', 'y'],
    "D U'": ["E'", "y'"],
    'D2 U2': ['E2', 'y2'],

    # 3-move patterns with rotation (sorted form is canonical)
    "D' U y'": ['E'],
    "D U' y": ["E'"],
    'D2 U2 y2': ['E2'],

    # Wide move patterns (sorted form is canonical)
    "U u'": ['E'],
    "D' d": ['E'],
    "U' u": ["E'"],
    "D d'": ["E'"],
    'D2 d2': ['E2'],
    'U2 u2': ['E2'],
}

RESLICE_MOVES: dict[str, list[str]] = {}
RESLICE_MOVES.update(RESLICE_M_MOVES)
RESLICE_MOVES.update(RESLICE_S_MOVES)
RESLICE_MOVES.update(RESLICE_E_MOVES)

UNWIDE_ROTATION_MOVES = {
    'r': ['L', 'x'],
    "r'": ["L'", "x'"],
    'r2': ['L2', 'x2'],

    'l': ['R', "x'"],
    "l'": ["R'", 'x'],
    'l2': ['R2', 'x2'],

    'f': ['B', 'z'],
    "f'": ["B'", "z'"],
    'f2': ['B2', 'z2'],

    'b': ['F', "z'"],
    "b'": ["F'", 'z'],
    'b2': ['F2', 'z2'],

    'u': ['D', 'y'],
    "u'": ["D'", "y'"],
    'u2': ['D2', 'y2'],

    'd': ['U', "y'"],
    "d'": ["U'", 'y'],
    'd2': ['U2', 'y2'],
}

UNWIDE_SLICE_MOVES = {
    'r': ['R', "M'"],
    "r'": ["R'", 'M'],
    'r2': ['R2', 'M2'],

    'l': ['L', 'M'],
    "l'": ["L'", "M'"],
    'l2': ['L2', 'M2'],

    'f': ['F', 'S'],
    "f'": ["F'", "S'"],
    'f2': ['F2', 'S2'],

    'b': ['B', "S'"],
    "b'": ["B'", 'S'],
    'b2': ['B2', 'S2'],

    'u': ['U', "E'"],
    "u'": ["U'", 'E'],
    'u2': ['U2', 'E2'],

    'd': ['D', 'E'],
    "d'": ["D'", "E'"],
    'd2': ['D2', 'E2'],
}

REWIDE_MOVES = {
    ' '.join(v): k
    for k, v in UNWIDE_ROTATION_MOVES.items()
}
REWIDE_MOVES.update(
    {
        ' '.join(reversed(v)): k
        for k, v in UNWIDE_ROTATION_MOVES.items()
    },
)
REWIDE_MOVES.update(
    {
        ' '.join(v): k
        for k, v in UNWIDE_SLICE_MOVES.items()
    },
)
REWIDE_MOVES.update(
    {
        ' '.join(reversed(v)): k
        for k, v in UNWIDE_SLICE_MOVES.items()
    },
)
UNWIDE_ROTATION_MOVES.update(
    {
        f'{ k.upper() }w' if len(k) == 1 else f'{ k[0].upper() }w{ k[1] }': v
        for k, v in UNWIDE_ROTATION_MOVES.items()
    },
)
UNWIDE_SLICE_MOVES.update(
    {
        f'{ k.upper() }w' if len(k) == 1 else f'{ k[0].upper() }w{ k[1] }': v
        for k, v in UNWIDE_SLICE_MOVES.items()
    },
)


# Matches one full move token: optional layer number(s), the base move
# letter, optional 'w' (wide), optional '2' or ''' modifier, optional
# '@<time>' suffix. Also matches a standalone pause '.' with an optional
# '@<time>' suffix. The negative lookahead `(?!-)` avoids swallowing a
# trailing '-' that belongs to the next move's layer number.
MOVE_SPLIT: RegexPattern = re.compile(
    r"([\d-]*[LlRrUuDdFfBbMSExyz][w]?[2']?(?!-)(?:@\d+)?|\.(?:@\d+)?)",
)

# Matches one layer specifier: optional layer number(s) followed by
# either a lowercase wide-move letter (e.g. 'r') or an uppercase basic
# move letter with an optional 'w' (e.g. 'R', 'Rw').
LAYER_SPLIT: RegexPattern = re.compile(r'(([\d-]*)([lrudfb]|[LRUDFB][w]?))')

SYMMETRY_M = {
    'F': 'F', 'S': 'S', 'z': 'z',
    'U': 'U',           'y': 'y',  # noqa: E241
    'R': 'L',           'x': 'x',  # noqa: E241
    'B': 'B',
    'L': 'R', 'M': 'M',
    'D': 'D', 'E': 'E',
}

SYMMETRY_S = {
    'F': 'B', 'S': 'S', 'z': 'z',
    'U': 'U',           'y': 'y',  # noqa: E241
    'R': 'R',           'x': 'x',  # noqa: E241
    'B': 'F',
    'L': 'L', 'M': 'M',
    'D': 'D', 'E': 'E',
}

SYMMETRY_E = {
    'F': 'F', 'S': 'S', 'z': 'z',
    'U': 'D',           'y': 'y',  # noqa: E241
    'R': 'R',           'x': 'x',  # noqa: E241
    'B': 'B',
    'L': 'L', 'M': 'M',
    'D': 'U', 'E': 'E',
}

SYMMETRY_TABLE = {
    'M': ({'x', 'M'}, SYMMETRY_M),
    'S': ({'z', 'S'}, SYMMETRY_S),
    'E': ({'y', 'E'}, SYMMETRY_E),
}

OPPOSITE_FACES = {
    'U': 'D',
    'R': 'L',
    'F': 'B',
    'D': 'U',
    'L': 'R',
    'B': 'F',
}

ADJACENT_FACES = {
    'U': ('F', 'R', 'B', 'L'),
    'R': ('F', 'D', 'B', 'U'),
    'F': ('D', 'R', 'U', 'L'),
    'D': ('F', 'L', 'B', 'R'),
    'L': ('F', 'U', 'B', 'D'),
    'B': ('U', 'R', 'D', 'L'),
}

FACE_ORDER: tuple[Facelet, ...] = ('U', 'R', 'F', 'D', 'L', 'B')

FACE_NUMBER = len(FACE_ORDER)

FACE_INDEXES: dict[str, int] = {
    face: i
    for i, face in enumerate(FACE_ORDER)
}

FACES = ''.join(FACE_ORDER)

F2L_EDGE_CORNERS = {  # Edge: Corner
    'FL': 'DLF',
    'FR': 'DFR',
    'BL': 'DBL',
    'BR': 'DRB',
}

ITERATIONS_BY_CUBE_SIZE = {
    2: (9, 11),
    3: (25, 30),
    4: (45, 50),
    5: (60, 60),
    6: (80, 80),
    7: (100, 100),
}

# Orientation move selection priority:
# 1. Fewest moves (1-move always beats 2-move)
# 2. Double moves (y2, x2, z2) preferred in first position
# 3. y-axis preferred over x-axis, x-axis over z-axis
# 4. Clockwise preferred over counter-clockwise
OFFSET_ORIENTATION_MAP: dict[str, str] = {
    '01': 'y',
    '02': '',
    '04': "y'",
    '05': 'y2',
    '10': "y' x'",
    '12': "z'",
    '13': 'y x',
    '15': 'y2 z',
    '20': "y2 x'",
    '21': 'x y',
    '23': 'x',
    '24': "x y'",
    '31': 'x2 y',
    '32': 'z2',
    '34': "x2 y'",
    '35': 'x2',
    '40': "y x'",
    '42': 'z',
    '43': "y' x",
    '45': "y2 z'",
    '50': "x'",
    '51': "y z'",
    '53': 'y2 x',
    '54': "y' z",
    '0': '',
    '1': "z'",
    '2': 'x',
    '3': 'z2',
    '4': 'z',
    '5': "x'",
}

ORIENTATIONS: list[str] = [
    'UF', 'UR', 'UL', 'UB',
    'DF', 'DR', 'DL', 'DB',

    'RF', 'RD', 'RB', 'RU',
    'LF', 'LD', 'LB', 'LU',

    'FD', 'FR', 'FU', 'FL',
    'BD', 'BR', 'BU', 'BL',
]

# Optimal rotation sequences for each of the 24 cube orientations.
# Maps orientation (top-face + front-face) to the shortest rotation
# sequence (at most 2 moves) that achieves it from solved (UF).
ORIENTATION_FACE_MOVES: dict[CubeOrientation, str] = {
    'UF': '',
    'UR': 'y',
    'UL': "y'",
    'UB': 'y2',

    'DF': 'z2',
    'DR': 'x2 y',
    'DL': "x2 y'",
    'DB': 'x2',

    'RF': "z'",
    'RD': 'y x',
    'RB': 'y2 z',
    'RU': "y' x'",

    'LF': 'z',
    'LD': "y' x",
    'LB': "y2 z'",
    'LU': "y x'",

    'FD': 'x',
    'FR': 'x y',
    'FU': "y2 x'",
    'FL': "x y'",

    'BD': 'y2 x',
    'BR': "y z'",
    'BU': "x'",
    'BL': "y' z",
}

FACE_EDGES_INDEX = {1, 3, 5, 7}

FACE_CORNERS_INDEX = {0, 2, 6, 8}

# QTM distance calculation constants.
# NOTE: the two constants below both hold the "diametrically opposite
# position on a face" pairs, so their values coincide. They are kept
# separate since they are used in distinct semantic contexts in
# impacts.py (same-face vs opposite-face distance calculations).
QTM_SAME_FACE_OPPOSITE_PAIRS = {
    (0, 8), (8, 0),  # Top-left corner <-> Bottom-right corner
    (2, 6), (6, 2),  # Top-right corner <-> Bottom-left corner
    (1, 7), (7, 1),  # Top edge <-> Bottom edge
    (3, 5), (5, 3),  # Left edge <-> Right edge
}

QTM_OPPOSITE_FACE_DOUBLE_PAIRS = {
    (1, 7), (7, 1),  # Top edge <-> Bottom edge
    (3, 5), (5, 3),  # Left edge <-> Right edge
    (0, 8), (8, 0),  # Top-left corner <-> Bottom-right corner
    (2, 6), (6, 2),  # Top-right corner <-> Bottom-left corner
}

QTM_OPPOSITE_EDGE_OFFSETS = {
    1: 6,
    7: -6,
    3: 2,
    5: -2,
}

# 3x3x3 constants
CORNER_NUMBER = 8
CORNER_VALID_ORIENTATIONS = {0, 1, 2}
CORNER_MODULUS = len(CORNER_VALID_ORIENTATIONS)

EDGE_NUMBER = 12
EDGE_VALID_ORIENTATIONS = {0, 1}
EDGE_MODULUS = len(EDGE_VALID_ORIENTATIONS)

SOLVED_CP = list(range(CORNER_NUMBER))
SOLVED_CO = [0] * CORNER_NUMBER
SOLVED_EP = list(range(EDGE_NUMBER))
SOLVED_EO = [0] * EDGE_NUMBER
SOLVED_SO = list(range(FACE_NUMBER))

CORNER_FACELET_MAP = [
    [8, 9, 20],    # URF
    [6, 18, 38],   # UFL
    [0, 36, 47],   # ULB
    [2, 45, 11],   # UBR
    [29, 26, 15],  # DFR
    [27, 44, 24],  # DLF
    [33, 53, 42],  # DBL
    [35, 17, 51],  # DRB
]

EDGE_FACELET_MAP = [
    [5, 10],   # UR
    [7, 19],   # UF
    [3, 37],   # UL
    [1, 46],   # UB
    [32, 16],  # DR
    [28, 25],  # DF
    [30, 43],  # DL
    [34, 52],  # DB
    [23, 12],  # FR
    [21, 41],  # FL
    [50, 39],  # BL
    [48, 14],  # BR
]

CORNER_NAMES = [
    'URF', 'UFL', 'ULB', 'UBR',
    'DFR', 'DLF', 'DBL', 'DRB',
]

EDGE_NAMES = [
    'UR', 'UF', 'UL', 'UB',
    'DR', 'DF', 'DL', 'DB',
    'FR', 'FL', 'BL', 'BR',
]

U_CORNERS = [0, 1, 2, 3]  # URF, UFL, ULB, UBR
D_CORNERS = [4, 5, 6, 7]  # DFR, DLF, DBL, DRB
R_CORNERS = [0, 3, 4, 7]  # URF, UBR, DFR, DRB
L_CORNERS = [1, 2, 5, 6]  # UFL, ULB, DLF, DBL
F_CORNERS = [0, 1, 4, 5]  # URF, UFL, DFR, DLF
B_CORNERS = [2, 3, 6, 7]  # ULB, UBR, DBL, DRB

U_EDGES = [0, 1, 2, 3]    # UR, UF, UL, UB
D_EDGES = [4, 5, 6, 7]    # DR, DF, DL, DB
R_EDGES = [0, 4, 8, 11]   # UR, DR, FR, BR
L_EDGES = [2, 6, 9, 10]   # UL, DL, FL, BL
F_EDGES = [1, 5, 8, 9]    # UF, DF, FR, FL
B_EDGES = [3, 7, 10, 11]  # UB, DB, BL, BR
E_EDGES = [8, 9, 10, 11]  # FR, FL, BL, BR

LAYER_MAP_CORNERS: dict[str, list[int]] = {
    'U': U_CORNERS,
    'D': D_CORNERS,
    'R': R_CORNERS,
    'L': L_CORNERS,
    'F': F_CORNERS,
    'B': B_CORNERS,
}

LAYER_MAP_EDGES: dict[str, list[int]] = {
    'U': U_EDGES,
    'D': D_EDGES,
    'R': R_EDGES,
    'L': L_EDGES,
    'F': F_EDGES,
    'B': B_EDGES,
    'E': E_EDGES,
}
