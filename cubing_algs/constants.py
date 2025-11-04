"""
Constants and configuration values for the cubing-algs library.

This module defines all the fundamental constants used throughout the library
including move notations, facelet mappings, transformation tables, and
algorithm patterns. These constants support cube manipulation, move parsing,
transformations, and visual display.
"""
import re

MAX_ITERATIONS = 50

RESLICE_THRESHOLD = 50

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
    'D': 'L',
    'L': 'U',
    'R': 'D',
    'U': 'R',

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
    'D2 U2': ['E2 y2'],

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

RESLICE_MOVES = {}
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


MOVE_SPLIT = re.compile(
    r"([\d-]*[LlRrUuDdFfBbMSExyz][w]?[2']?(?!-)(?:@\d+)?|\.(?:@\d+)?)",
)

LAYER_SPLIT = re.compile(r'(([\d-]*)([lrudfb]|[LRUDFB][w]?))')

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
    'U': ('R', 'L', 'F', 'B'),
    'R': ('F', 'B', 'U', 'D'),
    'F': ('U', 'D', 'L', 'R'),
    'D': ('R', 'L', 'F', 'B'),
    'L': ('F', 'B', 'U', 'D'),
    'B': ('U', 'D', 'L', 'R'),
}

FACE_ORDER = ['U', 'R', 'F', 'D', 'L', 'B']

FACE_INDEXES = {
    face: i
    for i, face in enumerate(FACE_ORDER)
}

FACES = ''.join(FACE_ORDER)

INITIAL_STATE = ''.join(face * 9 for face in FACE_ORDER)

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

F2L_FACES = ['F', 'L', 'R', 'B']

F2L_FACE_ORIENTATIONS = {
    'FL': 'F',
    'FR': 'R',
    'BL': 'L',
    'BR': 'B',
}

F2L_ADJACENT_FACES = {
    'R': ('B', 'F'),
    'L': ('F', 'B'),
    'B': ('L', 'R'),
    'F': ('R', 'L'),
}

ITERATIONS_BY_CUBE_SIZE = {
    2: (9, 11),
    3: (25, 30),
    4: (45, 50),
    5: (60, 60),
    6: (80, 80),
    7: (100, 100),
}

OFFSET_ORIENTATION_MAP = {
    '01': 'y',
    '02': '',
    '04': "y'",
    '05': 'y2',
    '10': "x' z'",
    '12': "z'",
    '13': "z' y",
    '15': "z' y2",
    '20': "x' z2",
    '21': 'x y',
    '23': 'x',
    '24': "x y'",
    '31': 'y z2',
    '32': 'z2',
    '34': "y' z2",
    '35': 'x2',
    '40': 'z y',
    '42': 'z',
    '43': "z y'",
    '45': 'z y2',
    '50': "x'",
    '51': "x' y",
    '53': "x' y2",
    '54': "x' y'",
    '0': '',
    '1': "z'",
    '2': 'x',
    '3': 'z2',
    '4': 'z',
    '5': "x'",
}

ORIENTATIONS = [
    'UF', 'UR', 'UL', 'UB',
    'DF', 'DR', 'DL', 'DB',

    'RF', 'RD', 'RB', 'RU',
    'LF', 'LD', 'LB', 'LU',

    'FD', 'FR', 'FU', 'FL',
    'BD', 'BR', 'BU', 'BL',
]

FACE_EDGES_INDEX = {1, 3, 5, 7}

FACE_CORNERS_INDEX = {0, 2, 6, 8}

# QTM distance calculation constants
QTM_SAME_FACE_OPPOSITE_PAIRS = {
    (0, 8), (8, 0),  # Top-left corner <-> Bottom-right corner
    (2, 6), (6, 2),  # Top-right corner <-> Bottom-left corner
    (1, 7), (7, 1),  # Top edge <-> Bottom edge
    (3, 5), (5, 3),  # Left edge <-> Right edge
}

QTM_OPPOSITE_FACE_SIMPLE_PAIRS = {
    (1, 1), (7, 7),  # Top edge <-> Bottom edge
    (3, 5), (5, 3),  # Left edge <-> Right edge
    (0, 0), (2, 2),  # Top-left corner + Top-right corner
    (6, 6), (8, 8),  # Bottom-left corner + Bottom-right corner
}

QTM_OPPOSITE_FACE_DOUBLE_PAIRS = {
    (1, 7), (7, 1),  # Top edge <-> Bottom edge
    (3, 3), (5, 5),  # Left edge <-> Right edge
    (0, 8), (8, 0),  # Top-left corner <-> Bottom-right corner
    (2, 6), (6, 2),  # Top-right corner <-> Bottom-left corner
}

QTM_OPPOSITE_EDGE_OFFSETS = {
    1: 6,
    7: -6,
    3: 2,
    5: -2,
}
