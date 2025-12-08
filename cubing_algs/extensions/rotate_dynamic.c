/**
 * Dynamic cube rotation system for arbitrary cube sizes.
 *
 * This C extension mirrors the Python rotate_dynamic.py implementation,
 * providing size-agnostic rotation for NxNxN cubes using coordinate-based
 * rotation logic.
 *
 * Key features:
 * - Works with any cube size (2x2x2, 3x3x3, ..., NxNxN)
 * - Supports all move types: basic, wide, slice, rotations
 * - Produces identical results to Python implementation
 * - Heavily optimized for maximum performance
 */

#include <Python.h>
#include <stdlib.h>
#include <string.h>
#include <stdio.h>

// Maximum cube size supported (can be increased if needed)
#define MAX_CUBE_SIZE 20
#define MAX_STATE_SIZE (6 * MAX_CUBE_SIZE * MAX_CUBE_SIZE + 1)
#define MAX_COORDS (MAX_CUBE_SIZE * MAX_CUBE_SIZE * MAX_CUBE_SIZE)

// Compiler optimization hints
#ifdef __GNUC__
#define LIKELY(x)       __builtin_expect(!!(x), 1)
#define UNLIKELY(x)     __builtin_expect(!!(x), 0)
#define INLINE          static inline __attribute__((always_inline))
#define RESTRICT        __restrict__
#else
#define LIKELY(x)       (x)
#define UNLIKELY(x)     (x)
#define INLINE          static inline
#define RESTRICT
#endif

// 3D coordinate structure
typedef struct {
    int x, y, z;
} Coord3D;

// Face order: U, R, F, D, L, B
static const char FACE_ORDER[] = "URFBLB";

/**
 * Get 3D coordinates for all facelets on a specific face.
 *
 * Args:
 *     face: Face letter (U, R, F, D, L, B)
 *     size: Cube size
 *     coords: Output array for coordinates
 *
 * Returns:
 *     Number of coordinates generated (should be size*size)
 */
static int get_face_coordinates(char face, int size, Coord3D* coords) {
    int idx = 0;

    switch (face) {
        case 'U':  // Top face: y = size-1
            for (int z = 0; z < size; z++) {
                for (int x = 0; x < size; x++) {
                    coords[idx].x = x;
                    coords[idx].y = size - 1;
                    coords[idx].z = z;
                    idx++;
                }
            }
            break;

        case 'R':  // Right face: x = size-1
            for (int y = size - 1; y >= 0; y--) {
                for (int z = size - 1; z >= 0; z--) {
                    coords[idx].x = size - 1;
                    coords[idx].y = y;
                    coords[idx].z = z;
                    idx++;
                }
            }
            break;

        case 'F':  // Front face: z = size-1
            for (int y = size - 1; y >= 0; y--) {
                for (int x = 0; x < size; x++) {
                    coords[idx].x = x;
                    coords[idx].y = y;
                    coords[idx].z = size - 1;
                    idx++;
                }
            }
            break;

        case 'D':  // Bottom face: y = 0
            for (int z = size - 1; z >= 0; z--) {
                for (int x = 0; x < size; x++) {
                    coords[idx].x = x;
                    coords[idx].y = 0;
                    coords[idx].z = z;
                    idx++;
                }
            }
            break;

        case 'L':  // Left face: x = 0
            for (int y = size - 1; y >= 0; y--) {
                for (int z = 0; z < size; z++) {
                    coords[idx].x = 0;
                    coords[idx].y = y;
                    coords[idx].z = z;
                    idx++;
                }
            }
            break;

        case 'B':  // Back face: z = 0
            for (int y = size - 1; y >= 0; y--) {
                for (int x = size - 1; x >= 0; x--) {
                    coords[idx].x = x;
                    coords[idx].y = y;
                    coords[idx].z = 0;
                    idx++;
                }
            }
            break;
    }

    return idx;
}

/**
 * Build a mapping from 3D coordinates to facelet indices.
 *
 * Returns a hash-like lookup where coord_to_facelet[x][y][z] = facelet_idx
 */
static void build_coord_to_facelet_map(int size, int coord_map[MAX_CUBE_SIZE][MAX_CUBE_SIZE][MAX_CUBE_SIZE]) {
    // Initialize with -1 (invalid)
    for (int x = 0; x < MAX_CUBE_SIZE; x++) {
        for (int y = 0; y < MAX_CUBE_SIZE; y++) {
            for (int z = 0; z < MAX_CUBE_SIZE; z++) {
                coord_map[x][y][z] = -1;
            }
        }
    }

    Coord3D coords[MAX_CUBE_SIZE * MAX_CUBE_SIZE];
    int facelet_idx = 0;

    for (int face_idx = 0; face_idx < 6; face_idx++) {
        char face = FACE_ORDER[face_idx];
        int num_coords = get_face_coordinates(face, size, coords);

        for (int i = 0; i < num_coords; i++) {
            coord_map[coords[i].x][coords[i].y][coords[i].z] = facelet_idx;
            facelet_idx++;
        }
    }
}

/**
 * Rotate a 3D coordinate 90 degrees around an axis.
 *
 * Args:
 *     coord: Input coordinate
 *     axis: Rotation axis (0=x, 1=y, 2=z)
 *     size: Cube size
 *     direction: Rotation direction (1=CW, -1=CCW)
 *
 * Returns:
 *     Rotated coordinate
 */
INLINE Coord3D rotate_coord_90(Coord3D coord, int axis, int size, int direction) {
    Coord3D result;
    const int x = coord.x, y = coord.y, z = coord.z;
    const int size_m1 = size - 1;

    // Use branchless computation where possible
    if (LIKELY(axis == 0)) {  // Rotate around x-axis (L/R moves)
        result.x = x;
        result.y = (direction == 1) ? (size_m1 - z) : z;
        result.z = (direction == 1) ? y : (size_m1 - y);
    } else if (axis == 1) {  // Rotate around y-axis (U/D moves)
        result.x = (direction == 1) ? (size_m1 - z) : z;
        result.y = y;
        result.z = (direction == 1) ? x : (size_m1 - x);
    } else {  // axis == 2, Rotate around z-axis (F/B moves)
        result.x = (direction == 1) ? (size_m1 - y) : y;
        result.y = (direction == 1) ? x : (size_m1 - x);
        result.z = z;
    }

    return result;
}

/**
 * Get which axes a coordinate is on the surface of.
 */
INLINE int get_axes_for_coord(Coord3D coord, int size, int* RESTRICT axes) {
    const int size_m1 = size - 1;
    int count = 0;

    if (coord.x == 0 || coord.x == size_m1) {
        axes[count++] = 0;
    }
    if (coord.y == 0 || coord.y == size_m1) {
        axes[count++] = 1;
    }
    if (coord.z == 0 || coord.z == size_m1) {
        axes[count++] = 2;
    }

    return count;
}

/**
 * Rotate piece orientation axes.
 */
INLINE void rotate_piece_orientation(const int* RESTRICT axes, int num_axes, int rotation_axis, int* RESTRICT result) {
    // Lookup table for axis mapping
    static const int mapping[3][3] = {
        {0, 2, 1},  // x-axis rotation
        {2, 1, 0},  // y-axis rotation
        {1, 0, 2}   // z-axis rotation
    };

    const int* RESTRICT map = mapping[rotation_axis];
    for (int i = 0; i < num_axes; i++) {
        result[i] = map[axes[i]];
    }
}

/**
 * Parse move string to extract layers.
 *
 * Args:
 *     move: Move string (e.g., "R", "2Rw", "3-5Rw'")
 *     base_move: Output base move character
 *     layers: Output array of layer indices
 *     num_rotations: Output number of 90-degree rotations
 *     counter_clockwise: Output whether move is counter-clockwise
 *
 * Returns:
 *     Number of layers, or -1 on error
 */
static int parse_move(const char* move, char* base_move, int* layers, int* num_rotations, int* counter_clockwise) {
    *counter_clockwise = 0;
    *num_rotations = 1;
    int num_layers = 0;
    int is_wide = 0;

    const char* p = move;

    // Check for number prefix (e.g., "2Rw", "3-5Rw")
    int layer_count = 0;
    int range_start = 0, range_end = 0;

    if (*p >= '0' && *p <= '9') {
        range_start = *p - '0';
        p++;

        if (*p == '-') {  // Range notation (3-5Rw)
            p++;
            if (*p < '0' || *p > '9') return -1;
            range_end = *p - '0';
            p++;
            layer_count = -1;  // Mark as range
        } else {
            layer_count = range_start;  // Number of layers
        }
    }

    // Get base move
    if (*p == '\0') return -1;
    *base_move = *p;
    p++;

    // Check for wide notation
    if (*p == 'w') {
        is_wide = 1;
        p++;
    }

    // Determine layers based on notation
    if (is_wide) {
        if (layer_count == -1) {
            // Range notation (e.g., "3-5Rw"): layers from range_start-1 to range_end-1
            for (int i = range_start - 1; i < range_end; i++) {
                layers[num_layers++] = i;
            }
        } else if (layer_count > 0) {
            // Number prefix (e.g., "3Rw"): first N layers (0 to layer_count-1)
            for (int i = 0; i < layer_count; i++) {
                layers[num_layers++] = i;
            }
        } else {
            // No prefix, just "Rw": default to first 2 layers
            layers[0] = 0;
            layers[1] = 1;
            num_layers = 2;
        }
    } else {
        // Non-wide move
        if (layer_count > 0) {
            // Number prefix without 'w' (e.g., "2F"): single layer at index layer_count-1
            layers[0] = layer_count - 1;
            num_layers = 1;
        } else {
            // No prefix, just move letter: outermost layer (0)
            layers[0] = 0;
            num_layers = 1;
        }
    }

    // Check for modifiers
    if (*p == '\'') {
        *counter_clockwise = 1;
        p++;
    } else if (*p == '2') {
        *num_rotations = 2;
        p++;
    }

    // Should be end of string
    if (*p != '\0') return -1;

    return num_layers;
}

/**
 * Get axis and direction for a move type using lookup table.
 */
INLINE void get_move_axis_and_direction(char move_type, int* RESTRICT axis, int* RESTRICT direction) {
    // Lookup table indexed by character value for common moves
    // This is faster than a switch statement for the hot path
    // Initialize with {-1, 0} for invalid moves, then set valid ones
    static const struct {
        int axis;
        int direction;
    } move_table[256] = {
        ['R'] = {0, -1}, ['L'] = {0, 1},  ['x'] = {0, -1}, ['M'] = {0, 1},
        ['U'] = {1, 1},  ['D'] = {1, -1}, ['y'] = {1, 1},  ['E'] = {1, -1},
        ['F'] = {2, -1}, ['B'] = {2, 1},  ['z'] = {2, -1}, ['S'] = {2, -1}
    };

    // Valid move characters for quick check
    static const char valid_moves[] = "RLxMUDyEFBzS";
    int is_valid = 0;
    for (int i = 0; valid_moves[i] != '\0'; i++) {
        if (move_type == valid_moves[i]) {
            is_valid = 1;
            break;
        }
    }

    if (LIKELY(is_valid)) {
        *axis = move_table[(unsigned char)move_type].axis;
        *direction = move_table[(unsigned char)move_type].direction;
    } else {
        *axis = -1;
        *direction = 0;
    }
}

/**
 * Get coordinates affected by a move.
 */
static int get_affected_coords(char move_type, int size, int* layers, int num_layers, Coord3D* coords) {
    int count = 0;

    // For rotation moves (x, y, z), affect entire cube
    if (move_type == 'x' || move_type == 'y' || move_type == 'z') {
        for (int x = 0; x < size; x++) {
            for (int y = 0; y < size; y++) {
                for (int z = 0; z < size; z++) {
                    coords[count].x = x;
                    coords[count].y = y;
                    coords[count].z = z;
                    count++;
                }
            }
        }
        return count;
    }

    // For slice moves, use middle layer
    if (move_type == 'M' || move_type == 'E' || move_type == 'S') {
        if (size % 2 == 0) {
            // Error: slice moves only work on odd cubes
            return -1;
        }

        int mid = size / 2;

        if (move_type == 'M') {
            for (int y = 0; y < size; y++) {
                for (int z = 0; z < size; z++) {
                    coords[count].x = mid;
                    coords[count].y = y;
                    coords[count].z = z;
                    count++;
                }
            }
        } else if (move_type == 'E') {
            for (int x = 0; x < size; x++) {
                for (int z = 0; z < size; z++) {
                    coords[count].x = x;
                    coords[count].y = mid;
                    coords[count].z = z;
                    count++;
                }
            }
        } else {  // S
            for (int x = 0; x < size; x++) {
                for (int y = 0; y < size; y++) {
                    coords[count].x = x;
                    coords[count].y = y;
                    coords[count].z = mid;
                    count++;
                }
            }
        }
        return count;
    }

    // For face moves, affect specified layers
    for (int layer_idx = 0; layer_idx < num_layers; layer_idx++) {
        int layer = layers[layer_idx];
        int coord_val;

        switch (move_type) {
            case 'R':
                coord_val = size - 1 - layer;
                for (int y = 0; y < size; y++) {
                    for (int z = 0; z < size; z++) {
                        coords[count].x = coord_val;
                        coords[count].y = y;
                        coords[count].z = z;
                        count++;
                    }
                }
                break;

            case 'L':
                coord_val = layer;
                for (int y = 0; y < size; y++) {
                    for (int z = 0; z < size; z++) {
                        coords[count].x = coord_val;
                        coords[count].y = y;
                        coords[count].z = z;
                        count++;
                    }
                }
                break;

            case 'U':
                coord_val = size - 1 - layer;
                for (int x = 0; x < size; x++) {
                    for (int z = 0; z < size; z++) {
                        coords[count].x = x;
                        coords[count].y = coord_val;
                        coords[count].z = z;
                        count++;
                    }
                }
                break;

            case 'D':
                coord_val = layer;
                for (int x = 0; x < size; x++) {
                    for (int z = 0; z < size; z++) {
                        coords[count].x = x;
                        coords[count].y = coord_val;
                        coords[count].z = z;
                        count++;
                    }
                }
                break;

            case 'F':
                coord_val = size - 1 - layer;
                for (int x = 0; x < size; x++) {
                    for (int y = 0; y < size; y++) {
                        coords[count].x = x;
                        coords[count].y = y;
                        coords[count].z = coord_val;
                        count++;
                    }
                }
                break;

            case 'B':
                coord_val = layer;
                for (int x = 0; x < size; x++) {
                    for (int y = 0; y < size; y++) {
                        coords[count].x = x;
                        coords[count].y = y;
                        coords[count].z = coord_val;
                        count++;
                    }
                }
                break;
        }
    }

    return count;
}

/**
 * Build coord to facelets mapping (with axes).
 * Each coordinate can have 1-3 facelets on it (corner=3, edge=2, center=1).
 */
typedef struct {
    int facelet_idx;
    int axis;
} FaceletInfo;

typedef struct {
    FaceletInfo facelets[3];  // Max 3 facelets per coord (corners)
    int count;
} CoordFacelets;

static void build_coord_to_facelets_map(int size, CoordFacelets coord_facelets[MAX_CUBE_SIZE][MAX_CUBE_SIZE][MAX_CUBE_SIZE]) {
    // Initialize
    for (int x = 0; x < MAX_CUBE_SIZE; x++) {
        for (int y = 0; y < MAX_CUBE_SIZE; y++) {
            for (int z = 0; z < MAX_CUBE_SIZE; z++) {
                coord_facelets[x][y][z].count = 0;
            }
        }
    }

    Coord3D coords[MAX_CUBE_SIZE * MAX_CUBE_SIZE];
    int facelet_idx = 0;

    const char faces[] = {'U', 'R', 'F', 'D', 'L', 'B'};

    for (int face_idx = 0; face_idx < 6; face_idx++) {
        char face = faces[face_idx];
        int num_coords = get_face_coordinates(face, size, coords);

        // Determine face axis
        int face_axis;
        if (face == 'U' || face == 'D') face_axis = 1;
        else if (face == 'R' || face == 'L') face_axis = 0;
        else face_axis = 2;  // F or B

        for (int i = 0; i < num_coords; i++) {
            int x = coords[i].x, y = coords[i].y, z = coords[i].z;
            int idx = coord_facelets[x][y][z].count;

            coord_facelets[x][y][z].facelets[idx].facelet_idx = facelet_idx;
            coord_facelets[x][y][z].facelets[idx].axis = face_axis;
            coord_facelets[x][y][z].count++;

            facelet_idx++;
        }
    }
}

/**
 * Main rotate_move function.
 */
static PyObject* rotate_move(PyObject* self, PyObject* args, PyObject* kwargs) {
    const char* state;
    const char* move;
    int size = 3;  // Default size

    static char* kwlist[] = {"state", "move", "size", NULL};

    if (!PyArg_ParseTupleAndKeywords(args, kwargs, "ss|i", kwlist, &state, &move, &size)) {
        return NULL;
    }

    // Validate size
    if (size < 2 || size > MAX_CUBE_SIZE) {
        PyErr_Format(PyExc_ValueError, "Cube size must be between 2 and %d", MAX_CUBE_SIZE);
        return NULL;
    }

    int state_len = strlen(state);
    int expected_len = 6 * size * size;
    if (state_len != expected_len) {
        PyErr_Format(PyExc_ValueError, "State length %d doesn't match expected %d for size %d",
                     state_len, expected_len, size);
        return NULL;
    }

    // Parse move
    char base_move;
    int layers[MAX_CUBE_SIZE];
    int num_rotations, counter_clockwise;
    int num_layers = parse_move(move, &base_move, layers, &num_rotations, &counter_clockwise);

    if (num_layers < 0) {
        PyErr_Format(PyExc_ValueError, "Invalid move: %s", move);
        return NULL;
    }

    // Validate layers don't exceed size
    for (int i = 0; i < num_layers; i++) {
        if (layers[i] >= size) {
            PyErr_Format(PyExc_ValueError, "Layer %d exceeds cube size %d", layers[i] + 1, size);
            return NULL;
        }
    }

    // Get axis and direction
    int axis, base_direction;
    get_move_axis_and_direction(base_move, &axis, &base_direction);

    if (axis < 0) {
        PyErr_Format(PyExc_ValueError, "Unsupported move type: %c", base_move);
        return NULL;
    }

    if (counter_clockwise) {
        base_direction *= -1;
    }

    // Get affected coordinates
    Coord3D affected_coords[MAX_COORDS];
    int num_affected = get_affected_coords(base_move, size, layers, num_layers, affected_coords);

    if (num_affected < 0) {
        PyErr_Format(PyExc_ValueError, "%c moves are only allowed on odd-sized cubes. Current cube size is %dx%dx%d.",
                     base_move, size, size, size);
        return NULL;
    }

    // Build coordinate mappings
    CoordFacelets coord_facelets[MAX_CUBE_SIZE][MAX_CUBE_SIZE][MAX_CUBE_SIZE];
    build_coord_to_facelets_map(size, coord_facelets);

    // Initialize permutation (identity) - optimized
    const int total_facelets = 6 * size * size;
    int permutation[MAX_STATE_SIZE];

    // Unrolled loop for common sizes
    if (LIKELY(total_facelets == 54)) {  // 3x3x3
        for (int i = 0; i < 54; i += 6) {
            permutation[i] = i;
            permutation[i+1] = i+1;
            permutation[i+2] = i+2;
            permutation[i+3] = i+3;
            permutation[i+4] = i+4;
            permutation[i+5] = i+5;
        }
    } else if (total_facelets == 24) {  // 2x2x2
        for (int i = 0; i < 24; i += 4) {
            permutation[i] = i;
            permutation[i+1] = i+1;
            permutation[i+2] = i+2;
            permutation[i+3] = i+3;
        }
    } else {
        // Generic case
        for (int i = 0; i < total_facelets; i++) {
            permutation[i] = i;
        }
    }

    // Apply rotations
    for (int rot = 0; rot < num_rotations; rot++) {
        int temp_perm[MAX_STATE_SIZE];

        // Initialize identity permutation - optimized for common sizes
        if (LIKELY(total_facelets == 54)) {  // 3x3x3
            for (int i = 0; i < 54; i += 6) {
                temp_perm[i] = i;
                temp_perm[i+1] = i+1;
                temp_perm[i+2] = i+2;
                temp_perm[i+3] = i+3;
                temp_perm[i+4] = i+4;
                temp_perm[i+5] = i+5;
            }
        } else if (total_facelets == 24) {  // 2x2x2
            for (int i = 0; i < 24; i += 4) {
                temp_perm[i] = i;
                temp_perm[i+1] = i+1;
                temp_perm[i+2] = i+2;
                temp_perm[i+3] = i+3;
            }
        } else {
            for (int i = 0; i < total_facelets; i++) {
                temp_perm[i] = i;
            }
        }

        // Rotate each affected coordinate
        for (int i = 0; i < num_affected; i++) {
            const Coord3D orig = affected_coords[i];
            const Coord3D rotated = rotate_coord_90(orig, axis, size, base_direction);

            CoordFacelets* RESTRICT orig_cf = &coord_facelets[orig.x][orig.y][orig.z];
            CoordFacelets* RESTRICT new_cf = &coord_facelets[rotated.x][rotated.y][rotated.z];

            const int num_axes = orig_cf->count;
            if (UNLIKELY(num_axes != new_cf->count)) continue;

            // Get original axes
            int orig_axes[3];
            for (int j = 0; j < num_axes; j++) {
                orig_axes[j] = orig_cf->facelets[j].axis;
            }

            // Rotate axes
            int rotated_axes[3];
            rotate_piece_orientation(orig_axes, num_axes, axis, rotated_axes);

            // Map facelets - optimized for common cases (1-3 facelets)
            if (LIKELY(num_axes == 2)) {
                // Edge piece (most common case for 3x3x3)
                const int orig_idx0 = orig_cf->facelets[0].facelet_idx;
                const int orig_idx1 = orig_cf->facelets[1].facelet_idx;
                const int target_axis0 = rotated_axes[0];
                const int target_axis1 = rotated_axes[1];

                if (new_cf->facelets[0].axis == target_axis0) {
                    temp_perm[orig_idx0] = new_cf->facelets[0].facelet_idx;
                    temp_perm[orig_idx1] = new_cf->facelets[1].facelet_idx;
                } else {
                    temp_perm[orig_idx0] = new_cf->facelets[1].facelet_idx;
                    temp_perm[orig_idx1] = new_cf->facelets[0].facelet_idx;
                }
            } else {
                // Corner (3) or center (1) - less common
                for (int j = 0; j < num_axes; j++) {
                    const int orig_idx = orig_cf->facelets[j].facelet_idx;
                    const int target_axis = rotated_axes[j];

                    // Find matching axis in new position
                    for (int k = 0; k < num_axes; k++) {
                        if (new_cf->facelets[k].axis == target_axis) {
                            temp_perm[orig_idx] = new_cf->facelets[k].facelet_idx;
                            break;
                        }
                    }
                }
            }
        }

        // Compose permutations - use direct assignment for better performance
        int composed[MAX_STATE_SIZE];
        const int* RESTRICT perm_read = permutation;
        const int* RESTRICT temp_read = temp_perm;
        int* RESTRICT comp_write = composed;

        for (int i = 0; i < total_facelets; i++) {
            comp_write[i] = temp_read[perm_read[i]];
        }
        memcpy(permutation, composed, total_facelets * sizeof(int));
    }

    // Apply permutation to state - optimized with restrict pointers
    char new_state[MAX_STATE_SIZE];
    const char* RESTRICT state_read = state;
    char* RESTRICT new_state_write = new_state;
    const int* RESTRICT perm_read = permutation;

    for (int i = 0; i < total_facelets; i++) {
        new_state_write[perm_read[i]] = state_read[i];
    }
    new_state_write[total_facelets] = '\0';

    return PyUnicode_FromString(new_state);
}

// Method definitions
static PyMethodDef RotateDynamicMethods[] = {
    {"rotate_move", (PyCFunction)rotate_move, METH_VARARGS | METH_KEYWORDS,
     "Apply a move to a cube state.\n\n"
     "Args:\n"
     "    state: Current cube state as facelet string\n"
     "    move: Move to apply (e.g., 'R', \"U'\", 'F2', '2Rw')\n"
     "    size: Size of the cube (default 3)\n\n"
     "Returns:\n"
     "    New cube state after applying the move"},
    {NULL, NULL, 0, NULL}
};

// Module definition
static struct PyModuleDef rotatedynamicmodule = {
    PyModuleDef_HEAD_INIT,
    "rotate_dynamic",
    "Dynamic cube rotation system for arbitrary cube sizes",
    -1,
    RotateDynamicMethods
};

// Module initialization
PyMODINIT_FUNC PyInit_rotate_dynamic(void) {
    return PyModule_Create(&rotatedynamicmodule);
}
