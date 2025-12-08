#include <Python.h>
#include <string.h>

// Main function for rotating a move on 2x2x2 cube
static PyObject* rotate_move(PyObject* self, PyObject* args) {
    const char* state;
    const char* move;

    if (!PyArg_ParseTuple(args, "ss", &state, &move)) {
        return NULL;
    }

    // Copy state for modification (2x2x2 has 25 chars including null terminator)
    char new_state[25];
    strcpy(new_state, state);

    char temp_state[25];
    strcpy(temp_state, new_state);

    // Parse the move - optimized for speed
    char face = move[0];
    int direction = 1; // Default: clockwise

    // Fast path: check second character directly without strlen calls
    char second = move[1];
    if (second == 'w') {
        // Handle wide moves: convert valid face letters to lowercase
        switch (face) {
            case 'R': face = 'r'; break;
            case 'L': face = 'l'; break;
            case 'U': face = 'u'; break;
            case 'D': face = 'd'; break;
            case 'F': face = 'f'; break;
            case 'B': face = 'b'; break;
        }

        // Check third character for modifiers
        char third = move[2];
        if (third == '\'') {
            direction = 3; // Anticlockwise
        } else if (third == '2') {
            direction = 2; // 180°
        } else if (third != '\0') {
            PyErr_Format(PyExc_ValueError, "Invalid move modifier: '%c'", third);
            return NULL;
        }
    } else if (second == '\'') {
        direction = 3; // Anticlockwise
    } else if (second == '2') {
        direction = 2; // 180°
    } else if (second != '\0') {
        PyErr_Format(PyExc_ValueError, "Invalid move modifier: '%c'", second);
        return NULL;
    }

    switch (face) {
        case 'U': {
            if (direction == 1) {
                // Face U rotation clockwise
                new_state[0] = temp_state[2];   // U[2] -> U[0]
                new_state[1] = temp_state[0];   // U[0] -> U[1]
                new_state[2] = temp_state[3];   // U[3] -> U[2]
                new_state[3] = temp_state[1];   // U[1] -> U[3]

                // Top row rotation (clockwise: R<-B, F<-R, L<-F, B<-L)
                new_state[4] = temp_state[20];  // B[0] -> R[0]
                new_state[5] = temp_state[21];  // B[1] -> R[1]
                new_state[8] = temp_state[4];   // R[0] -> F[0]
                new_state[9] = temp_state[5];   // R[1] -> F[1]
                new_state[16] = temp_state[8];  // F[0] -> L[0]
                new_state[17] = temp_state[9];  // F[1] -> L[1]
                new_state[20] = temp_state[16]; // L[0] -> B[0]
                new_state[21] = temp_state[17]; // L[1] -> B[1]
            } else if (direction == 2) {
                // Face U rotation 180°
                new_state[0] = temp_state[3];   // U[3] -> U[0]
                new_state[1] = temp_state[2];   // U[2] -> U[1]
                new_state[2] = temp_state[1];   // U[1] -> U[2]
                new_state[3] = temp_state[0];   // U[0] -> U[3]

                // 180° top row rotation (R<-L, F<-B, L<-R, B<-F)
                new_state[4] = temp_state[16];  // L[0] -> R[0]
                new_state[5] = temp_state[17];  // L[1] -> R[1]
                new_state[8] = temp_state[20];  // B[0] -> F[0]
                new_state[9] = temp_state[21];  // B[1] -> F[1]
                new_state[16] = temp_state[4];  // R[0] -> L[0]
                new_state[17] = temp_state[5];  // R[1] -> L[1]
                new_state[20] = temp_state[8];  // F[0] -> B[0]
                new_state[21] = temp_state[9];  // F[1] -> B[1]
            } else {
                // Face U rotation counterclockwise
                new_state[0] = temp_state[1];   // U[1] -> U[0]
                new_state[1] = temp_state[3];   // U[3] -> U[1]
                new_state[2] = temp_state[0];   // U[0] -> U[2]
                new_state[3] = temp_state[2];   // U[2] -> U[3]

                // Top row rotation (counterclockwise: R<-F, F<-L, L<-B, B<-R)
                new_state[4] = temp_state[8];   // F[0] -> R[0]
                new_state[5] = temp_state[9];   // F[1] -> R[1]
                new_state[8] = temp_state[16];  // L[0] -> F[0]
                new_state[9] = temp_state[17];  // L[1] -> F[1]
                new_state[16] = temp_state[20]; // B[0] -> L[0]
                new_state[17] = temp_state[21]; // B[1] -> L[1]
                new_state[20] = temp_state[4];  // R[0] -> B[0]
                new_state[21] = temp_state[5];  // R[1] -> B[1]
            }
            break;
        }

        case 'R': {
            if (direction == 1) {
                // Face R rotation clockwise
                new_state[4] = temp_state[6];   // R[2] -> R[0]
                new_state[5] = temp_state[4];   // R[0] -> R[1]
                new_state[6] = temp_state[7];   // R[3] -> R[2]
                new_state[7] = temp_state[5];   // R[1] -> R[3]

                // Right column rotation (clockwise: U<-F, F<-D, D<-B, B<-U)
                new_state[1] = temp_state[9];   // F[1] -> U[1]
                new_state[3] = temp_state[11];  // F[3] -> U[3]
                new_state[9] = temp_state[13];  // D[1] -> F[1]
                new_state[11] = temp_state[15]; // D[3] -> F[3]
                new_state[13] = temp_state[22]; // B[2] -> D[1]
                new_state[15] = temp_state[20]; // B[0] -> D[3]
                new_state[20] = temp_state[3];  // U[3] -> B[0]
                new_state[22] = temp_state[1];  // U[1] -> B[2]
            } else if (direction == 2) {
                // Face R rotation 180°
                new_state[4] = temp_state[7];   // R[3] -> R[0]
                new_state[5] = temp_state[6];   // R[2] -> R[1]
                new_state[6] = temp_state[5];   // R[1] -> R[2]
                new_state[7] = temp_state[4];   // R[0] -> R[3]

                // 180° right column rotation (U<-D, F<-B, D<-U, B<-F)
                new_state[1] = temp_state[13];  // D[1] -> U[1]
                new_state[3] = temp_state[15];  // D[3] -> U[3]
                new_state[9] = temp_state[22];  // B[2] -> F[1]
                new_state[11] = temp_state[20]; // B[0] -> F[3]
                new_state[13] = temp_state[1];  // U[1] -> D[1]
                new_state[15] = temp_state[3];  // U[3] -> D[3]
                new_state[20] = temp_state[11]; // F[3] -> B[0]
                new_state[22] = temp_state[9];  // F[1] -> B[2]
            } else {
                // Face R rotation counterclockwise
                new_state[4] = temp_state[5];   // R[1] -> R[0]
                new_state[5] = temp_state[7];   // R[3] -> R[1]
                new_state[6] = temp_state[4];   // R[0] -> R[2]
                new_state[7] = temp_state[6];   // R[2] -> R[3]

                // Right column rotation (counterclockwise: U<-B, F<-U, D<-F, B<-D)
                new_state[1] = temp_state[22];  // B[2] -> U[1]
                new_state[3] = temp_state[20];  // B[0] -> U[3]
                new_state[9] = temp_state[1];   // U[1] -> F[1]
                new_state[11] = temp_state[3];  // U[3] -> F[3]
                new_state[13] = temp_state[9];  // F[1] -> D[1]
                new_state[15] = temp_state[11]; // F[3] -> D[3]
                new_state[20] = temp_state[15]; // D[3] -> B[0]
                new_state[22] = temp_state[13]; // D[1] -> B[2]
            }
            break;
        }

        case 'F': {
            if (direction == 1) {
                // Face F rotation clockwise
                new_state[8] = temp_state[10];  // F[2] -> F[0]
                new_state[9] = temp_state[8];   // F[0] -> F[1]
                new_state[10] = temp_state[11]; // F[3] -> F[2]
                new_state[11] = temp_state[9];  // F[1] -> F[3]

                // Front edge rotation (clockwise: U<-L, R<-U, D<-R, L<-D)
                new_state[2] = temp_state[19];  // L[3] -> U[2]
                new_state[3] = temp_state[17];  // L[1] -> U[3]
                new_state[4] = temp_state[2];   // U[2] -> R[0]
                new_state[6] = temp_state[3];   // U[3] -> R[2]
                new_state[12] = temp_state[6];  // R[2] -> D[0]
                new_state[13] = temp_state[4];  // R[0] -> D[1]
                new_state[17] = temp_state[12]; // D[0] -> L[1]
                new_state[19] = temp_state[13]; // D[1] -> L[3]
            } else if (direction == 2) {
                // Face F rotation 180°
                new_state[8] = temp_state[11];  // F[3] -> F[0]
                new_state[9] = temp_state[10];  // F[2] -> F[1]
                new_state[10] = temp_state[9];  // F[1] -> F[2]
                new_state[11] = temp_state[8];  // F[0] -> F[3]

                // 180° front edge rotation (U<-D, R<-L, D<-U, L<-R)
                new_state[2] = temp_state[12];  // D[0] -> U[2]
                new_state[3] = temp_state[13];  // D[1] -> U[3]
                new_state[4] = temp_state[19];  // L[3] -> R[0]
                new_state[6] = temp_state[17];  // L[1] -> R[2]
                new_state[12] = temp_state[2];  // U[2] -> D[0]
                new_state[13] = temp_state[3];  // U[3] -> D[1]
                new_state[17] = temp_state[6];  // R[2] -> L[1]
                new_state[19] = temp_state[4];  // R[0] -> L[3]
            } else {
                // Face F rotation counterclockwise
                new_state[8] = temp_state[9];   // F[1] -> F[0]
                new_state[9] = temp_state[11];  // F[3] -> F[1]
                new_state[10] = temp_state[8];  // F[0] -> F[2]
                new_state[11] = temp_state[10]; // F[2] -> F[3]

                // Front edge rotation (counterclockwise: U<-R, R<-D, D<-L, L<-U)
                new_state[2] = temp_state[4];   // R[0] -> U[2]
                new_state[3] = temp_state[6];   // R[2] -> U[3]
                new_state[4] = temp_state[13];  // D[1] -> R[0]
                new_state[6] = temp_state[12];  // D[0] -> R[2]
                new_state[12] = temp_state[19]; // L[3] -> D[0]
                new_state[13] = temp_state[17]; // L[1] -> D[1]
                new_state[17] = temp_state[3];  // U[3] -> L[1]
                new_state[19] = temp_state[2];  // U[2] -> L[3]
            }
            break;
        }

        case 'D': {
            if (direction == 1) {
                // Face D rotation clockwise
                new_state[12] = temp_state[14]; // D[2] -> D[0]
                new_state[13] = temp_state[12]; // D[0] -> D[1]
                new_state[14] = temp_state[15]; // D[3] -> D[2]
                new_state[15] = temp_state[13]; // D[1] -> D[3]

                // Bottom row rotation (clockwise: F<-R, L<-F, B<-L, R<-B)
                new_state[6] = temp_state[10];  // F[2] -> R[2]
                new_state[7] = temp_state[11];  // F[3] -> R[3]
                new_state[10] = temp_state[18]; // L[2] -> F[2]
                new_state[11] = temp_state[19]; // L[3] -> F[3]
                new_state[18] = temp_state[22]; // B[2] -> L[2]
                new_state[19] = temp_state[23]; // B[3] -> L[3]
                new_state[22] = temp_state[6];  // R[2] -> B[2]
                new_state[23] = temp_state[7];  // R[3] -> B[3]
            } else if (direction == 2) {
                // Face D rotation 180°
                new_state[12] = temp_state[15]; // D[3] -> D[0]
                new_state[13] = temp_state[14]; // D[2] -> D[1]
                new_state[14] = temp_state[13]; // D[1] -> D[2]
                new_state[15] = temp_state[12]; // D[0] -> D[3]

                // 180° bottom row rotation (F<-B, L<-R, B<-F, R<-L)
                new_state[6] = temp_state[22];  // B[2] -> R[2]
                new_state[7] = temp_state[23];  // B[3] -> R[3]
                new_state[10] = temp_state[6];  // R[2] -> F[2]
                new_state[11] = temp_state[7];  // R[3] -> F[3]
                new_state[18] = temp_state[10]; // F[2] -> L[2]
                new_state[19] = temp_state[11]; // F[3] -> L[3]
                new_state[22] = temp_state[18]; // L[2] -> B[2]
                new_state[23] = temp_state[19]; // L[3] -> B[3]
            } else {
                // Face D rotation counterclockwise
                new_state[12] = temp_state[13]; // D[1] -> D[0]
                new_state[13] = temp_state[15]; // D[3] -> D[1]
                new_state[14] = temp_state[12]; // D[0] -> D[2]
                new_state[15] = temp_state[14]; // D[2] -> D[3]

                // Bottom row rotation (counterclockwise: F<-L, L<-B, B<-R, R<-F)
                new_state[6] = temp_state[22];  // B[2] -> R[2]
                new_state[7] = temp_state[23];  // B[3] -> R[3]
                new_state[10] = temp_state[6];  // R[2] -> F[2]
                new_state[11] = temp_state[7];  // R[3] -> F[3]
                new_state[18] = temp_state[10]; // F[2] -> L[2]
                new_state[19] = temp_state[11]; // F[3] -> L[3]
                new_state[22] = temp_state[18]; // L[2] -> B[2]
                new_state[23] = temp_state[19]; // L[3] -> B[3]
            }
            break;
        }

        case 'L': {
            if (direction == 1) {
                // Face L rotation clockwise
                new_state[16] = temp_state[18]; // L[2] -> L[0]
                new_state[17] = temp_state[16]; // L[0] -> L[1]
                new_state[18] = temp_state[19]; // L[3] -> L[2]
                new_state[19] = temp_state[17]; // L[1] -> L[3]

                // Left column rotation (clockwise: U<-B, F<-U, D<-F, B<-D)
                new_state[0] = temp_state[23];  // B[3] -> U[0]
                new_state[2] = temp_state[21];  // B[1] -> U[2]
                new_state[8] = temp_state[0];   // U[0] -> F[0]
                new_state[10] = temp_state[2];  // U[2] -> F[2]
                new_state[12] = temp_state[8];  // F[0] -> D[0]
                new_state[14] = temp_state[10]; // F[2] -> D[2]
                new_state[21] = temp_state[14]; // D[2] -> B[1]
                new_state[23] = temp_state[12]; // D[0] -> B[3]
            } else if (direction == 2) {
                // Face L rotation 180°
                new_state[16] = temp_state[19]; // L[3] -> L[0]
                new_state[17] = temp_state[18]; // L[2] -> L[1]
                new_state[18] = temp_state[17]; // L[1] -> L[2]
                new_state[19] = temp_state[16]; // L[0] -> L[3]

                // 180° left column rotation (U<-D, F<-B, D<-U, B<-F)
                new_state[0] = temp_state[12];  // D[0] -> U[0]
                new_state[2] = temp_state[14];  // D[2] -> U[2]
                new_state[8] = temp_state[23];  // B[3] -> F[0]
                new_state[10] = temp_state[21]; // B[1] -> F[2]
                new_state[12] = temp_state[0];  // U[0] -> D[0]
                new_state[14] = temp_state[2];  // U[2] -> D[2]
                new_state[21] = temp_state[10]; // F[2] -> B[1]
                new_state[23] = temp_state[8];  // F[0] -> B[3]
            } else {
                // Face L rotation counterclockwise
                new_state[16] = temp_state[17]; // L[1] -> L[0]
                new_state[17] = temp_state[19]; // L[3] -> L[1]
                new_state[18] = temp_state[16]; // L[0] -> L[2]
                new_state[19] = temp_state[18]; // L[2] -> L[3]

                // Left column rotation (counterclockwise: U<-F, F<-D, D<-B, B<-U)
                new_state[0] = temp_state[8];   // F[0] -> U[0]
                new_state[2] = temp_state[10];  // F[2] -> U[2]
                new_state[8] = temp_state[12];  // D[0] -> F[0]
                new_state[10] = temp_state[14]; // D[2] -> F[2]
                new_state[12] = temp_state[23]; // B[3] -> D[0]
                new_state[14] = temp_state[21]; // B[1] -> D[2]
                new_state[21] = temp_state[2];  // U[2] -> B[1]
                new_state[23] = temp_state[0];  // U[0] -> B[3]
            }
            break;
        }

        case 'B': {
            if (direction == 1) {
                // Face B rotation clockwise
                new_state[20] = temp_state[22]; // B[2] -> B[0]
                new_state[21] = temp_state[20]; // B[0] -> B[1]
                new_state[22] = temp_state[23]; // B[3] -> B[2]
                new_state[23] = temp_state[21]; // B[1] -> B[3]

                // Back edge rotation (clockwise: U<-R, R<-D, D<-L, L<-U)
                new_state[0] = temp_state[5];   // R[1] -> U[0]
                new_state[1] = temp_state[7];   // R[3] -> U[1]
                new_state[5] = temp_state[15];  // D[3] -> R[1]
                new_state[7] = temp_state[14];  // D[2] -> R[3]
                new_state[14] = temp_state[16]; // L[0] -> D[2]
                new_state[15] = temp_state[18]; // L[2] -> D[3]
                new_state[16] = temp_state[1];  // U[1] -> L[0]
                new_state[18] = temp_state[0];  // U[0] -> L[2]
            } else if (direction == 2) {
                // Face B rotation 180°
                new_state[20] = temp_state[23]; // B[3] -> B[0]
                new_state[21] = temp_state[22]; // B[2] -> B[1]
                new_state[22] = temp_state[21]; // B[1] -> B[2]
                new_state[23] = temp_state[20]; // B[0] -> B[3]

                // 180° back edge rotation (U<-D, R<-L, D<-U, L<-R)
                new_state[0] = temp_state[14];  // D[2] -> U[0]
                new_state[1] = temp_state[15];  // D[3] -> U[1]
                new_state[5] = temp_state[18];  // L[2] -> R[1]
                new_state[7] = temp_state[16];  // L[0] -> R[3]
                new_state[14] = temp_state[0];  // U[0] -> D[2]
                new_state[15] = temp_state[1];  // U[1] -> D[3]
                new_state[16] = temp_state[7];  // R[3] -> L[0]
                new_state[18] = temp_state[5];  // R[1] -> L[2]
            } else {
                // Face B rotation counterclockwise
                new_state[20] = temp_state[21]; // B[1] -> B[0]
                new_state[21] = temp_state[23]; // B[3] -> B[1]
                new_state[22] = temp_state[20]; // B[0] -> B[2]
                new_state[23] = temp_state[22]; // B[2] -> B[3]

                // Back edge rotation (counterclockwise: U<-L, R<-U, D<-R, L<-D)
                new_state[0] = temp_state[18];  // L[2] -> U[0]
                new_state[1] = temp_state[16];  // L[0] -> U[1]
                new_state[5] = temp_state[0];   // U[0] -> R[1]
                new_state[7] = temp_state[1];   // U[1] -> R[3]
                new_state[14] = temp_state[7];  // R[3] -> D[2]
                new_state[15] = temp_state[5];  // R[1] -> D[3]
                new_state[16] = temp_state[14]; // D[2] -> L[0]
                new_state[18] = temp_state[15]; // D[3] -> L[2]
            }
            break;
        }

        // Wide moves (for 2x2x2, wide moves are equivalent to rotations)
        case 'r': {
            // Rw = x rotation (R + M' + x simplifies to just x for 2x2x2)
            if (direction == 1) {
                // x rotation (clockwise around R axis)
                new_state[0] = temp_state[8];   new_state[1] = temp_state[9];
                new_state[2] = temp_state[10];  new_state[3] = temp_state[11];
                new_state[4] = temp_state[6];   new_state[5] = temp_state[4];
                new_state[6] = temp_state[7];   new_state[7] = temp_state[5];
                new_state[8] = temp_state[12];  new_state[9] = temp_state[13];
                new_state[10] = temp_state[14]; new_state[11] = temp_state[15];
                new_state[12] = temp_state[23]; new_state[13] = temp_state[22];
                new_state[14] = temp_state[21]; new_state[15] = temp_state[20];
                new_state[16] = temp_state[17]; new_state[17] = temp_state[19];
                new_state[18] = temp_state[16]; new_state[19] = temp_state[18];
                new_state[20] = temp_state[3];  new_state[21] = temp_state[2];
                new_state[22] = temp_state[1];  new_state[23] = temp_state[0];
            } else if (direction == 2) {
                // x2 rotation
                new_state[0] = temp_state[12];  new_state[1] = temp_state[13];
                new_state[2] = temp_state[14];  new_state[3] = temp_state[15];
                new_state[4] = temp_state[7];   new_state[5] = temp_state[6];
                new_state[6] = temp_state[5];   new_state[7] = temp_state[4];
                new_state[8] = temp_state[23];  new_state[9] = temp_state[22];
                new_state[10] = temp_state[21]; new_state[11] = temp_state[20];
                new_state[12] = temp_state[0];  new_state[13] = temp_state[1];
                new_state[14] = temp_state[2];  new_state[15] = temp_state[3];
                new_state[16] = temp_state[19]; new_state[17] = temp_state[18];
                new_state[18] = temp_state[17]; new_state[19] = temp_state[16];
                new_state[20] = temp_state[11]; new_state[21] = temp_state[10];
                new_state[22] = temp_state[9];  new_state[23] = temp_state[8];
            } else {
                // x' rotation
                new_state[0] = temp_state[23];  new_state[1] = temp_state[22];
                new_state[2] = temp_state[21];  new_state[3] = temp_state[20];
                new_state[4] = temp_state[5];   new_state[5] = temp_state[7];
                new_state[6] = temp_state[4];   new_state[7] = temp_state[6];
                new_state[8] = temp_state[0];   new_state[9] = temp_state[1];
                new_state[10] = temp_state[2];  new_state[11] = temp_state[3];
                new_state[12] = temp_state[8];  new_state[13] = temp_state[9];
                new_state[14] = temp_state[10]; new_state[15] = temp_state[11];
                new_state[16] = temp_state[18]; new_state[17] = temp_state[16];
                new_state[18] = temp_state[19]; new_state[19] = temp_state[17];
                new_state[20] = temp_state[15]; new_state[21] = temp_state[14];
                new_state[22] = temp_state[13]; new_state[23] = temp_state[12];
            }
            break;
        }

        case 'l': {
            // Lw = x' rotation
            if (direction == 1) {
                // x' rotation
                new_state[0] = temp_state[23];  new_state[1] = temp_state[22];
                new_state[2] = temp_state[21];  new_state[3] = temp_state[20];
                new_state[4] = temp_state[5];   new_state[5] = temp_state[7];
                new_state[6] = temp_state[4];   new_state[7] = temp_state[6];
                new_state[8] = temp_state[0];   new_state[9] = temp_state[1];
                new_state[10] = temp_state[2];  new_state[11] = temp_state[3];
                new_state[12] = temp_state[8];  new_state[13] = temp_state[9];
                new_state[14] = temp_state[10]; new_state[15] = temp_state[11];
                new_state[16] = temp_state[18]; new_state[17] = temp_state[16];
                new_state[18] = temp_state[19]; new_state[19] = temp_state[17];
                new_state[20] = temp_state[15]; new_state[21] = temp_state[14];
                new_state[22] = temp_state[13]; new_state[23] = temp_state[12];
            } else if (direction == 2) {
                // x2 rotation
                new_state[0] = temp_state[12];  new_state[1] = temp_state[13];
                new_state[2] = temp_state[14];  new_state[3] = temp_state[15];
                new_state[4] = temp_state[7];   new_state[5] = temp_state[6];
                new_state[6] = temp_state[5];   new_state[7] = temp_state[4];
                new_state[8] = temp_state[23];  new_state[9] = temp_state[22];
                new_state[10] = temp_state[21]; new_state[11] = temp_state[20];
                new_state[12] = temp_state[0];  new_state[13] = temp_state[1];
                new_state[14] = temp_state[2];  new_state[15] = temp_state[3];
                new_state[16] = temp_state[19]; new_state[17] = temp_state[18];
                new_state[18] = temp_state[17]; new_state[19] = temp_state[16];
                new_state[20] = temp_state[11]; new_state[21] = temp_state[10];
                new_state[22] = temp_state[9];  new_state[23] = temp_state[8];
            } else {
                // x rotation
                new_state[0] = temp_state[8];   new_state[1] = temp_state[9];
                new_state[2] = temp_state[10];  new_state[3] = temp_state[11];
                new_state[4] = temp_state[6];   new_state[5] = temp_state[4];
                new_state[6] = temp_state[7];   new_state[7] = temp_state[5];
                new_state[8] = temp_state[12];  new_state[9] = temp_state[13];
                new_state[10] = temp_state[14]; new_state[11] = temp_state[15];
                new_state[12] = temp_state[23]; new_state[13] = temp_state[22];
                new_state[14] = temp_state[21]; new_state[15] = temp_state[20];
                new_state[16] = temp_state[17]; new_state[17] = temp_state[19];
                new_state[18] = temp_state[16]; new_state[19] = temp_state[18];
                new_state[20] = temp_state[3];  new_state[21] = temp_state[2];
                new_state[22] = temp_state[1];  new_state[23] = temp_state[0];
            }
            break;
        }

        case 'u': {
            // Uw = y rotation
            if (direction == 1) {
                // y rotation
                new_state[0] = temp_state[2];   new_state[1] = temp_state[0];
                new_state[2] = temp_state[3];   new_state[3] = temp_state[1];
                new_state[4] = temp_state[20];  new_state[5] = temp_state[21];
                new_state[6] = temp_state[22];  new_state[7] = temp_state[23];
                new_state[8] = temp_state[4];   new_state[9] = temp_state[5];
                new_state[10] = temp_state[6];  new_state[11] = temp_state[7];
                new_state[12] = temp_state[13]; new_state[13] = temp_state[15];
                new_state[14] = temp_state[12]; new_state[15] = temp_state[14];
                new_state[16] = temp_state[8];  new_state[17] = temp_state[9];
                new_state[18] = temp_state[10]; new_state[19] = temp_state[11];
                new_state[20] = temp_state[16]; new_state[21] = temp_state[17];
                new_state[22] = temp_state[18]; new_state[23] = temp_state[19];
            } else if (direction == 2) {
                // y2 rotation
                new_state[0] = temp_state[3];   new_state[1] = temp_state[2];
                new_state[2] = temp_state[1];   new_state[3] = temp_state[0];
                new_state[4] = temp_state[16];  new_state[5] = temp_state[17];
                new_state[6] = temp_state[18];  new_state[7] = temp_state[19];
                new_state[8] = temp_state[20];  new_state[9] = temp_state[21];
                new_state[10] = temp_state[22]; new_state[11] = temp_state[23];
                new_state[12] = temp_state[15]; new_state[13] = temp_state[14];
                new_state[14] = temp_state[13]; new_state[15] = temp_state[12];
                new_state[16] = temp_state[4];  new_state[17] = temp_state[5];
                new_state[18] = temp_state[6];  new_state[19] = temp_state[7];
                new_state[20] = temp_state[8];  new_state[21] = temp_state[9];
                new_state[22] = temp_state[10]; new_state[23] = temp_state[11];
            } else {
                // y' rotation
                new_state[0] = temp_state[1];   new_state[1] = temp_state[3];
                new_state[2] = temp_state[0];   new_state[3] = temp_state[2];
                new_state[4] = temp_state[8];   new_state[5] = temp_state[9];
                new_state[6] = temp_state[10];  new_state[7] = temp_state[11];
                new_state[8] = temp_state[16];  new_state[9] = temp_state[17];
                new_state[10] = temp_state[18]; new_state[11] = temp_state[19];
                new_state[12] = temp_state[14]; new_state[13] = temp_state[12];
                new_state[14] = temp_state[15]; new_state[15] = temp_state[13];
                new_state[16] = temp_state[20]; new_state[17] = temp_state[21];
                new_state[18] = temp_state[22]; new_state[19] = temp_state[23];
                new_state[20] = temp_state[4];  new_state[21] = temp_state[5];
                new_state[22] = temp_state[6];  new_state[23] = temp_state[7];
            }
            break;
        }

        case 'd': {
            // Dw = y' rotation
            if (direction == 1) {
                // y' rotation
                new_state[0] = temp_state[1];   new_state[1] = temp_state[3];
                new_state[2] = temp_state[0];   new_state[3] = temp_state[2];
                new_state[4] = temp_state[8];   new_state[5] = temp_state[9];
                new_state[6] = temp_state[10];  new_state[7] = temp_state[11];
                new_state[8] = temp_state[16];  new_state[9] = temp_state[17];
                new_state[10] = temp_state[18]; new_state[11] = temp_state[19];
                new_state[12] = temp_state[14]; new_state[13] = temp_state[12];
                new_state[14] = temp_state[15]; new_state[15] = temp_state[13];
                new_state[16] = temp_state[20]; new_state[17] = temp_state[21];
                new_state[18] = temp_state[22]; new_state[19] = temp_state[23];
                new_state[20] = temp_state[4];  new_state[21] = temp_state[5];
                new_state[22] = temp_state[6];  new_state[23] = temp_state[7];
            } else if (direction == 2) {
                // y2 rotation
                new_state[0] = temp_state[3];   new_state[1] = temp_state[2];
                new_state[2] = temp_state[1];   new_state[3] = temp_state[0];
                new_state[4] = temp_state[16];  new_state[5] = temp_state[17];
                new_state[6] = temp_state[18];  new_state[7] = temp_state[19];
                new_state[8] = temp_state[20];  new_state[9] = temp_state[21];
                new_state[10] = temp_state[22]; new_state[11] = temp_state[23];
                new_state[12] = temp_state[15]; new_state[13] = temp_state[14];
                new_state[14] = temp_state[13]; new_state[15] = temp_state[12];
                new_state[16] = temp_state[4];  new_state[17] = temp_state[5];
                new_state[18] = temp_state[6];  new_state[19] = temp_state[7];
                new_state[20] = temp_state[8];  new_state[21] = temp_state[9];
                new_state[22] = temp_state[10]; new_state[23] = temp_state[11];
            } else {
                // y rotation
                new_state[0] = temp_state[2];   new_state[1] = temp_state[0];
                new_state[2] = temp_state[3];   new_state[3] = temp_state[1];
                new_state[4] = temp_state[20];  new_state[5] = temp_state[21];
                new_state[6] = temp_state[22];  new_state[7] = temp_state[23];
                new_state[8] = temp_state[4];   new_state[9] = temp_state[5];
                new_state[10] = temp_state[6];  new_state[11] = temp_state[7];
                new_state[12] = temp_state[13]; new_state[13] = temp_state[15];
                new_state[14] = temp_state[12]; new_state[15] = temp_state[14];
                new_state[16] = temp_state[8];  new_state[17] = temp_state[9];
                new_state[18] = temp_state[10]; new_state[19] = temp_state[11];
                new_state[20] = temp_state[16]; new_state[21] = temp_state[17];
                new_state[22] = temp_state[18]; new_state[23] = temp_state[19];
            }
            break;
        }

        case 'f': {
            // Fw = z rotation
            if (direction == 1) {
                // z rotation
                new_state[0] = temp_state[18];  new_state[1] = temp_state[16];
                new_state[2] = temp_state[19];  new_state[3] = temp_state[17];
                new_state[4] = temp_state[2];   new_state[5] = temp_state[0];
                new_state[6] = temp_state[3];   new_state[7] = temp_state[1];
                new_state[8] = temp_state[10];  new_state[9] = temp_state[8];
                new_state[10] = temp_state[11]; new_state[11] = temp_state[9];
                new_state[12] = temp_state[6];  new_state[13] = temp_state[4];
                new_state[14] = temp_state[7];  new_state[15] = temp_state[5];
                new_state[16] = temp_state[14]; new_state[17] = temp_state[12];
                new_state[18] = temp_state[15]; new_state[19] = temp_state[13];
                new_state[20] = temp_state[21]; new_state[21] = temp_state[23];
                new_state[22] = temp_state[20]; new_state[23] = temp_state[22];
            } else if (direction == 2) {
                // z2 rotation
                new_state[0] = temp_state[15];  new_state[1] = temp_state[14];
                new_state[2] = temp_state[13];  new_state[3] = temp_state[12];
                new_state[4] = temp_state[19];  new_state[5] = temp_state[18];
                new_state[6] = temp_state[17];  new_state[7] = temp_state[16];
                new_state[8] = temp_state[11];  new_state[9] = temp_state[10];
                new_state[10] = temp_state[9];  new_state[11] = temp_state[8];
                new_state[12] = temp_state[3];  new_state[13] = temp_state[2];
                new_state[14] = temp_state[1];  new_state[15] = temp_state[0];
                new_state[16] = temp_state[7];  new_state[17] = temp_state[6];
                new_state[18] = temp_state[5];  new_state[19] = temp_state[4];
                new_state[20] = temp_state[23]; new_state[21] = temp_state[22];
                new_state[22] = temp_state[21]; new_state[23] = temp_state[20];
            } else {
                // z' rotation
                new_state[0] = temp_state[5];   new_state[1] = temp_state[7];
                new_state[2] = temp_state[4];   new_state[3] = temp_state[6];
                new_state[4] = temp_state[13];  new_state[5] = temp_state[15];
                new_state[6] = temp_state[12];  new_state[7] = temp_state[14];
                new_state[8] = temp_state[9];   new_state[9] = temp_state[11];
                new_state[10] = temp_state[8];  new_state[11] = temp_state[10];
                new_state[12] = temp_state[17]; new_state[13] = temp_state[19];
                new_state[14] = temp_state[16]; new_state[15] = temp_state[18];
                new_state[16] = temp_state[1];  new_state[17] = temp_state[3];
                new_state[18] = temp_state[0];  new_state[19] = temp_state[2];
                new_state[20] = temp_state[22]; new_state[21] = temp_state[20];
                new_state[22] = temp_state[23]; new_state[23] = temp_state[21];
            }
            break;
        }

        case 'b': {
            // Bw = z' rotation
            if (direction == 1) {
                // z' rotation
                new_state[0] = temp_state[5];   new_state[1] = temp_state[7];
                new_state[2] = temp_state[4];   new_state[3] = temp_state[6];
                new_state[4] = temp_state[13];  new_state[5] = temp_state[15];
                new_state[6] = temp_state[12];  new_state[7] = temp_state[14];
                new_state[8] = temp_state[9];   new_state[9] = temp_state[11];
                new_state[10] = temp_state[8];  new_state[11] = temp_state[10];
                new_state[12] = temp_state[17]; new_state[13] = temp_state[19];
                new_state[14] = temp_state[16]; new_state[15] = temp_state[18];
                new_state[16] = temp_state[1];  new_state[17] = temp_state[3];
                new_state[18] = temp_state[0];  new_state[19] = temp_state[2];
                new_state[20] = temp_state[22]; new_state[21] = temp_state[20];
                new_state[22] = temp_state[23]; new_state[23] = temp_state[21];
            } else if (direction == 2) {
                // z2 rotation
                new_state[0] = temp_state[15];  new_state[1] = temp_state[14];
                new_state[2] = temp_state[13];  new_state[3] = temp_state[12];
                new_state[4] = temp_state[19];  new_state[5] = temp_state[18];
                new_state[6] = temp_state[17];  new_state[7] = temp_state[16];
                new_state[8] = temp_state[11];  new_state[9] = temp_state[10];
                new_state[10] = temp_state[9];  new_state[11] = temp_state[8];
                new_state[12] = temp_state[3];  new_state[13] = temp_state[2];
                new_state[14] = temp_state[1];  new_state[15] = temp_state[0];
                new_state[16] = temp_state[7];  new_state[17] = temp_state[6];
                new_state[18] = temp_state[5];  new_state[19] = temp_state[4];
                new_state[20] = temp_state[23]; new_state[21] = temp_state[22];
                new_state[22] = temp_state[21]; new_state[23] = temp_state[20];
            } else {
                // z rotation
                new_state[0] = temp_state[18];  new_state[1] = temp_state[16];
                new_state[2] = temp_state[19];  new_state[3] = temp_state[17];
                new_state[4] = temp_state[2];   new_state[5] = temp_state[0];
                new_state[6] = temp_state[3];   new_state[7] = temp_state[1];
                new_state[8] = temp_state[10];  new_state[9] = temp_state[8];
                new_state[10] = temp_state[11]; new_state[11] = temp_state[9];
                new_state[12] = temp_state[6];  new_state[13] = temp_state[4];
                new_state[14] = temp_state[7];  new_state[15] = temp_state[5];
                new_state[16] = temp_state[14]; new_state[17] = temp_state[12];
                new_state[18] = temp_state[15]; new_state[19] = temp_state[13];
                new_state[20] = temp_state[21]; new_state[21] = temp_state[23];
                new_state[22] = temp_state[20]; new_state[23] = temp_state[22];
            }
            break;
        }

        // Cube rotations (x, y, z)
        case 'x': {
            if (direction == 1) {
                // x rotation
                new_state[0] = temp_state[8];   new_state[1] = temp_state[9];
                new_state[2] = temp_state[10];  new_state[3] = temp_state[11];
                new_state[4] = temp_state[6];   new_state[5] = temp_state[4];
                new_state[6] = temp_state[7];   new_state[7] = temp_state[5];
                new_state[8] = temp_state[12];  new_state[9] = temp_state[13];
                new_state[10] = temp_state[14]; new_state[11] = temp_state[15];
                new_state[12] = temp_state[23]; new_state[13] = temp_state[22];
                new_state[14] = temp_state[21]; new_state[15] = temp_state[20];
                new_state[16] = temp_state[17]; new_state[17] = temp_state[19];
                new_state[18] = temp_state[16]; new_state[19] = temp_state[18];
                new_state[20] = temp_state[3];  new_state[21] = temp_state[2];
                new_state[22] = temp_state[1];  new_state[23] = temp_state[0];
            } else if (direction == 2) {
                // x2 rotation
                new_state[0] = temp_state[12];  new_state[1] = temp_state[13];
                new_state[2] = temp_state[14];  new_state[3] = temp_state[15];
                new_state[4] = temp_state[7];   new_state[5] = temp_state[6];
                new_state[6] = temp_state[5];   new_state[7] = temp_state[4];
                new_state[8] = temp_state[23];  new_state[9] = temp_state[22];
                new_state[10] = temp_state[21]; new_state[11] = temp_state[20];
                new_state[12] = temp_state[0];  new_state[13] = temp_state[1];
                new_state[14] = temp_state[2];  new_state[15] = temp_state[3];
                new_state[16] = temp_state[19]; new_state[17] = temp_state[18];
                new_state[18] = temp_state[17]; new_state[19] = temp_state[16];
                new_state[20] = temp_state[11]; new_state[21] = temp_state[10];
                new_state[22] = temp_state[9];  new_state[23] = temp_state[8];
            } else {
                // x' rotation
                new_state[0] = temp_state[23];  new_state[1] = temp_state[22];
                new_state[2] = temp_state[21];  new_state[3] = temp_state[20];
                new_state[4] = temp_state[5];   new_state[5] = temp_state[7];
                new_state[6] = temp_state[4];   new_state[7] = temp_state[6];
                new_state[8] = temp_state[0];   new_state[9] = temp_state[1];
                new_state[10] = temp_state[2];  new_state[11] = temp_state[3];
                new_state[12] = temp_state[8];  new_state[13] = temp_state[9];
                new_state[14] = temp_state[10]; new_state[15] = temp_state[11];
                new_state[16] = temp_state[18]; new_state[17] = temp_state[16];
                new_state[18] = temp_state[19]; new_state[19] = temp_state[17];
                new_state[20] = temp_state[15]; new_state[21] = temp_state[14];
                new_state[22] = temp_state[13]; new_state[23] = temp_state[12];
            }
            break;
        }

        case 'y': {
            if (direction == 1) {
                // y rotation
                new_state[0] = temp_state[2];   new_state[1] = temp_state[0];
                new_state[2] = temp_state[3];   new_state[3] = temp_state[1];
                new_state[4] = temp_state[20];  new_state[5] = temp_state[21];
                new_state[6] = temp_state[22];  new_state[7] = temp_state[23];
                new_state[8] = temp_state[4];   new_state[9] = temp_state[5];
                new_state[10] = temp_state[6];  new_state[11] = temp_state[7];
                new_state[12] = temp_state[13]; new_state[13] = temp_state[15];
                new_state[14] = temp_state[12]; new_state[15] = temp_state[14];
                new_state[16] = temp_state[8];  new_state[17] = temp_state[9];
                new_state[18] = temp_state[10]; new_state[19] = temp_state[11];
                new_state[20] = temp_state[16]; new_state[21] = temp_state[17];
                new_state[22] = temp_state[18]; new_state[23] = temp_state[19];
            } else if (direction == 2) {
                // y2 rotation
                new_state[0] = temp_state[3];   new_state[1] = temp_state[2];
                new_state[2] = temp_state[1];   new_state[3] = temp_state[0];
                new_state[4] = temp_state[16];  new_state[5] = temp_state[17];
                new_state[6] = temp_state[18];  new_state[7] = temp_state[19];
                new_state[8] = temp_state[20];  new_state[9] = temp_state[21];
                new_state[10] = temp_state[22]; new_state[11] = temp_state[23];
                new_state[12] = temp_state[15]; new_state[13] = temp_state[14];
                new_state[14] = temp_state[13]; new_state[15] = temp_state[12];
                new_state[16] = temp_state[4];  new_state[17] = temp_state[5];
                new_state[18] = temp_state[6];  new_state[19] = temp_state[7];
                new_state[20] = temp_state[8];  new_state[21] = temp_state[9];
                new_state[22] = temp_state[10]; new_state[23] = temp_state[11];
            } else {
                // y' rotation
                new_state[0] = temp_state[1];   new_state[1] = temp_state[3];
                new_state[2] = temp_state[0];   new_state[3] = temp_state[2];
                new_state[4] = temp_state[8];   new_state[5] = temp_state[9];
                new_state[6] = temp_state[10];  new_state[7] = temp_state[11];
                new_state[8] = temp_state[16];  new_state[9] = temp_state[17];
                new_state[10] = temp_state[18]; new_state[11] = temp_state[19];
                new_state[12] = temp_state[14]; new_state[13] = temp_state[12];
                new_state[14] = temp_state[15]; new_state[15] = temp_state[13];
                new_state[16] = temp_state[20]; new_state[17] = temp_state[21];
                new_state[18] = temp_state[22]; new_state[19] = temp_state[23];
                new_state[20] = temp_state[4];  new_state[21] = temp_state[5];
                new_state[22] = temp_state[6];  new_state[23] = temp_state[7];
            }
            break;
        }

        case 'z': {
            if (direction == 1) {
                // z rotation
                new_state[0] = temp_state[18];  new_state[1] = temp_state[16];
                new_state[2] = temp_state[19];  new_state[3] = temp_state[17];
                new_state[4] = temp_state[2];   new_state[5] = temp_state[0];
                new_state[6] = temp_state[3];   new_state[7] = temp_state[1];
                new_state[8] = temp_state[10];  new_state[9] = temp_state[8];
                new_state[10] = temp_state[11]; new_state[11] = temp_state[9];
                new_state[12] = temp_state[6];  new_state[13] = temp_state[4];
                new_state[14] = temp_state[7];  new_state[15] = temp_state[5];
                new_state[16] = temp_state[14]; new_state[17] = temp_state[12];
                new_state[18] = temp_state[15]; new_state[19] = temp_state[13];
                new_state[20] = temp_state[21]; new_state[21] = temp_state[23];
                new_state[22] = temp_state[20]; new_state[23] = temp_state[22];
            } else if (direction == 2) {
                // z2 rotation
                new_state[0] = temp_state[15];  new_state[1] = temp_state[14];
                new_state[2] = temp_state[13];  new_state[3] = temp_state[12];
                new_state[4] = temp_state[19];  new_state[5] = temp_state[18];
                new_state[6] = temp_state[17];  new_state[7] = temp_state[16];
                new_state[8] = temp_state[11];  new_state[9] = temp_state[10];
                new_state[10] = temp_state[9];  new_state[11] = temp_state[8];
                new_state[12] = temp_state[3];  new_state[13] = temp_state[2];
                new_state[14] = temp_state[1];  new_state[15] = temp_state[0];
                new_state[16] = temp_state[7];  new_state[17] = temp_state[6];
                new_state[18] = temp_state[5];  new_state[19] = temp_state[4];
                new_state[20] = temp_state[23]; new_state[21] = temp_state[22];
                new_state[22] = temp_state[21]; new_state[23] = temp_state[20];
            } else {
                // z' rotation
                new_state[0] = temp_state[5];   new_state[1] = temp_state[7];
                new_state[2] = temp_state[4];   new_state[3] = temp_state[6];
                new_state[4] = temp_state[13];  new_state[5] = temp_state[15];
                new_state[6] = temp_state[12];  new_state[7] = temp_state[14];
                new_state[8] = temp_state[9];   new_state[9] = temp_state[11];
                new_state[10] = temp_state[8];  new_state[11] = temp_state[10];
                new_state[12] = temp_state[17]; new_state[13] = temp_state[19];
                new_state[14] = temp_state[16]; new_state[15] = temp_state[18];
                new_state[16] = temp_state[1];  new_state[17] = temp_state[3];
                new_state[18] = temp_state[0];  new_state[19] = temp_state[2];
                new_state[20] = temp_state[22]; new_state[21] = temp_state[20];
                new_state[22] = temp_state[23]; new_state[23] = temp_state[21];
            }
            break;
        }

        // Slice moves are not allowed on 2x2x2
        case 'M':
            PyErr_SetString(PyExc_ValueError,
                "M moves are only allowed on odd-sized cubes. "
                "The current cube is a 2x2x2.");
            return NULL;

        case 'E':
            PyErr_SetString(PyExc_ValueError,
                "E moves are only allowed on odd-sized cubes. "
                "The current cube is a 2x2x2.");
            return NULL;

        case 'S':
            PyErr_SetString(PyExc_ValueError,
                "S moves are only allowed on odd-sized cubes. "
                "The current cube is a 2x2x2.");
            return NULL;

        default:
            PyErr_Format(PyExc_ValueError, "Invalid move face: '%c'", face);
            return NULL;
    }

    return PyUnicode_FromString(new_state);
}

// Module method definitions
static PyMethodDef RotateMethods[] = {
    {"rotate_move", rotate_move, METH_VARARGS, "Rotate 2x2x2 cube state with given move"},
    {NULL, NULL, 0, NULL}
};

// Module definition
static struct PyModuleDef rotatemodule = {
    PyModuleDef_HEAD_INIT,
    "rotate_2x2x2",
    "Fast 2x2x2 cube rotation operations",
    -1,
    RotateMethods
};

// Module initialization function
PyMODINIT_FUNC PyInit_rotate_2x2x2(void) {
    return PyModule_Create(&rotatemodule);
}
