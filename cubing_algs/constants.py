import re

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

UNSLICE = {
    'M': ["r'", 'R'],
    'S': ['f', "F'"],
    'E': ['u', "U'"],
    "M'": ['r', "R'"],
    "S'": ["f'", 'F'],
    "E'": ["u'", 'U'],
    'M2': ['r2', 'R2'],
    'S2': ['f2', 'F2'],
    'E2': ['u2', 'U2'],
}

MOVE_SPLIT = re.compile(r"([LlRrUuDdFfBbMSExyz][w]?[2']?)")

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
