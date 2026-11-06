/**
 * Rotation kernel for NxNxN cubes, from 2x2x2 to 20x20x20.
 *
 * A move is reduced to a range of layers of one face turned a number of
 * quarter turns: x is every R layer, M the middle L layer, E the middle D
 * layer, S the middle F layer. The facelet permutation of such a move is
 * computed once, from the geometry of the cube, then cached: executing a
 * move is a single gather over the facelets of the state.
 *
 * Grammar of a move:
 *     move     := [layers] base [w] [modifier]
 *     layers   := N | N-M        (1 <= N <= M <= size, range on wide moves)
 *     base     := U R F D L B | u r f d l b (wide) | x y z | M E S (odd)
 *     modifier := ' | 2 | 2'
 */

#define PY_SSIZE_T_CLEAN
#include <Python.h>
#include <stdint.h>
#include <stdio.h>
#include <string.h>

#define MIN_SIZE 2
#define MAX_SIZE 20
#define MAX_FACELETS (6 * MAX_SIZE * MAX_SIZE)
#define MAX_LAYER_NUMBER 100000
#define CACHE_LIMIT (16 * 1024 * 1024)
#define SHOWN_MOVE_LENGTH 64

enum { FACE_U, FACE_R, FACE_F, FACE_D, FACE_L, FACE_B, FACE_COUNT };

typedef struct {
    int face;   // Face whose layers are turned
    int first;  // First layer, 1 being the face itself
    int last;   // Last layer, included
    int turns;  // Quarter turns clockwise, seen from the face: 1, 2 or 3
} Move;

typedef struct {
    int x, y, z;
} Vector;

// Axis of each face (0 = x, 1 = y, 2 = z), and the direction of the
// rotation turning the face clockwise, as the coordinate system expects it
static const int FACE_AXIS[FACE_COUNT] = {1, 0, 2, 1, 0, 2};
static const int FACE_DIRECTION[FACE_COUNT] = {1, -1, -1, -1, 1, 1};
// Faces whose first layer is at the highest coordinate of their axis
static const int FACE_POSITIVE[FACE_COUNT] = {1, 1, 1, 0, 0, 0};

/**
 * Cached gather permutations, indexed by size, face, first and last layer.
 * Each entry holds the permutations of 1, 2 and 3 quarter turns:
 * after[i] = before[permutation[i]]. The cache lives as long as the
 * process, bounded by CACHE_LIMIT bytes; the GIL guards it.
 */
static uint16_t* cache[MAX_SIZE + 1][FACE_COUNT][MAX_SIZE][MAX_SIZE];
static size_t cache_bytes = 0;

/**
 * Position of the cubie holding a facelet, and the outward normal of the
 * facelet. Facelets are ordered face by face (U R F D L B), row by row,
 * with x from L to R, y from D to U and z from B to F.
 */
static void facelet_geometry(int size, int index, Vector* position, Vector* normal) {
    const int area = size * size;
    const int face = index / area;
    const int row = (index % area) / size;
    const int column = index % size;
    const int far = size - 1;

    *normal = (Vector){0, 0, 0};
    switch (face) {
        case FACE_U:
            *position = (Vector){column, far, row};
            normal->y = 1;
            break;
        case FACE_R:
            *position = (Vector){far, far - row, far - column};
            normal->x = 1;
            break;
        case FACE_F:
            *position = (Vector){column, far - row, far};
            normal->z = 1;
            break;
        case FACE_D:
            *position = (Vector){column, 0, far - row};
            normal->y = -1;
            break;
        case FACE_L:
            *position = (Vector){0, far - row, column};
            normal->x = -1;
            break;
        default:  // FACE_B
            *position = (Vector){far - column, far - row, 0};
            normal->z = -1;
            break;
    }
}

/**
 * Index of the facelet at a position, facing a normal: the inverse of
 * facelet_geometry.
 */
static int facelet_index(int size, Vector position, Vector normal) {
    const int far = size - 1;
    int face, row, column;

    if (normal.y == 1) {
        face = FACE_U; row = position.z; column = position.x;
    } else if (normal.x == 1) {
        face = FACE_R; row = far - position.y; column = far - position.z;
    } else if (normal.z == 1) {
        face = FACE_F; row = far - position.y; column = position.x;
    } else if (normal.y == -1) {
        face = FACE_D; row = far - position.z; column = position.x;
    } else if (normal.x == -1) {
        face = FACE_L; row = far - position.y; column = position.z;
    } else {
        face = FACE_B; row = far - position.y; column = far - position.x;
    }
    return face * size * size + row * size + column;
}

/**
 * Rotate a vector a quarter turn around an axis. The offset is size - 1
 * for a position, 0 for a normal.
 */
static Vector rotate_vector(Vector v, int axis, int direction, int offset) {
    Vector r = v;

    if (axis == 0) {
        r.y = direction == 1 ? offset - v.z : v.z;
        r.z = direction == 1 ? v.y : offset - v.y;
    } else if (axis == 1) {
        r.x = direction == 1 ? offset - v.z : v.z;
        r.z = direction == 1 ? v.x : offset - v.x;
    } else {
        r.x = direction == 1 ? offset - v.y : v.y;
        r.y = direction == 1 ? v.x : offset - v.x;
    }
    return r;
}

/**
 * Compute the permutations of 1, 2 and 3 quarter turns of the layers
 * first to last of a face, into three consecutive blocks of 6 * size^2.
 */
static void build_permutations(int size, int face, int first, int last, uint16_t* permutations) {
    const int count = 6 * size * size;
    const int axis = FACE_AXIS[face];
    const int direction = FACE_DIRECTION[face];
    uint16_t* quarter = permutations;
    uint16_t* half = permutations + count;
    uint16_t* inverse = permutations + 2 * count;

    for (int i = 0; i < count; i++) {
        quarter[i] = (uint16_t)i;
    }

    for (int i = 0; i < count; i++) {
        Vector position, normal;
        facelet_geometry(size, i, &position, &normal);

        const int coordinate = axis == 0 ? position.x : axis == 1 ? position.y : position.z;
        const int layer = FACE_POSITIVE[face] ? size - coordinate : coordinate + 1;
        if (layer < first || layer > last) {
            continue;
        }

        const Vector moved = rotate_vector(position, axis, direction, size - 1);
        const Vector turned = rotate_vector(normal, axis, direction, 0);
        quarter[facelet_index(size, moved, turned)] = (uint16_t)i;
    }

    for (int i = 0; i < count; i++) {
        half[i] = quarter[quarter[i]];
    }
    for (int i = 0; i < count; i++) {
        inverse[i] = half[quarter[i]];
    }
}

/**
 * Gather permutation of a move, from the cache, or computed into scratch
 * (3 * MAX_FACELETS entries) once the cache is full. Returns NULL with an
 * exception set when memory runs out.
 */
static const uint16_t* move_permutation(int size, const Move* move, uint16_t* scratch) {
    uint16_t** slot = &cache[size][move->face][move->first - 1][move->last - 1];
    const size_t count = (size_t)(6 * size * size);
    uint16_t* permutations = *slot;

    if (permutations == NULL) {
        const size_t bytes = 3 * count * sizeof(uint16_t);

        if (cache_bytes + bytes > CACHE_LIMIT) {
            build_permutations(size, move->face, move->first, move->last, scratch);
            permutations = scratch;
        } else {
            permutations = PyMem_RawMalloc(bytes);
            if (permutations == NULL) {
                PyErr_NoMemory();
                return NULL;
            }
            build_permutations(size, move->face, move->first, move->last, permutations);
            cache_bytes += bytes;
            *slot = permutations;
        }
    }
    return permutations + (size_t)(move->turns - 1) * count;
}

/**
 * Apply a gather permutation to facelets stored with a given width.
 */
static void permute(int kind, const void* source, void* target, const uint16_t* permutation, int count) {
    switch (kind) {
        case PyUnicode_1BYTE_KIND: {
            const Py_UCS1* from = source;
            Py_UCS1* to = target;
            for (int i = 0; i < count; i++) to[i] = from[permutation[i]];
            break;
        }
        case PyUnicode_2BYTE_KIND: {
            const Py_UCS2* from = source;
            Py_UCS2* to = target;
            for (int i = 0; i < count; i++) to[i] = from[permutation[i]];
            break;
        }
        default: {
            const Py_UCS4* from = source;
            Py_UCS4* to = target;
            for (int i = 0; i < count; i++) to[i] = from[permutation[i]];
            break;
        }
    }
}

static void invalid_move(const char* text, Py_ssize_t length) {
    char shown[SHOWN_MOVE_LENGTH];
    snprintf(shown, sizeof(shown), "%.*s", (int)(length < SHOWN_MOVE_LENGTH - 1 ? length : SHOWN_MOVE_LENGTH - 1), text);
    PyErr_Format(PyExc_ValueError, "Invalid move: '%s'", shown);
}

static int is_digit(char c) {
    return c >= '0' && c <= '9';
}

static int read_number(const char** cursor, const char* end) {
    int value = 0;
    while (*cursor < end && is_digit(**cursor)) {
        if (value < MAX_LAYER_NUMBER) {
            value = value * 10 + (**cursor - '0');
        }
        (*cursor)++;
    }
    return value < MAX_LAYER_NUMBER ? value : MAX_LAYER_NUMBER;
}

static int face_of(char c) {
    switch (c) {
        case 'U': case 'u': return FACE_U;
        case 'R': case 'r': return FACE_R;
        case 'F': case 'f': return FACE_F;
        case 'D': case 'd': return FACE_D;
        case 'L': case 'l': return FACE_L;
        case 'B': case 'b': return FACE_B;
        default: return -1;
    }
}

/**
 * Parse one move for a cube size. Returns 0, or -1 with an exception set.
 */
static int parse_move(const char* text, Py_ssize_t length, int size, Move* move) {
    const char* cursor = text;
    const char* end = text + length;
    int prefix = 0;  // 0: none, 1: N, 2: N-M
    int first = 0, last = 0;

    if (cursor < end && is_digit(*cursor)) {
        first = read_number(&cursor, end);
        prefix = 1;
        if (cursor < end && *cursor == '-') {
            cursor++;
            if (cursor == end || !is_digit(*cursor)) {
                invalid_move(text, length);
                return -1;
            }
            last = read_number(&cursor, end);
            prefix = 2;
        }
    }

    if (cursor == end) {
        invalid_move(text, length);
        return -1;
    }

    const char base = *cursor++;
    const int face = face_of(base);
    const int is_face = face >= 0;
    int wide = base >= 'a' && base <= 'z' && is_face;

    if (is_face && !wide && cursor < end && *cursor == 'w') {
        wide = 1;
        cursor++;
    }

    int turns = 1;
    if (cursor < end && *cursor == '\'') {
        turns = 3;
        cursor++;
    } else if (cursor < end && *cursor == '2') {
        turns = 2;
        cursor++;
        if (cursor < end && *cursor == '\'') {
            cursor++;
        }
    }

    if (cursor != end || (prefix && !is_face) || (prefix == 2 && !wide)) {
        invalid_move(text, length);
        return -1;
    }

    move->turns = turns;

    if (is_face) {
        if (prefix == 0) {
            first = 1;
            last = wide ? 2 : 1;
        } else if (prefix == 1) {
            last = first;
            if (wide) {
                first = 1;
            }
        }
        if (first < 1 || first > last) {
            invalid_move(text, length);
            return -1;
        }
        if (last > size) {
            PyErr_Format(PyExc_ValueError, "Layer %d exceeds cube size %d",
                         first > size ? first : size + 1, size);
            return -1;
        }
        move->face = face;
        move->first = first;
        move->last = last;
        return 0;
    }

    switch (base) {
        case 'x': move->face = FACE_R; break;
        case 'y': move->face = FACE_U; break;
        case 'z': move->face = FACE_F; break;
        case 'M': move->face = FACE_L; break;
        case 'E': move->face = FACE_D; break;
        case 'S': move->face = FACE_F; break;
        default:
            invalid_move(text, length);
            return -1;
    }

    if (base == 'x' || base == 'y' || base == 'z') {
        move->first = 1;
        move->last = size;
        return 0;
    }

    if (size % 2 == 0) {
        PyErr_Format(PyExc_ValueError,
                     "%c moves are only allowed on odd-sized cubes. "
                     "The current cube is a %dx%dx%d.",
                     base, size, size, size);
        return -1;
    }
    move->first = move->last = size / 2 + 1;
    return 0;
}

/**
 * Unpack (state, moves[, size]) with size also accepted by keyword, and
 * deduce the cube size from the state length. Returns 0, or -1 with an
 * exception set.
 */
static int parse_arguments(const char* name, PyObject* const* args, Py_ssize_t nargs, PyObject* kwnames,
                           PyObject** state, PyObject** moves, int* size) {
    const Py_ssize_t nkwargs = kwnames == NULL ? 0 : PyTuple_GET_SIZE(kwnames);
    PyObject* size_object = NULL;

    if (nargs < 2 || nargs + nkwargs > 3) {
        PyErr_Format(PyExc_TypeError, "%s() takes 2 or 3 arguments", name);
        return -1;
    }
    if (nkwargs == 1) {
        if (!PyUnicode_Check(PyTuple_GET_ITEM(kwnames, 0)) ||
            PyUnicode_CompareWithASCIIString(PyTuple_GET_ITEM(kwnames, 0), "size") != 0) {
            PyErr_Format(PyExc_TypeError, "%s() got an unexpected keyword argument", name);
            return -1;
        }
        size_object = args[nargs];
    } else if (nargs == 3) {
        size_object = args[2];
    }

    *state = args[0];
    *moves = args[1];
    if (!PyUnicode_Check(*state) || !PyUnicode_Check(*moves)) {
        PyErr_Format(PyExc_TypeError, "%s() expects str for the state and the moves", name);
        return -1;
    }

    const Py_ssize_t count = PyUnicode_GET_LENGTH(*state);
    int deduced = 0;
    for (int n = 1; n <= MAX_SIZE + 1; n++) {
        if (6 * (Py_ssize_t)n * n == count) {
            deduced = n;
            break;
        }
    }

    if (size_object != NULL && size_object != Py_None) {
        const long wanted = PyLong_AsLong(size_object);
        if (wanted == -1 && PyErr_Occurred()) {
            return -1;
        }
        if (wanted < MIN_SIZE || wanted > MAX_SIZE) {
            PyErr_Format(PyExc_ValueError, "Cube size must be between %d and %d", MIN_SIZE, MAX_SIZE);
            return -1;
        }
        if (wanted != deduced) {
            PyErr_Format(PyExc_ValueError, "State length %zd doesn't match expected %ld for size %ld",
                         count, 6 * wanted * wanted, wanted);
            return -1;
        }
    }

    if (deduced == 0) {
        PyErr_Format(PyExc_ValueError, "State length %zd is not the one of a cube", count);
        return -1;
    }
    if (deduced < MIN_SIZE || deduced > MAX_SIZE) {
        PyErr_Format(PyExc_ValueError, "Cube size must be between %d and %d", MIN_SIZE, MAX_SIZE);
        return -1;
    }

    *size = deduced;
    return 0;
}

/**
 * Apply the space separated moves of text to state.
 */
static PyObject* rotate(PyObject* state, const char* text, Py_ssize_t length, int size, int single) {
    const int count = 6 * size * size;
    const int kind = PyUnicode_KIND(state);
    const void* source = PyUnicode_DATA(state);
    static uint16_t scratch[3 * MAX_FACELETS];
    Py_UCS4 buffers[2][MAX_FACELETS];
    int current = 0;
    int applied = 0;

    const char* cursor = text;
    const char* end = text + length;

    if (single) {
        Move move;
        if (parse_move(text, length, size, &move) < 0) {
            return NULL;
        }
        const uint16_t* permutation = move_permutation(size, &move, scratch);
        if (permutation == NULL) {
            return NULL;
        }
        permute(kind, source, buffers[0], permutation, count);
        source = buffers[0];
        applied = 1;
    } else {
        while (cursor < end) {
            while (cursor < end && *cursor == ' ') cursor++;
            if (cursor == end) break;

            const char* token = cursor;
            while (cursor < end && *cursor != ' ') cursor++;

            Move move;
            if (parse_move(token, cursor - token, size, &move) < 0) {
                return NULL;
            }
            const uint16_t* permutation = move_permutation(size, &move, scratch);
            if (permutation == NULL) {
                return NULL;
            }
            permute(kind, source, buffers[current], permutation, count);
            source = buffers[current];
            current ^= 1;
            applied = 1;
        }
    }

    if (!applied) {
        return Py_NewRef(state);
    }

    PyObject* result = PyUnicode_New(count, PyUnicode_MAX_CHAR_VALUE(state));
    if (result == NULL) {
        return NULL;
    }
    memcpy(PyUnicode_DATA(result), source, (size_t)count * (size_t)kind);
    return result;
}

static PyObject* rotate_move(PyObject* self, PyObject* const* args, Py_ssize_t nargs, PyObject* kwnames) {
    PyObject* state;
    PyObject* move;
    int size;
    Py_ssize_t length;

    if (parse_arguments("rotate_move", args, nargs, kwnames, &state, &move, &size) < 0) {
        return NULL;
    }
    const char* text = PyUnicode_AsUTF8AndSize(move, &length);
    if (text == NULL) {
        return NULL;
    }
    return rotate(state, text, length, size, 1);
}

static PyObject* rotate_moves(PyObject* self, PyObject* const* args, Py_ssize_t nargs, PyObject* kwnames) {
    PyObject* state;
    PyObject* moves;
    int size;
    Py_ssize_t length;

    if (parse_arguments("rotate_moves", args, nargs, kwnames, &state, &moves, &size) < 0) {
        return NULL;
    }
    const char* text = PyUnicode_AsUTF8AndSize(moves, &length);
    if (text == NULL) {
        return NULL;
    }
    return rotate(state, text, length, size, 0);
}

static PyMethodDef RotateMethods[] = {
    {"rotate_move", (PyCFunction)(void (*)(void))rotate_move, METH_FASTCALL | METH_KEYWORDS,
     "rotate_move(state, move, size=None)\n--\n\n"
     "Apply one move to a cube state.\n\n"
     "The cube size is deduced from the state length; an explicit size\n"
     "must match it. Raises ValueError on an invalid state or move."},
    {"rotate_moves", (PyCFunction)(void (*)(void))rotate_moves, METH_FASTCALL | METH_KEYWORDS,
     "rotate_moves(state, moves, size=None)\n--\n\n"
     "Apply space separated moves to a cube state.\n\n"
     "The cube size is deduced from the state length; an explicit size\n"
     "must match it. Raises ValueError on an invalid state or move."},
    {NULL, NULL, 0, NULL}
};

static struct PyModuleDef rotatemodule = {
    PyModuleDef_HEAD_INIT,
    "rotate",
    "Rotation kernel for NxNxN cubes, by cached facelet permutations",
    -1,
    RotateMethods
};

PyMODINIT_FUNC PyInit_rotate(void) {
    return PyModule_Create(&rotatemodule);
}
