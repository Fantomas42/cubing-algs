import re

MAX_ITERATIONS = 50

DOUBLE_CHAR = '2'

INVERT_CHAR = "'"

JAPANESE_CHAR = 'w'

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
    'B': 'U',
    'D': 'B',
    'F': 'D',
    'u': 'f',
    'b': 'u',
    'd': 'b',
    'f': 'd',

    'E': "S'",
    'S': 'E',

    'y': 'z',
    'z': "y'",
}

OFFSET_Y_CW = {
    'B': 'L',
    'R': 'B',
    'F': 'R',
    'L': 'F',
    'b': 'l',
    'r': 'b',
    'f': 'r',
    'l': 'f',

    'S': "M'",
    'M': 'S',

    'z': 'x',
    'x': "z'",
}

OFFSET_Z_CW = {
    'U': 'L',
    'R': 'U',
    'D': 'R',
    'L': 'D',
    'u': 'l',
    'r': 'u',
    'd': 'r',
    'l': 'd',

    'E': "M'",
    'M': 'E',

    'x': 'y',
    'y': "x'",
}

OFFSET_X_CC = {v: k for k, v in OFFSET_X_CW.items()}
OFFSET_Y_CC = {v: k for k, v in OFFSET_Y_CW.items()}
OFFSET_Z_CC = {v: k for k, v in OFFSET_Z_CW.items()}

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
    "L' R": ['M', 'x'],
    "R L'": ['M', 'x'],
    "L R'": ["M'", "x'"],
    "R' L": ["M'", "x'"],

    "r' R": ['M'],
    "R r'": ['M'],
    "l L'": ['M'],
    "L' l": ['M'],

    "r R'": ["M'"],
    "R' r": ["M'"],
    "l' L": ["M'"],
    "L l'": ["M'"],
}

RESLICE_S_MOVES = {
    "F' B": ['S', "z'"],
    "B F'": ['S', "z'"],
    "F B'": ["S'", 'z'],
    "B' F": ["S'", 'z'],

    "f F'": ['S'],
    "F' f": ['S'],
    "b' B": ['S'],
    "B b'": ['S'],

    "f' F": ["S'"],
    "F f'": ["S'"],
    "b B'": ["S'"],
    "B' b": ["S'"],
}

RESLICE_E_MOVES = {
    "U D'": ['E', 'y'],
    "D' U": ['E', 'y'],
    "U' D": ["E'", "y'"],
    "D U'": ["E'", "y'"],

    "u' U": ['E'],
    "U u'": ['E'],
    "d D'": ['E'],
    "D' d": ['E'],

    "u U'": ["E'"],
    "U' u": ["E'"],
    "d' D": ["E'"],
    "D d'": ["E'"],
}

RESLICE_MOVES = {}
RESLICE_MOVES.update(RESLICE_M_MOVES)
RESLICE_MOVES.update(RESLICE_S_MOVES)
RESLICE_MOVES.update(RESLICE_E_MOVES)

UNFAT_ROTATION_MOVES = {
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

UNFAT_SLICE_MOVES = {
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

REFAT_MOVES = {
    ' '.join(v): k
    for k, v in UNFAT_ROTATION_MOVES.items()
}
REFAT_MOVES.update(
    {
        ' '.join(reversed(v)): k
        for k, v in UNFAT_ROTATION_MOVES.items()
    },
)
REFAT_MOVES.update(
    {
        ' '.join(v): k
        for k, v in UNFAT_SLICE_MOVES.items()
    },
)
REFAT_MOVES.update(
    {
        ' '.join(reversed(v)): k
        for k, v in UNFAT_SLICE_MOVES.items()
    },
)


MOVE_SPLIT = re.compile(r"([\d-]*[LlRrUuDdFfBbMSExyz][w]?[2']?(?!-)(?:@\d+)?)")

LAYER_SPLIT = re.compile(r'(([\d-]*)([lrudfb]|[LRUDFB][w]?))')

SYMMETRY_M = {
    'U': 'U', 'u': 'u',                     'y': 'y',  # noqa: E241
    'F': 'F', 'f': 'f', 'S': 'S',           'z': 'z',  # noqa: E241
    'R': 'L', 'r': 'l',                     'x': 'x',  # noqa: E241
    'B': 'B', 'b': 'b',
    'L': 'R', 'l': 'r', 'M': 'M',
    'D': 'D', 'd': 'd', 'E': 'E',
}

SYMMETRY_S = {
    'U': 'U', 'u': 'u',                     'y': 'y',  # noqa: E241
    'F': 'B', 'f': 'b', 'S': 'S',           'z': 'z',  # noqa: E241
    'R': 'R', 'r': 'r',                     'x': 'x',  # noqa: E241
    'B': 'F', 'b': 'f',
    'L': 'L', 'l': 'l', 'M': 'M',
    'D': 'D', 'd': 'd', 'E': 'E',
}

SYMMETRY_E = {
    'U': 'D', 'u': 'd',                     'y': 'y',  # noqa: E241
    'F': 'F', 'f': 'f', 'S': 'S',           'z': 'z',  # noqa: E241
    'R': 'R', 'r': 'r',                     'x': 'x',  # noqa: E241
    'B': 'B', 'b': 'b',
    'L': 'L', 'l': 'l', 'M': 'M',
    'D': 'U', 'd': 'u', 'E': 'E',
}

OPPOSITE_FACES = {
    'F': 'B',
    'R': 'L',
    'U': 'D',
    'B': 'F',
    'L': 'R',
    'D': 'U',
}
